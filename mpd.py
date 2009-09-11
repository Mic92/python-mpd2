# Python MPD client library
# Copyright (C) 2008  J. Alexander Treuman <jat@spatialrift.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket


HELLO_PREFIX = "OK MPD "
ERROR_PREFIX = "ACK "
SUCCESS = "OK"
NEXT = "list_OK"


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


class _NotConnected(object):
    def __getattr__(self, attr):
        return self._dummy

    def _dummy(*args):
        raise ConnectionError("Not connected")

class MPDClient(object):
    def __init__(self):
        self.iterate = False
        self._reset()
        self._commands = {
            # Status Commands
            "clearerror":       self._fetch_nothing,
            "currentsong":      self._fetch_object,
            "idle":             self._fetch_list,
            "noidle":           None,
            "status":           self._fetch_object,
            "stats":            self._fetch_object,
            # Playback Option Commands
            "consume":          self._fetch_nothing,
            "crossfade":        self._fetch_nothing,
            "random":           self._fetch_nothing,
            "repeat":           self._fetch_nothing,
            "setvol":           self._fetch_nothing,
            "single":           self._fetch_nothing,
            "volume":           self._fetch_nothing,
            # Playback Control Commands
            "next":             self._fetch_nothing,
            "pause":            self._fetch_nothing,
            "play":             self._fetch_nothing,
            "playid":           self._fetch_nothing,
            "previous":         self._fetch_nothing,
            "seek":             self._fetch_nothing,
            "seekid":           self._fetch_nothing,
            "stop":             self._fetch_nothing,
            # Playlist Commands
            "add":              self._fetch_nothing,
            "addid":            self._fetch_item,
            "clear":            self._fetch_nothing,
            "delete":           self._fetch_nothing,
            "deleteid":         self._fetch_nothing,
            "move":             self._fetch_nothing,
            "moveid":           self._fetch_nothing,
            "playlist":         self._fetch_playlist,
            "playlistfind":     self._fetch_songs,
            "playlistid":       self._fetch_songs,
            "playlistinfo":     self._fetch_songs,
            "playlistsearch":   self._fetch_songs,
            "plchanges":        self._fetch_songs,
            "plchangesposid":   self._fetch_changes,
            "shuffle":          self._fetch_nothing,
            "swap":             self._fetch_nothing,
            "swapid":           self._fetch_nothing,
            # Stored Playlist Commands
            "listplaylist":     self._fetch_list,
            "listplaylistinfo": self._fetch_songs,
            "listplaylists":    self._fetch_playlists,
            "load":             self._fetch_nothing,
            "playlistadd":      self._fetch_nothing,
            "playlistclear":    self._fetch_nothing,
            "playlistdelete":   self._fetch_nothing,
            "playlistmove":     self._fetch_nothing,
            "rename":           self._fetch_nothing,
            "rm":               self._fetch_nothing,
            "save":             self._fetch_nothing,
            # Database Commands
            "count":            self._fetch_object,
            "find":             self._fetch_songs,
            "list":             self._fetch_list,
            "listall":          self._fetch_database,
            "listallinfo":      self._fetch_database,
            "lsinfo":           self._fetch_database,
            "search":           self._fetch_songs,
            "update":           self._fetch_item,
            # Connection Commands
            "close":            None,
            "kill":             None,
            "password":         self._fetch_nothing,
            "ping":             self._fetch_nothing,
            # Audio Output Commands
            "disableoutput":    self._fetch_nothing,
            "enableoutput":     self._fetch_nothing,
            "outputs":          self._fetch_outputs,
            # Reflection Commands
            "commands":         self._fetch_list,
            "notcommands":      self._fetch_list,
            "tagtypes":         self._fetch_list,
            "urlhandlers":      self._fetch_list,
        }

    def __getattr__(self, attr):
        try:
            retval = self._commands[attr]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (self.__class__.__name__, attr))
        return lambda *args: self._execute(attr, args, retval)

    def _execute(self, command, args, retval):
        if self._command_list is not None and not callable(retval):
            raise CommandListError("%s not allowed in command list" % command)
        self._write_command(command, args)
        if self._command_list is None:
            if callable(retval):
                return retval()
            return retval
        self._command_list.append(retval)

    def _write_line(self, line):
        self._wfile.write("%s\n" % line)
        self._wfile.flush()

    def _write_command(self, command, args=[]):
        parts = [command]
        for arg in args:
            parts.append('"%s"' % escape(str(arg)))
        self._write_line(" ".join(parts))

    def _read_line(self):
        line = self._rfile.readline()
        if not line.endswith("\n"):
            raise ConnectionError("Connection lost while reading line")
        line = line.rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError(error)
        if self._command_list is not None:
            if line == NEXT:
                return
            if line == SUCCESS:
                raise ProtocolError("Got unexpected '%s'" % SUCCESS)
        elif line == SUCCESS:
            return
        return line

    def _read_pair(self, separator):
        line = self._read_line()
        if line is None:
            return
        pair = line.split(separator, 1)
        if len(pair) < 2:
            raise ProtocolError("Could not parse pair: '%s'" % line)
        return pair

    def _read_pairs(self, separator=": "):
        pair = self._read_pair(separator)
        while pair:
            yield pair
            pair = self._read_pair(separator)
        raise StopIteration

    def _read_list(self):
        seen = None
        for key, value in self._read_pairs():
            if key != seen:
                if seen is not None:
                    raise ProtocolError("Expected key '%s', got '%s'" %
                                        (seen, key))
                seen = key
            yield value
        raise StopIteration

    def _read_playlist(self):
        for key, value in self._read_pairs(":"):
            yield value
        raise StopIteration

    def _read_objects(self, delimiters=[]):
        obj = {}
        for key, value in self._read_pairs():
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
        raise StopIteration

    def _read_command_list(self):
        for retval in self._command_list:
            yield retval()
        self._command_list = None
        self._fetch_nothing()
        raise StopIteration

    def _wrap_iterator(self, iterator):
        if not self.iterate:
            return list(iterator)
        return iterator

    def _fetch_nothing(self):
        line = self._read_line()
        if line is not None:
            raise ProtocolError("Got unexpected return value: '%s'" % line)

    def _fetch_item(self):
        pairs = list(self._read_pairs())
        if len(pairs) != 1:
            return
        return pairs[0][1]

    def _fetch_list(self):
        return self._wrap_iterator(self._read_list())

    def _fetch_playlist(self):
        return self._wrap_iterator(self._read_playlist())

    def _fetch_object(self):
        objs = list(self._read_objects())
        if not objs:
            return {}
        return objs[0]

    def _fetch_objects(self, delimiters):
        return self._wrap_iterator(self._read_objects(delimiters))

    def _fetch_songs(self):
        return self._fetch_objects(["file"])

    def _fetch_playlists(self):
        return self._fetch_objects(["playlist"])

    def _fetch_database(self):
        return self._fetch_objects(["file", "directory", "playlist"])

    def _fetch_outputs(self):
        return self._fetch_objects(["outputid"])

    def _fetch_changes(self):
        return self._fetch_objects(["cpos"])

    def _fetch_command_list(self):
        return self._wrap_iterator(self._read_command_list())

    def _hello(self):
        line = self._rfile.readline()
        if not line.endswith("\n"):
            raise ConnectionError("Connection lost while reading MPD hello")
        line = line.rstrip("\n")
        if not line.startswith(HELLO_PREFIX):
            raise ProtocolError("Got invalid MPD hello: '%s'" % line)
        self.mpd_version = line[len(HELLO_PREFIX):].strip()

    def _reset(self):
        self.mpd_version = None
        self._command_list = None
        self._sock = None
        self._rfile = _NotConnected()
        self._wfile = _NotConnected()

    def _connect_unix(self, path):
        if not hasattr(socket, "AF_UNIX"):
            raise ConnectionError("Unix domain sockets not supported "
                                  "on this platform")
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(path)
        return sock

    def _connect_tcp(self, host, port):
        try:
            flags = socket.AI_ADDRCONFIG
        except AttributeError:
            flags = 0
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC,
                                      socket.SOCK_STREAM, socket.IPPROTO_TCP,
                                      flags):
            af, socktype, proto, canonname, sa = res
            try:
                sock = socket.socket(af, socktype, proto)
                sock.connect(sa)
            except socket.error, msg:
                if sock:
                    sock.close()
                sock = None
                continue
            break
        if not sock:
            raise socket.error(msg)
        return sock

    def connect(self, host, port):
        if self._sock:
            raise ConnectionError("Already connected")
        if host.startswith("/"):
            self._sock = self._connect_unix(host)
        else:
            self._sock = self._connect_tcp(host, port)
        self._rfile = self._sock.makefile("rb")
        self._wfile = self._sock.makefile("wb")
        try:
            self._hello()
        except:
            self.disconnect()
            raise

    def disconnect(self):
        self._rfile.close()
        self._wfile.close()
        self._sock.close()
        self._reset()

    def command_list_ok_begin(self):
        if self._command_list is not None:
            raise CommandListError("Already in command list")
        self._write_command("command_list_ok_begin")
        self._command_list = []

    def command_list_end(self):
        if self._command_list is None:
            raise CommandListError("Not in command list")
        self._write_command("command_list_end")
        return self._fetch_command_list()


def escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
