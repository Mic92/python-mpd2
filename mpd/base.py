# python-mpd2: Python MPD client library
#
# Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
# Copyright (C) 2012  J. Thalheim <jthalheim@gmail.com>
# Copyright (C) 2016  Robert Niederreiter <rnix@squarewave.at>
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
import socket
import sys
import warnings


###############################################################################
# constants
###############################################################################

VERSION = (1, 1, 0)
HELLO_PREFIX = "OK MPD "
ERROR_PREFIX = "ACK "
SUCCESS = "OK"
NEXT = "list_OK"


###############################################################################
# utils
###############################################################################

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


def escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


###############################################################################
# logging
###############################################################################

try:
    from logging import NullHandler
except ImportError:  # NullHandler was introduced in python2.7
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())


###############################################################################
# exceptions
###############################################################################

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


###############################################################################
# command registration
###############################################################################

class mpd_commands(object):
    """Decorator for registering MPD commands with it's corresponding result
    callback.
    """

    def __init__(self, *commands, **kwargs):
        self.commands = commands
        self.is_direct = kwargs.pop('is_direct', False)
        if kwargs:
            raise AttributeError(
                "mpd_commands() got unexpected keyword"
                " arguments %s" % ",".join(kwargs)
            )

    def __call__(self, ob):
        ob.mpd_commands = self.commands
        ob.mpd_commands_direct = self.is_direct
        return ob


def mpd_command_provider(cls):
    """Decorator hooking up registered MPD commands to concrete client
    implementation.

    A class using this decorator must inherit from ``MPDClientBase`` and
    implement it's ``add_command`` function.
    """
    def collect(cls, callbacks=dict()):
        """Collect MPD command callbacks from given class.

        Searches class __dict__ on given class and all it's bases for functions
        which have been decorated with @mpd_commands and returns a dict
        containing callback name as keys and
        (callback, callback implementing class) tuples as values.
        """
        for name, ob in cls.__dict__.items():
            if hasattr(ob, "mpd_commands") and name not in callbacks:
                callbacks[name] = (ob, cls)
        for base in cls.__bases__:
            callbacks = collect(base, callbacks)
        return callbacks

    for name, value in collect(cls).items():
        callback, from_ = value
        for command in callback.mpd_commands:
            cls.add_command(command, callback)
    return cls


class Noop(object):
    """An instance of this class represents a MPD command callback which
    does nothing.
    """
    mpd_commands = None


###############################################################################
# abstract base client
###############################################################################

