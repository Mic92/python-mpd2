"""Asynchronous access to MPD using the asyncio methods of Python 3.

Interaction happens over the mpd.asyncio.MPDClient class, whose connect and
command methods are coroutines.

Some commands (eg. listall) additionally support the asynchronous iteration
(aiter, `async for`) interface; using it allows the library user to obtain
items of result as soon as they arrive.

The .idle() method works differently here: It is an asynchronous iterator that
produces a list of changed subsystems whenever a new one is available. The
MPDClient object automatically switches in and out of idle mode depending on
which subsystems there is currently interest in.

Command lists are currently not supported.


This module requires Python 3.5.2 or later to run.
"""

import asyncio
from functools import partial

from mpd.base import HELLO_PREFIX, ERROR_PREFIX, SUCCESS
from mpd.base import MPDClientBase
from mpd.base import MPDClient as SyncMPDClient
from mpd.base import ProtocolError, ConnectionError, CommandError
from mpd.base import mpd_command_provider

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

    __iter__ = __await__ # for 'yield from' style invocation

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

    #: When in idle, this is a Future on which incoming commands should set a
    #: result. (This works around asyncio.Queue not having a .peek() coroutine)
    __command_enqueued = None

    #: Seconds after a command's completion to send idle. Setting this too high
    # causes "blind spots" in the client's view of the server, setting it too
    # low sends needless idle/noidle after commands in quick succession.
    IMMEDIATE_COMMAND_TIMEOUT = 0.1

    async def connect(self, host, port=6600, loop=None):
        self.__loop = loop

        if '/' in host:
            r, w = await asyncio.open_unix_connection(host, loop=loop)
        else:
            r, w = await asyncio.open_connection(host, port, loop=loop)
        self.__rfile, self.__wfile = r, w

        self.__commandqueue = asyncio.Queue(loop=loop)
        self.__idle_results = asyncio.Queue(loop=loop) #: a queue of CommandResult("idle") futures
        self.__idle_consumers = [] #: list of (subsystem-list, callbacks) tuples

        try:
            helloline = await asyncio.wait_for(self.__readline(), timeout=5)
        except asyncio.TimeoutError:
            self.disconnect()
            raise ConnectionError("No response from server while reading MPD hello")
        # FIXME should be reusable w/o reaching in
        SyncMPDClient._hello(self, helloline)

        self.__run_task = asyncio.Task(self.__run())
        self.__idle_task = asyncio.Task(self.__distribute_idle_results())

    def disconnect(self):
        if self.__run_task is not None: # is None eg. when connection fails in .connect()
            self.__run_task.cancel()
        if self.__idle_task is not None:
            self.__idle_task.cancel()
        self.__wfile.close()
        self.__rfile = self.__wfile = None
        self.__run_task = self.__idle_task = None
        self.__commandqueue = self.__command_enqueued = None
        self.__idle_results = self.__idle_consumers = None

    def _get_idle_interests(self):
        """Accumulate a set of interests from the current __idle_consumers.
        Returns the union of their subscribed subjects, [] if at least one of
        them is the empty catch-all set, or None if there are no interests at
        all."""

        if not self.__idle_consumers:
            return None
        if any(len(s) == 0 for (s, c) in self.__idle_consumers):
            return []
        return set.union(*(set(s) for (s, c) in self.__idle_consumers))

    def _nudge_idle(self):
        """If the main task is currently idling, make it leave idle and process
        the next command (if one is present) or just restart idle"""

        if self.__command_enqueued is not None and not self.__command_enqueued.done():
            self.__command_enqueued.set_result(None)

    async def __run(self):
        result = None

        try:
            while True:
                try:
                    result = await asyncio.wait_for(
                            self.__commandqueue.get(),
                            timeout=self.IMMEDIATE_COMMAND_TIMEOUT,
                            loop=self.__loop,
                            )
                except asyncio.TimeoutError:
                    # The cancellation of the __commandqueue.get() that happens
                    # in this case is intended, and is just what asyncio.Queue
                    # suggests for "get with timeout".

                    subsystems = self._get_idle_interests()
                    if subsystems is None:
                        # The presumably most quiet subsystem -- in this case,
                        # idle is only used to keep the connection alive.
                        subsystems = ["database"]

                    result = CommandResult("idle", subsystems, self._parse_list)
                    self.__idle_results.put_nowait(result)

                    self.__command_enqueued = asyncio.Future()

                self._write_command(result._command, result._args)
                while True:
                    try:
                        if self.__command_enqueued is not None:
                            # We're in idle mode.
                            line_future = asyncio.shield(self.__read_output_line())
                            await asyncio.wait([line_future, self.__command_enqueued],
                                    return_when=asyncio.FIRST_COMPLETED)
                            if self.__command_enqueued.done():
                                self._write_command("noidle")
                                self.__command_enqueued = None
                            l = await line_future
                        else:
                            l = await self.__read_output_line()
                    except CommandError as e:
                        result._feed_error(e)
                        break
                    result._feed_line(l)
                    if l is None:
                        break

                result = None

        except Exception as e:
            # Prevent the destruction of the pending task in the shutdown
            # function -- it's just shutting down by itself.
            self.__run_task = None
            self.disconnect()

            if result is not None:
                result._feed_error(e)
                return
            else:
                # Typically this is a bug in mpd.asyncio.
                raise

    async def __distribute_idle_results(self):
        # An exception flying out of here probably means a connection
        # interruption during idle. This will just show like any other
        # unhandled task exception and that's probably the best we can do.
        while True:
            result = await self.__idle_results.get()
            idle_changes = list(await result)
            if not idle_changes:
                continue
            for subsystems, callback in self.__idle_consumers:
                if not subsystems or any(s in subsystems for s in idle_changes):
                    callback(idle_changes)

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

    # This is just a wrapper for the below.
    def _write_line(self, text):
        self.__write(text + "\n")
    # FIXME This code should be shareable.
    _write_command = SyncMPDClient._write_command


    async def __read_output_line(self):
        """Kind of like SyncMPDClient._read_line"""
        line = await self.__readline()
        if not line.endswith("\n"):
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError(error)
        if line == SUCCESS:
            return None
        return line


