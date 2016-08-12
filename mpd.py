# python-mpd2: Python MPD client library
#
# Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
# Copyright (C) 2012  J. Thalheim <jthalheim@gmail.com>
#
# python-mpd2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-mpd2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python-mpd2.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sys
import socket
import warnings
from collections import Callable

VERSION = (0, 6, 0)
HELLO_PREFIX = "OK MPD "
ERROR_PREFIX = "ACK "
SUCCESS = "OK"
NEXT = "list_OK"

IS_PYTHON2 = sys.version_info < (3, 0)
if IS_PYTHON2:
    def decode_str(s):
        return s.decode("utf-8")

    def encode_str(s):
        if type(s) == str:
            return s
        else:
            return (unicode(s)).encode("utf-8")
else:

    def decode_str(s):
        return s
    encode_str = str

try:
    from logging import NullHandler
except ImportError:  # NullHandler was introduced in python2.7
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


class MPDError(Exception):
    pass


class ConnectionError(MPDError):
    pass


class ProtocolError(MPDError):
    pass


class CommandError(MPDError):
    pass


class CommandListError(MPDError):
    pass


class PendingCommandError(MPDError):
    pass


class IteratingError(MPDError):
    pass


class _NotConnected(object):
    def __getattr__(self, attr):
        return self._dummy

    def _dummy(*args):
        raise ConnectionError("Not connected")


_commands = {
    # Status Commands
    "clearerror":         "_fetch_nothing",
    "currentsong":        "_fetch_object",
    "idle":               "_fetch_idle",
    "status":             "_fetch_object",
    "stats":              "_fetch_object",
    # Playback Option Commands
    "consume":            "_fetch_nothing",
    "crossfade":          "_fetch_nothing",
    "mixrampdb":          "_fetch_nothing",
    "mixrampdelay":       "_fetch_nothing",
    "random":             "_fetch_nothing",
    "repeat":             "_fetch_nothing",
    "setvol":             "_fetch_nothing",
    "single":             "_fetch_nothing",
    "replay_gain_mode":   "_fetch_nothing",
    "replay_gain_status": "_fetch_item",
    # Playback Control Commands
    "next":               "_fetch_nothing",
    "pause":              "_fetch_nothing",
    "play":               "_fetch_nothing",
    "playid":             "_fetch_nothing",
    "previous":           "_fetch_nothing",
    "seek":               "_fetch_nothing",
    "seekid":             "_fetch_nothing",
    "seekcur":            "_fetch_nothing",
    "stop":               "_fetch_nothing",
    # Playlist Commands
    "add":                "_fetch_nothing",
    "addid":              "_fetch_item",
    "addtagid":           "_fetch_nothing",
    "cleartagid":         "_fetch_nothing",
    "clear":              "_fetch_nothing",
    "delete":             "_fetch_nothing",
    "deleteid":           "_fetch_nothing",
    "move":               "_fetch_nothing",
    "moveid":             "_fetch_nothing",
    "playlist":           "_fetch_playlist",
    "playlistfind":       "_fetch_songs",
    "playlistid":         "_fetch_songs",
    "playlistinfo":       "_fetch_songs",
    "playlistsearch":     "_fetch_songs",
    "plchanges":          "_fetch_songs",
    "plchangesposid":     "_fetch_changes",
    "prio":               "_fetch_nothing",
    "prioid":             "_fetch_nothing",
    "rangeid":            "_fetch_nothing",
    "shuffle":            "_fetch_nothing",
    "swap":               "_fetch_nothing",
    "swapid":             "_fetch_nothing",
    # Stored Playlist Commands
    "listplaylist":       "_fetch_list",
    "listplaylistinfo":   "_fetch_songs",
    "listplaylists":      "_fetch_playlists",
    "load":               "_fetch_nothing",
    "playlistadd":        "_fetch_nothing",
    "playlistclear":      "_fetch_nothing",
    "playlistdelete":     "_fetch_nothing",
    "playlistmove":       "_fetch_nothing",
    "rename":             "_fetch_nothing",
    "rm":                 "_fetch_nothing",
    "save":               "_fetch_nothing",
    # Database Commands
    "count":              "_fetch_object",
    "find":               "_fetch_songs",
    "findadd":            "_fetch_nothing",
    "list":               "_fetch_list",
    "listall":            "_fetch_database",
    "listallinfo":        "_fetch_database",
    "listfiles":          "_fetch_database",
    "lsinfo":             "_fetch_database",
    "readcomments":       "_fetch_object",
    "search":             "_fetch_songs",
    "searchadd":          "_fetch_nothing",
    "searchaddpl":        "_fetch_nothing",
    "update":             "_fetch_item",
    "rescan":             "_fetch_item",
    # Mounts and neighbors
    "mount":              "_fetch_nothing",
    "umount":             "_fetch_nothing",
    "listmounts":         "_fetch_mounts",
    "listneighbors":      "_fetch_neighbors",
    # Sticker Commands
    "sticker get":        "_fetch_sticker",
    "sticker set":        "_fetch_nothing",
    "sticker delete":     "_fetch_nothing",
    "sticker list":       "_fetch_stickers",
    "sticker find":       "_fetch_songs",
    # Connection Commands
    "close":              None,
    "kill":               None,
    "password":           "_fetch_nothing",
    "ping":               "_fetch_nothing",
    # Audio Output Commands
    "disableoutput":      "_fetch_nothing",
    "enableoutput":       "_fetch_nothing",
    "toggleoutput":       "_fetch_nothing",
    "outputs":            "_fetch_outputs",
    # Reflection Commands
    "config":             "_fetch_item",
    "commands":           "_fetch_list",
    "notcommands":        "_fetch_list",
    "tagtypes":           "_fetch_list",
    "urlhandlers":        "_fetch_list",
    "decoders":           "_fetch_plugins",
    # Client To Client
    "subscribe":          "_fetch_nothing",
    "unsubscribe":        "_fetch_nothing",
    "channels":           "_fetch_list",
    "readmessages":       "_fetch_messages",
    "sendmessage":        "_fetch_nothing",
}