class MPDClientBase(object):
    """Abstract MPD client.

    This class defines a general client contract, provides MPD protocol parsers
    and defines all available MPD commands and it's corresponding result
    parsing callbacks. There might be the need of overriding some callbacks on
    subclasses.
    """

    def __init__(self, use_unicode=False):
        self.iterate = False
        self.use_unicode = use_unicode
        self._reset()

    @classmethod
    def add_command(cls, name, callback):
        raise NotImplementedError(
            'Abstract ``MPDClientBase`` does not implement ``add_command``')

    def noidle(self):
        raise NotImplementedError(
            'Abstract ``MPDClientBase`` does not implement ``noidle``')

    def command_list_ok_begin(self):
        raise NotImplementedError(
            'Abstract ``MPDClientBase`` does not implement '
            '``command_list_ok_begin``')

    def command_list_end(self):
        raise NotImplementedError(
            'Abstract ``MPDClientBase`` does not implement '
            '``command_list_end``')

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

    def _parse_objects(self, lines, delimiters=[], lookup_delimiter=False):
        obj = {}
        for key, value in self._parse_pairs(lines):
            key = key.lower()
            if lookup_delimiter and not delimiters:
                delimiters = [key]
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

    # Use this instead of _parse_objects whenever the result is returned
    # immediately in a command implementation
    _parse_objects_direct = _parse_objects

    def _parse_raw_stickers(self, lines):
        for key, sticker in self._parse_pairs(lines):
            value = sticker.split('=', 1)
            if len(value) < 2:
                raise ProtocolError(
                    "Could not parse sticker: {}".format(repr(sticker)))
            yield tuple(value)

    NOOP = mpd_commands('close', 'kill')(Noop())

    @mpd_commands('plchangesposid', is_direct=True)
    def _parse_changes(self, lines):
        return self._parse_objects_direct(lines, ["cpos"])

    @mpd_commands('listall', 'listallinfo', 'listfiles', 'lsinfo', is_direct=True)
    def _parse_database(self, lines):
        return self._parse_objects_direct(lines, ["file", "directory", "playlist"])

    @mpd_commands('idle')
    def _parse_idle(self, lines):
        return self._parse_list(lines)

    @mpd_commands('addid', 'config', 'replay_gain_status', 'rescan', 'update')
    def _parse_item(self, lines):
        pairs = list(self._parse_pairs(lines))
        if len(pairs) != 1:
            return
        return pairs[0][1]

    @mpd_commands(
        'channels', 'commands', 'listplaylist', 'notcommands',
        'tagtypes', 'urlhandlers')
    def _parse_list(self, lines):
        seen = None
        for key, value in self._parse_pairs(lines):
            if key != seen:
                if seen is not None:
                    raise ProtocolError(
                        "Expected key '{}', got '{}'".format(seen, key))
                seen = key
            yield value

    @mpd_commands('list', is_direct=True)
    def _parse_list_groups(self, lines):
        lines = iter(lines)
        return self._parse_objects_direct(lines, lookup_delimiter=True)

    @mpd_commands('readmessages', is_direct=True)
    def _parse_messages(self, lines):
        return self._parse_objects_direct(lines, ["channel"])

    @mpd_commands('listmounts', is_direct=True)
    def _parse_mounts(self, lines):
        return self._parse_objects_direct(lines, ["mount"])

    @mpd_commands('listneighbors', is_direct=True)
    def _parse_neighbors(self, lines):
        return self._parse_objects_direct(lines, ["neighbor"])

    @mpd_commands(
        'add', 'addtagid', 'clear', 'clearerror', 'cleartagid', 'consume',
        'crossfade', 'delete', 'deleteid', 'disableoutput', 'enableoutput',
        'findadd', 'load', 'mixrampdb', 'mixrampdelay', 'mount', 'move',
        'moveid', 'next', 'outputvolume', 'password', 'pause', 'ping', 'play',
        'playid', 'playlistadd', 'playlistclear', 'playlistdelete', 'playlistmove',
        'previous', 'prio', 'prioid', 'random', 'rangeid', 'rename', 'repeat',
        'replay_gain_mode', 'rm', 'save', 'searchadd', 'searchaddpl', 'seek',
        'seekcur', 'seekid', 'sendmessage', 'setvol', 'shuffle', 'single',
        'sticker delete', 'sticker set', 'stop', 'subscribe', 'swap', 'swapid',
        'toggleoutput', 'umount', 'unsubscribe')
    def _parse_nothing(self, lines):
        for line in lines:
            raise ProtocolError(
                "Got unexpected return value: '{}'".format(', '.join(lines)))

    @mpd_commands('count', 'currentsong', 'readcomments', 'stats', 'status')
    def _parse_object(self, lines):
        objs = list(self._parse_objects(lines))
        if not objs:
            return {}
        return objs[0]

    @mpd_commands('outputs', is_direct=True)
    def _parse_outputs(self, lines):
        return self._parse_objects_direct(lines, ["outputid"])

    @mpd_commands('playlist')
    def _parse_playlist(self, lines):
        for key, value in self._parse_pairs(lines, ":"):
            yield value

    @mpd_commands('listplaylists', is_direct=True)
    def _parse_playlists(self, lines):
        return self._parse_objects_direct(lines, ["playlist"])

    @mpd_commands('decoders', is_direct=True)
    def _parse_plugins(self, lines):
        return self._parse_objects_direct(lines, ["plugin"])

    @mpd_commands(
        'find', 'listplaylistinfo', 'playlistfind', 'playlistid',
        'playlistinfo', 'playlistsearch', 'plchanges', 'search',
        'sticker find', is_direct=True)
    def _parse_songs(self, lines):
        return self._parse_objects_direct(lines, ["file"])

    @mpd_commands('sticker get')
    def _parse_sticker(self, lines):
        key, value = list(self._parse_raw_stickers(lines))[0]
        return value

    @mpd_commands('sticker list')
    def _parse_stickers(self, lines):
        return dict(self._parse_raw_stickers(lines))


###############################################################################
# sync client
###############################################################################

def _create_callback(self, function, wrap_result):
    """Create MPD command related response callback.
    """
    if not callable(function):
        return None

    def command_callback():
        # command result callback expects response from MPD as iterable lines,
        # thus read available lines from socket
        res = function(self, self._read_lines())
        # wrap result in iterator helper if desired
        if wrap_result:
            res = self._wrap_iterator(res)
        return res
    return command_callback


