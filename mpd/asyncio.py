import asyncio
from functools import partial

from mpd.base import HELLO_PREFIX, ERROR_PREFIX, SUCCESS
from mpd.base import MPDClientBase
from mpd.base import MPDClient as SyncMPDClient
from mpd.base import ProtocolError, ConnectionError, CommandError
from mpd.base import mpd_command_provider

class CommandResult(asyncio.Future):
    """A future that carries its command/args/callback with it for the
    convenience of passing it around to the command queue."""

    def __init__(self, command, args, callback):
        super().__init__()
        self._command = command
        self._args = args
        self.__callback = callback
        self.__spooled_lines = []

    def _feed_line(self, line):
        """Put the given line into the callback machinery, and set the result on a None line."""
        if line is None:
            self.set_result(self.__callback(self.__spooled_lines))
        else:
            self.__spooled_lines.append(line)

    async def __aiter__(self):
        raise NotImplementedError("async for x in clientcommand() is work in progress")

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
            try:
                responselines = await self.__read_full_output()
                for l in responselines:
                    result._feed_line(l)
            except Exception as e:
                # may be CommandError flying out of __read_fulloutput or any kind of exception from the callback
                result.set_exception(e)
            finally:
                assert result.done(), "Result %s not done after __read_full_output was processed"%(result,)

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

    # copied stuff from base

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

    async def __read_full_output(self):
        """Kind of like SyncMPDClient._read_lines, but without the iteration"""
        result = []
        while True:
            line = await self.__read_output_line()
            result.append(line)
            if line is None:
                return result

    # command provider interface

    @classmethod
    def add_command(cls, name, callback):
        if hasattr(cls, name):
            # twisted silently ignores them; probably, i'll make an
            # experience that'll make me take the same router at some point.
            raise AttributeError("Refusing to override the %s command"%name)
        def f(self, *args):
            result = CommandResult(name, args, partial(callback, self))
            self.__commandqueue.put_nowait(result)
            return result
        escaped_name = name.replace(" ", "_")
        f.__name__ = escaped_name
        setattr(cls, escaped_name, f)