class MPDClientBase(object):

    def __init__(self, use_unicode=False):
        self.iterate = False
        self.use_unicode = use_unicode
        self._reset()

    def disconnect(self):
        raise NotImplementedError(
            "MPDClientBase does not implement disconnect")

    def _reset(self):
        self.mpd_version = None
        self._command_list = None

    def _parse_pair(self, line, separator):
        if line is None:
            return
        pair = line.split(separator, 1)
        if len(pair) < 2:
            raise ProtocolError("Could not parse pair: '{}'".format(line))
        return pair

    def _parse_pairs(self, lines, separator=": "):
        for line in lines:
            yield self._parse_pair(line, separator)

    def _parse_objects(self, lines, delimiters=[]):
        obj = {}
        for key, value in self._parse_pairs(lines):
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

    ##########################
    # command result callbacks

    def _parse_changes(self, lines):
        """Related commands:

        - plchangesposid
        """
        return self._parse_objects(lines, ["cpos"])

    def _parse_database(self, lines):
        """Related commands:

        - listall
        - listallinfo
        - listfiles
        - lsinfo
        """
        return self._parse_objects(lines, ["file", "directory", "playlist"])

    def _parse_idle(self, lines):
        """Related commands:
        - idle
        """
        return self._parse_list(lines)

    def _parse_item(self, lines):
        """Related commands:

        - addid
        - config
        - replay_gain_status
        - rescan
        - update
        """
        pairs = list(self._parse_pairs(lines))
        if len(pairs) != 1:
            return
        return pairs[0][1]

    def _parse_list(self, lines):
        """Related commands:

        - channels
        - commands
        - list
        - listplaylist
        - notcommands
        - tagtypes
        - urlhandlers
        """
        seen = None
        for key, value in self._parse_pairs(lines):
            if key != seen:
                if seen is not None:
                    raise ProtocolError(
                        "Expected key '{}', got '{}'".format(seen, key))
                seen = key
            yield value

    def _parse_messages(self, lines):
        """Related commands:

        - readmessages
        """
        return self._parse_objects(lines, ["channel"])

    def _parse_mounts(self, lines):
        """Related commands:

        - listmounts
        """
        return self._parse_objects(lines, ["mount"])

    def _parse_neighbors(self, lines):
        """Related commands:

        - listneighbors
        """
        return self._parse_objects(lines, ["neighbor"])

    def _parse_nothing(self, lines):
        """Related commands:

        - add
        - addtagid
        - clear
        - clearerror
        - cleartagid
        - consume
        - crossfade
        - delete
        - deleteid
        - disableoutput
        - enableoutput
        - findadd
        - load
        - mixrampdb
        - mixrampdelay
        - mount
        - move
        - moveid
        - next
        - password
        - pause
        - ping
        - play
        - playid
        - playlistadd
        - playlistclear
        - playlistdelete
        - playlistmove
        - previous
        - prio
        - prioid
        - random
        - rangeid
        - rename
        - repeat
        - replay_gain_mode
        - rm
        - save
        - searchadd
        - searchaddpl
        - seek
        - seekcur
        - seekid
        - sendmessage
        - setvol
        - shuffle
        - single
        - sticker delete
        - sticker set
        - stop
        - subscribe
        - swap
        - swapid
        - toggleoutput
        - umount
        - unsubscribe
        """
        return

    def _parse_object(self, lines):
        """Related commands:

        - count
        - currentsong
        - readcomments
        - stats
        - status
        """
        objs = list(self._parse_objects(lines))
        if not objs:
            return {}
        return objs[0]

    def _parse_outputs(self, lines):
        """Related commands:

        - outputs
        """
        return self._parse_objects(lines, ["outputid"])

    def _parse_playlist(self, lines):
        """Related commands:

        - playlist
        """
        for key, value in self._parse_pairs(lines, ":"):
            yield value

    def _parse_playlists(self, lines):
        """Related commands:

        - listplaylists
        """
        return self._parse_objects(lines, ["playlist"])

    def _parse_plugins(self, lines):
        """Related commands:

        - decoders
        """
        return self._parse_objects(lines, ["plugin"])

    def _parse_songs(self, lines):
        """Related commands:

        - find
        - listplaylistinfo
        - playlistfind
        - playlistid
        - playlistinfo
        - playlistsearch
        - plchanges
        - search
        - sticker find
        """
        return self._parse_objects(lines, ["file"])

    def _parse_sticker(self, lines):
        """Related commands:

        - sticker get
        """
        key, value = list(self._parse_stickers(lines))[0]
        return value

    def _parse_stickers(self, lines):
        """Related commands:

        - sticker list
        """
        for key, sticker in self._parse_pairs(lines):
            value = sticker.split('=', 1)
            if len(value) < 2:
                raise ProtocolError(
                    "Could not parse sticker: {}".format(repr(sticker)))
            yield tuple(value)