def _create_command(wrapper, name, return_value, wrap_result):
    """Create MPD command related function.
    """
    def mpd_command(self, *args):
        callback = _create_callback(self, return_value, wrap_result)
        return wrapper(self, name, args, callback)
    return mpd_command


class _NotConnected(object):
    def __getattr__(self, attr):
        return self._dummy

    def _dummy(*args):
        raise ConnectionError("Not connected")


@mpd_command_provider
class MPDClient(MPDClientBase):
    idletimeout = None
    _timeout = None
    _wrap_iterator_parsers = [
        MPDClientBase._parse_list,
        MPDClientBase._parse_list_groups,
        MPDClientBase._parse_playlist,
        MPDClientBase._parse_changes,
        MPDClientBase._parse_songs,
        MPDClientBase._parse_mounts,
        MPDClientBase._parse_neighbors,
        MPDClientBase._parse_playlists,
        MPDClientBase._parse_database,
        MPDClientBase._parse_messages,
        MPDClientBase._parse_outputs,
        MPDClientBase._parse_plugins
    ]
    if IS_PYTHON2:
        _wrap_iterator_parsers = [f.__func__ for f in _wrap_iterator_parsers]

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
        warnings.warn(
            "``send_{}`` is deprecated in favor of "
            "asynchronous API".format(command),
            DeprecationWarning)
        if self._command_list is not None:
            raise CommandListError(
                "Cannot use send_{} in a command list".format(command))
        self._write_command(command, args)
        if retval is not None:
            self._pending.append(command)

    def _fetch(self, command, args, retval):
        warnings.warn(
            "``fetch_{}`` is deprecated in favor of "
            "asynchronous API".format(command),
            DeprecationWarning)
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
        if callable(retval):
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
            if not callable(retval):
                raise CommandListError(
                    "'{}' not allowed in command list".format(command))
            self._write_command(command, args)
            self._command_list.append(retval)
        else:
            self._write_command(command, args)
            if callable(retval):
                return retval()
            return retval

    def _write_line(self, line):
        try:
            self._wfile.write("{}\n".format(line))
            self._wfile.flush()
        except socket.error as e:
            error_message = "Connection to server was reset"
            logger.info(error_message)
            self._reset()
            if IS_PYTHON2:
                # Utilizing exec is not particularly elegant, however, it seems
                # to be the only way as Python3 handles exceptions quite
                # different to Python2. Without exec, the whole script is not
                # executable in Python3. Also "six" does it the same way:
                # https://bitbucket.org/gutworth/six/src/ (search "reraise")
                exec('raise ConnectionError, "' + error_message + '",'
                     'sys.exc_info()[2]')
            else:
                e = ConnectionError(error_message)
                raise e.with_traceback(sys.exc_info()[2])

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
        cmd = " ".join(parts)
        self._write_line(cmd)

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
        self._parse_nothing(self._read_lines())

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

    def _hello(self, line):
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
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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

    @mpd_commands('idle')
    def _parse_idle(self, lines):
        self._sock.settimeout(self.idletimeout)
        ret = self._wrap_iterator(self._parse_list(lines))
        self._sock.settimeout(self._timeout)
        return ret

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = timeout
        if self._sock is not None:
            self._sock.settimeout(timeout)

    def connect(self, host, port=None, timeout=None):
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
            if port is None:
                raise ValueError("port argument must be specified when connecting via tcp")
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
            helloline = self._rfile.readline()
            self._hello(helloline)
        except Exception:
            self.disconnect()
            raise

    def disconnect(self):
        logger.info("Calling MPD disconnect()")
        if (self._rfile is not None and
                not isinstance(self._rfile, _NotConnected)):
            self._rfile.close()
        if (self._wfile is not None and
                not isinstance(self._wfile, _NotConnected)):
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
        return self._wrap_iterator(self._parse_list(self._read_lines()))

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
        return self._wrap_iterator(self._read_command_list())

    @classmethod
    def add_command(cls, name, callback):
        wrap_result = callback in cls._wrap_iterator_parsers
        method = _create_command(cls._execute, name, callback, wrap_result)
        send_method = _create_command(cls._send, name, callback, wrap_result)
        fetch_method = _create_command(cls._fetch, name, callback, wrap_result)
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

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
