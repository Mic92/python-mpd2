import asyncio
from functools import partial

from mpd.base import HELLO_PREFIX, ERROR_PREFIX, SUCCESS
from mpd.base import MPDClientBase
from mpd.base import MPDClient as SyncMPDClient
from mpd.base import ProtocolError, ConnectionError, CommandError
from mpd.base import mpd_command_provider, mpd_commands

class BaseCommandResult(asyncio.Future):
    """A future that carries its command/args/callback with it for the
    convenience of passing it around to the command queue."""

    def __init__(self, command, args, callback):
        super().__init__()
        self._command = command
        self._args = args
        self._callback = callback

class CommandResult(BaseCommandResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__spooled_lines = []

    def _feed_line(self, line):
        """Put the given line into the callback machinery, and set the result on a None line."""
        if line is None:
            self.set_result(self._callback(self.__spooled_lines))
        else:
            self.__spooled_lines.append(line)

    def _feed_error(self, error):
        self.set_exception(error)

class CommandResultIterable(BaseCommandResult):
    """Variant of CommandResult where the underlying callback is an
    asynchronous` generator, and can thus interpret lines as they come along.

    The result can be used with the aiter interface (`async for`). If it is
    still used as a future instead, it eventually results in a list.

    Commands used with this CommandResult must use their passed lines not like
    an iterable (as in the synchronous implementation), but as a asyncio.Queue.
    Furthermore, they must check whether the queue elements are exceptions, and
    raise them.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__spooled_lines = asyncio.Queue()

    def _feed_line(self, line):
        self.__spooled_lines.put_nowait(line)

    _feed_error = _feed_line

    def __await__(self):
        asyncio.Task(self.__feed_future())
        return super().__await__()

    async def __feed_future(self):
        result = []
        async for r in self:
            result.append(r)
        self.set_result(result)

    def __aiter__(self):
        if self.done():
            raise RuntimeError("Command result is already being consumed")
        return self._callback(self.__spooled_lines).__aiter__()


@mpd_command_provider
class MPDClient(MPDClientBase):
    __run_task = None # doubles as indicator for being connected

    async def connect(self, host, port=6600, loop=None):
        self.__loop = loop

        if '/' in host:
            r, w = await asyncio.open_unic_connection(path, loop=loop)
        else:
            r, w = await asyncio.open_connection(host, port, loop=loop)
        self.__rfile, self.__wfile = r, w

        self.__commandqueue = asyncio.Queue(loop=loop)

        await self.__hello()

        self.__run_task = asyncio.Task(self.__run())

    def disconnect(self):
        self.__run_task.cancel()
        self.__rfile = self.__wfile = None
        self.__run_task = self.__commandqueue = None

    async def __run(self):
        while True:
            result = await self.__commandqueue.get()
            self._write_command(result._command, result._args)
            while True:
                try:
                    l = await self.__read_output_line()
                except CommandError as e:
                    result._feed_error(e)
                    break
                result._feed_line(l)
                if l is None:
                    break

    # helper methods

    async def __readline(self):
        """Wrapper around .__rfile.readline that handles encoding"""
        data = await self.__rfile.readline()
        try:
            return data.decode('utf8')
        except UnicodeDecodeError:
            self.disconnect()
            raise ProtocolError("Invalid UTF8 received")

    def __write(self, text):
        """Wrapper around .__wfile.write that handles encoding."""
        self.__wfile.write(text.encode('utf8'))

    # copied and subtly modifiedstuff from base

    async def __hello(self):
        # not catching the timeout error, it's actually pretty adaequate
        try:
            line = await asyncio.wait_for(self.__readline(), timeout=5)
        except asyncio.TimeoutError:
            self.disconnect()
            raise ConnectionError("No response from server while reading MPD hello")

        # FIXME this is copied from base.MPDClient._hello
        if not line.endswith("\n"):
            self.disconnect()
            raise ConnectionError("Connection lost while reading MPD hello")
        line = line.rstrip("\n")
        if not line.startswith(HELLO_PREFIX):
            raise ProtocolError("Got invalid MPD hello: '{}'".format(line))
        self.mpd_version = line[len(HELLO_PREFIX):].strip()

    # this is just a wrapper for the below
    def _write_line(self, text):
        self.__write(text + "\n")
    # FIXME this code should be sharable
    _write_command = SyncMPDClient._write_command


    async def __read_output_line(self):
        """Kind of like SyncMPDClient._read_line"""
        line = await self.__readline()
        if not line.endswith("\n"):
            self.disconnect()
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError(error)
        if line == SUCCESS:
            return None
        return line

    async def _parse_objects(self, lines, delimiters=[]):
        """Like _parse_objects, but waits for lines"""
        obj = {}
        while True:
            line = await lines.get()
            if isinstance(line, BaseException):
                raise line
            if line is None:
                break
            key, value = self._parse_pair(line, separator=": ")
            key = key.lower()
            if obj:
                if key in delimiters:
                    yield obj
                    obj = {}
                elif key in obj:
                    if not isinstance(obj[key], list):
                        obj[key] = [obj[key], value]
                    else:
                        obj[key].append(value)
                    continue
            obj[key] = value
        if obj:
            yield obj

    # as the above works for everyone who calls `return _parse_objects` but
    # *not* for those that return list(_parse_objects(...))[0], that single
    # function is rewritten here to use the original _parse_objects

    @mpd_commands('count', 'currentsong', 'readcomments', 'stats', 'status')
    def _parse_object(self, lines):
        objs = list(SyncMPDClient._parse_objects(self, lines))
        if not objs:
            return {}
        return objs[0]

    # command provider interface

    __wrap_async_iterator_parsers = [
            # the very ones that return _parse_object directly
            SyncMPDClient._parse_changes,
            SyncMPDClient._parse_database,
            SyncMPDClient._parse_messages,
            SyncMPDClient._parse_mounts,
            SyncMPDClient._parse_neighbors,
            SyncMPDClient._parse_outputs,
            SyncMPDClient._parse_playlists,
            SyncMPDClient._parse_plugins,
            SyncMPDClient._parse_songs,
            ]

    @classmethod
    def add_command(cls, name, callback):
        wrap_result = callback in cls.__wrap_async_iterator_parsers
        command_class = CommandResultIterable if wrap_result else CommandResult
        if hasattr(cls, name):
            # twisted silently ignores them; probably, i'll make an
            # experience that'll make me take the same router at some point.
            raise AttributeError("Refusing to override the %s command"%name)
        def f(self, *args):
            result = command_class(name, args, partial(callback, self))
            self.__commandqueue.put_nowait(result)
            return result
        escaped_name = name.replace(" ", "_")
        f.__name__ = escaped_name
        setattr(cls, escaped_name, f)