class MPDClient(MPDClientBase):
    idletimeout = None
    _timeout = None

    def __init__(self, use_unicode=False):
        super(MPDClient, self).__init__(use_unicode=use_unicode)

    def _reset(self):
        super(MPDClient, self)._reset()
        self._pending = []
        self._iterating = False
        self._sock = None
        self._rfile = _NotConnected()
        self._wfile = _NotConnected()

    def _send(self, command, args, retval):
        if self._command_list is not None:
            raise CommandListError(
                "Cannot use send_{} in a command list".format(command))
        self._write_command(command, args)
        if retval is not None:
            self._pending.append(command)

    def _fetch(self, command, args, retval):
        if self._command_list is not None:
            raise CommandListError(
                "Cannot use fetch_{} in a command list".format(command))
        if self._iterating:
            raise IteratingError(
                "Cannot use fetch_{} while iterating".format(command))
        if not self._pending:
            raise PendingCommandError("No pending commands to fetch")
        if self._pending[0] != command:
            raise PendingCommandError(
                "'{}' is not the currently pending command".format(command))
        del self._pending[0]
        if isinstance(retval, Callable):
            return retval()
        return retval

    def _execute(self, command, args, retval):
        if self._iterating:
            raise IteratingError(
                "Cannot execute '{}' while iterating".format(command))
        if self._pending:
            raise PendingCommandError(
                "Cannot execute '{}' with pending commands".format(command))
        if self._command_list is not None:
            if not isinstance(retval, Callable):
                raise CommandListError(
                    "'{}' not allowed in command list".format(command))
            self._write_command(command, args)
            self._command_list.append(retval)
        else:
            self._write_command(command, args)
            if isinstance(retval, Callable):
                return retval()
            return retval

    def _write_line(self, line):
        self._wfile.write("{}\n".format(line))
        self._wfile.flush()

    def _write_command(self, command, args=[]):
        parts = [command]
        for arg in args:
            if type(arg) is tuple:
                if len(arg) == 0:
                    parts.append('":"')
                elif len(arg) == 1:
                    parts.append('"{}:"'.format(int(arg[0])))
                else:
                    parts.append('"{}:{}"'.format(int(arg[0]), int(arg[1])))
            else:
                parts.append('"{}"'.format(escape(encode_str(arg))))
        # Minimize logging cost if the logging is not activated.
        if logger.isEnabledFor(logging.DEBUG):
            if command == "password":
                logger.debug("Calling MPD password(******)")
            else:
                logger.debug("Calling MPD %s%r", command, args)
        self._write_line(" ".join(parts))

    ##################
    # response helpers

    def _read_line(self):
        line = self._rfile.readline()
        if self.use_unicode:
            line = decode_str(line)
        if not line.endswith("\n"):
            self.disconnect()
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError(error)
        if self._command_list is not None:
            if line == NEXT:
                return
            if line == SUCCESS:
                raise ProtocolError("Got unexpected '{}'".format(SUCCESS))
        elif line == SUCCESS:
            return
        return line

    def _read_lines(self):
        line = self._read_line()
        while line is not None:
            yield line
            line = self._read_line()

    def _read_command_list(self):
        try:
            for retval in self._command_list:
                yield retval()
        finally:
            self._command_list = None
        self._fetch_nothing()

    def _iterator_wrapper(self, iterator):
        try:
            for item in iterator:
                yield item
        finally:
            self._iterating = False

    def _wrap_iterator(self, iterator):
        if not self.iterate:
            return list(iterator)
        self._iterating = True
        return self._iterator_wrapper(iterator)

    ####################
    # response callbacks

    def _fetch_nothing(self):
        line = self._read_line()
        if line is not None:
            raise ProtocolError(
                "Got unexpected return value: '{}'".format(line))

    def _fetch_item(self):
        return self._parse_item(self._read_lines())

    def _fetch_sticker(self):
        return self._parse_sticker(self._read_lines())

    def _fetch_stickers(self):
        return self._parse_stickers(self._read_lines())

    def _fetch_list(self):
        return self._wrap_iterator(self._parse_list(self._read_lines()))

    def _fetch_playlist(self):
        return self._wrap_iterator(self._parse_playlist(self._read_lines()))

    def _fetch_object(self):
        return self._parse_object(self._read_lines())

    def _fetch_changes(self):
        return self._parse_changes(self._read_lines())

    def _fetch_idle(self):
        self._sock.settimeout(self.idletimeout)
        ret = self._fetch_list()
        self._sock.settimeout(self._timeout)
        return ret

    def _fetch_songs(self):
        return self._parse_songs(self._read_lines())

    def _fetch_mounts(self):
        return self._parse_mounts(self._read_lines())

    def _fetch_neighbors(self):
        return self._parse_neighbors(self._read_lines())

    def _fetch_playlists(self):
        return self._parse_playlists(self._read_lines())

    def _fetch_database(self):
        return self._parse_database(self._read_lines())

    def _fetch_messages(self):
        return self._parse_messages(self._read_lines())

    def _fetch_outputs(self):
        return self._parse_outputs(self._read_lines())

    def _fetch_plugins(self):
        return self._parse_plugins(self._read_lines())

    # end response callbacks
    ########################

    def _fetch_command_list(self):
        return self._wrap_iterator(self._read_command_list())

    def _hello(self):
        line = self._rfile.readline()
        if not line.endswith("\n"):
            self.disconnect()
            raise ConnectionError("Connection lost while reading MPD hello")
        line = line.rstrip("\n")
        if not line.startswith(HELLO_PREFIX):
            raise ProtocolError("Got invalid MPD hello: '{}'".format(line))
        self.mpd_version = line[len(HELLO_PREFIX):].strip()

    def _connect_unix(self, path):
        if not hasattr(socket, "AF_UNIX"):
            raise ConnectionError(
                "Unix domain sockets not supported on this platform")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect(path)
        return sock

    def _connect_tcp(self, host, port):
        try:
            flags = socket.AI_ADDRCONFIG
        except AttributeError:
            flags = 0
        err = None
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM, socket.IPPROTO_TCP,
                                      flags):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.settimeout(self.timeout)
                sock.connect(sa)
                return sock
            except socket.error as e:
                err = e
                if sock is not None:
                    sock.close()
        if err is not None:
            raise err
        else:
            raise ConnectionError("getaddrinfo returns an empty list")

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout
        if self._sock is not None:
            self._sock.settimeout(timeout)

    def connect(self, host, port, timeout=None):
        logger.info(
            "Calling MPD connect(%r, %r, timeout=%r)", host, port, timeout)
        if self._sock is not None:
            raise ConnectionError("Already connected")
        if timeout is not None:
            warnings.warn(
                "The timeout parameter in connect() is deprecated! "
                "Use MPDClient.timeout = yourtimeout instead.",
                DeprecationWarning)
            self.timeout = timeout
        if host.startswith("/"):
            self._sock = self._connect_unix(host)
        else:
            self._sock = self._connect_tcp(host, port)
        if IS_PYTHON2:
            self._rfile = self._sock.makefile("r")
            self._wfile = self._sock.makefile("w")
        else:
            # - Force UTF-8 encoding, since this is dependant from the LC_CTYPE
            #   locale.
            # - by setting newline explicit, we force to send '\n' also on
            #   windows
            self._rfile = self._sock.makefile(
                "r",
                encoding="utf-8",
                newline="\n")
            self._wfile = self._sock.makefile(
                "w",
                encoding="utf-8",
                newline="\n")
        try:
            self._hello()
        except:
            self.disconnect()
            raise

    def disconnect(self):
        logger.info("Calling MPD disconnect()")
        if (self._rfile is not None
                and not isinstance(self._rfile, _NotConnected)):
            self._rfile.close()
        if (self._wfile is not None
                and not isinstance(self._wfile, _NotConnected)):
            self._wfile.close()
        if self._sock is not None:
            self._sock.close()
        self._reset()

    def fileno(self):
        if self._sock is None:
            raise ConnectionError("Not connected")
        return self._sock.fileno()

    def noidle(self):
        if not self._pending or self._pending[0] != 'idle':
            msg = 'cannot send noidle if send_idle was not called'
            raise CommandError(msg)
        del self._pending[0]
        self._write_command("noidle")
        return self._fetch_list()

    def command_list_ok_begin(self):
        if self._command_list is not None:
            raise CommandListError("Already in command list")
        if self._iterating:
            raise IteratingError("Cannot begin command list while iterating")
        if self._pending:
            raise PendingCommandError(
                "Cannot begin command list with pending commands")
        self._write_command("command_list_ok_begin")
        self._command_list = []

    def command_list_end(self):
        if self._command_list is None:
            raise CommandListError("Not in command list")
        if self._iterating:
            raise IteratingError("Already iterating over a command list")
        self._write_command("command_list_end")
        return self._fetch_command_list()

    @classmethod
    def add_command(cls, name, callback):
        method = new_function(cls._execute, name, callback)
        send_method = new_function(cls._send, name, callback)
        fetch_method = new_function(cls._fetch, name, callback)
        # create new mpd commands as function in three flavors:
        # normal, with "send_"-prefix and with "fetch_"-prefix
        escaped_name = name.replace(" ", "_")
        setattr(cls, escaped_name, method)
        setattr(cls, "send_" + escaped_name, send_method)
        setattr(cls, "fetch_" + escaped_name, fetch_method)

    @classmethod
    def remove_command(cls, name):
        if not hasattr(cls, name):
            raise ValueError(
                "Can't remove not existent '{}' command".format(name))
        name = name.replace(" ", "_")
        delattr(cls, str(name))
        delattr(cls, str("send_" + name))
        delattr(cls, str("fetch_" + name))


def bound_decorator(self, function):
    """Bind decorator to self.
    """
    if not isinstance(function, Callable):
        return None
    def decorator(*args, **kwargs):
        return function(self, *args, **kwargs)
    return decorator


def new_function(wrapper, name, return_value):
    def decorator(self, *args):
        return wrapper(self, name, args, bound_decorator(self, return_value))
    return decorator


def lookup_func(cls, name):
    func = None
    if name in cls.__dict__:
        func = cls.__dict__[name]
    else:
        for base in cls.__bases__:
            func = lookup_func(base, name)
            if func is not None:
                break
    return func


for key, value in _commands.items():
    return_value = lookup_func(MPDClient, value)
    MPDClient.add_command(key, return_value)


def escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