#    async def _parse_objects_direct(self, lines, delimiters=[], lookup_delimiter=False):
#        obj = {}
#        while True:
#            line = await lines.get()
#            if isinstance(line, BaseException):
#                raise line
#            if line is None:
#                break
#            key, value = self._parse_pair(line, separator=": ")
#            key = key.lower()
#            if lookup_delimiter and not delimiters:
#                delimiters = [key]
#            if obj:
#                if key in delimiters:
#                    yield obj
#                    obj = {}
#                elif key in obj:
#                    if not isinstance(obj[key], list):
#                        obj[key] = [obj[key], value]
#                    else:
#                        obj[key].append(value)
#                    continue
#            obj[key] = value
#        if obj:
#            yield obj

    def _parse_objects_direct(self, lines, delimiters=[], lookup_delimiter=False):
        # This is a workaround implementing the above comment on Python 3.5. It
        # is recommended that the commented-out code be used for reasoning, and
        # that changes are applied there and only copied over to this
        # implementation.

        outerself = self
        class WrappedLoop:
            def __init__(self):
                self.obj = {}
                self.exhausted = False

            def __aiter__(self):
                return self

            async def __anext__(self):
                while True:
                    if self.exhausted:
                        raise StopAsyncIteration()

                    line = await lines.get()
                    if isinstance(line, BaseException):
                        raise line
                    if line is None:
                        self.exhausted = True
                        if self.obj:
                            return self.obj
                        continue
                    key, value = outerself._parse_pair(line, separator=": ")
                    key = key.lower()
                    if lookup_delimiter and not delimiters:
                        delimiters = [key]
                    if self.obj:
                        if key in delimiters:
                            oldobj = self.obj
                            self.obj = {key: value}
                            return oldobj
                        elif key in self.obj:
                            if not isinstance(self.obj[key], list):
                                self.obj[key] = [self.obj[key], value]
                            else:
                                self.obj[key].append(value)
                            continue
                    self.obj[key] = value
        return WrappedLoop()

    # command provider interface

    @classmethod
    def add_command(cls, name, callback):
        command_class = CommandResultIterable if callback.mpd_commands_direct else CommandResult
        if hasattr(cls, name):
            # Idle and noidle are explicitly implemented, skipping them.
            return
        def f(self, *args):
            result = command_class(name, args, partial(callback, self))
            if self.__run_task is None:
                raise ConnectionError("Can not send command to disconnected client")
            self.__commandqueue.put_nowait(result)
            self._nudge_idle()
            return result
        escaped_name = name.replace(" ", "_")
        f.__name__ = escaped_name
        setattr(cls, escaped_name, f)

    # commands that just work differently

#    async def idle(self, subsystems=()):
#        interests_before = self._get_idle_interests()
#        changes = asyncio.Queue()
#        try:
#            entry = (subsystems, changes.put_nowait)
#            self.__idle_consumers.append(entry)
#            if self._get_idle_interests != interests_before:
#                self._nudge_idle()
#            while True:
#                yield await changes.get()
#        finally:
#            self.__idle_consumers.remove(entry)

    def idle(self, subsystems=()):
        # This is a desugared workaround for python 3.5.
        # Please consider the above block authoritative and this a workaround,
        # and only apply changes here once they're incorporated there.

        def final():
            self.__idle_consumers.remove(entry)

        class IdleAIter:
            def __aiter__(self):
                return self

            def __anext__(self):
                return changes.get()

            def __del__(self):
                final()

        interests_before = self._get_idle_interests()
        changes = asyncio.Queue()

        entry = (subsystems, changes.put_nowait)
        self.__idle_consumers.append(entry)
        if self._get_idle_interests != interests_before:
            self._nudge_idle()

        return IdleAIter()

    def noidle(self):
        raise AttributeError("noidle is not supported / required in mpd.asyncio")
