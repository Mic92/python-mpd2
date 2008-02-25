#! /usr/bin/env python

import socket


HELLO_PREFIX = "OK MPD "
ERROR_PREFIX = "ACK "
SUCCESS = "OK"
NEXT = "list_OK"


class MPDError(Exception):
    pass

class ProtocolError(MPDError):
    pass

class CommandError(MPDError):
    pass

class CommandListError(MPDError):
    pass


class MPDClient(object):
    def __init__(self):
        self.iterate = False
        self._reset()
        self._commands = {
            # Admin Commands
            "disableoutput":    self._getnone,
            "enableoutput":     self._getnone,
            "kill":             None,
            "update":           self._getitem,
            # Informational Commands
            "status":           self._getobject,
            "stats":            self._getobject,
            "outputs":          self._getoutputs,
            "commands":         self._getlist,
            "notcommands":      self._getlist,
            "tagtypes":         self._getlist,
            "urlhandlers":      self._getlist,
            # Database Commands
            "find":             self._getsongs,
            "list":             self._getlist,
            "listall":          self._getdatabase,
            "listallinfo":      self._getdatabase,
            "lsinfo":           self._getdatabase,
            "search":           self._getsongs,
            "count":            self._getobject,
            # Playlist Commands
            "add":              self._getnone,
            "addid":            self._getitem,
            "clear":            self._getnone,
            "currentsong":      self._getobject,
            "delete":           self._getnone,
            "deleteid":         self._getnone,
            "load":             self._getnone,
            "rename":           self._getnone,
            "move":             self._getnone,
            "moveid":           self._getnone,
            "playlist":         self._getplaylist,
            "playlistinfo":     self._getsongs,
            "playlistid":       self._getsongs,
            "plchanges":        self._getsongs,
            "plchangesposid":   self._getchanges,
            "rm":               self._getnone,
            "save":             self._getnone,
            "shuffle":          self._getnone,
            "swap":             self._getnone,
            "swapid":           self._getnone,
            "listplaylist":     self._getlist,
            "listplaylistinfo": self._getsongs,
            "playlistadd":      self._getnone,
            "playlistclear":    self._getnone,
            "playlistdelete":   self._getnone,
            "playlistmove":     self._getnone,
            "playlistfind":     self._getsongs,
            "playlistsearch":   self._getsongs,
            # Playback Commands
            "crossfade":        self._getnone,
            "next":             self._getnone,
            "pause":            self._getnone,
            "play":             self._getnone,
            "playid":           self._getnone,
            "previous":         self._getnone,
            "random":           self._getnone,
            "repeat":           self._getnone,
            "seek":             self._getnone,
            "seekid":           self._getnone,
            "setvol":           self._getnone,
            "stop":             self._getnone,
            "volume":           self._getnone,
            # Miscellaneous Commands
            "clearerror":       self._getnone,
            "close":            None,
            "password":         self._getnone,
            "ping":             self._getnone,
        }

    def __getattr__(self, attr):
        try:
            retval = self._commands[attr]
        except KeyError:
            raise AttributeError, "'%s' object has no attribute '%s'" % \
                                  (self.__class__.__name__, attr)
        return lambda *args: self._docommand(attr, args, retval)

    def _docommand(self, command, args, retval):
        if self._commandlist is not None and not callable(retval):
            raise CommandListError, "%s not allowed in command list" % command
        self._writecommand(command, args)
        if self._commandlist is None:
            if callable(retval):
                return retval()
            return retval
        self._commandlist.append(retval)

    def _writeline(self, line):
        self._sockfile.write("%s\n" % line)
        self._sockfile.flush()

    def _writecommand(self, command, args=[]):
        parts = [command]
        for arg in args:
            parts.append('"%s"' % escape(str(arg)))
        self._writeline(" ".join(parts))

    def _readline(self):
        line = self._sockfile.readline().rstrip("\n")
        if line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            raise CommandError, error
        if self._commandlist is not None:
            if line == NEXT:
                return
            if line == SUCCESS:
                raise ProtocolError, "Got unexpected '%s'" % SUCCESS
        elif line == SUCCESS:
            return
        return line

    def _readitem(self, separator):
        line = self._readline()
        if line is None:
            return
        item = line.split(separator, 1)
        if len(item) < 2:
            raise ProtocolError, "Could not parse item: '%s'" % line
        return item

    def _readitems(self, separator=": "):
        item = self._readitem(separator)
        while item:
            yield item
            item = self._readitem(separator)
        raise StopIteration

    def _readlist(self):
        seen = None
        for key, value in self._readitems():
            if key != seen:
                if seen is not None:
                    raise ProtocolError, "Expected key '%s', got '%s'" % \
                                         (seen, key)
                seen = key
            yield value
        raise StopIteration

    def _readplaylist(self):
        for key, value in self._readitems(":"):
            yield value
        raise StopIteration

    def _readobjects(self, delimiters=[]):
        obj = {}
        for key, value in self._readitems():
            key = key.lower()
            if obj:
                if key in delimiters:
                    yield obj
                    obj = {}
                elif obj.has_key(key):
                    if not isinstance(obj[key], list):
                        obj[key] = [obj[key], value]
                    else:
                        obj[key].append(value)
                    continue
            obj[key] = value
        if obj:
            yield obj
        raise StopIteration

    def _readcommandlist(self):
        for retval in self._commandlist:
            yield retval()
        self._commandlist = None
        self._getnone()
        raise StopIteration

    def _wrapiterator(self, iterator):
        if not self.iterate:
            return list(iterator)
        return iterator

    def _getnone(self):
        line = self._readline()
        if line is not None:
            raise ProtocolError, "Got unexpected return value: '%s'" % line

    def _getitem(self):
        items = list(self._readitems())
        if len(items) != 1:
            raise ProtocolError, "Expected 1 item, got %i" % len(items)
        return items[0][1]

    def _getlist(self):
        return self._wrapiterator(self._readlist())

    def _getplaylist(self):
        return self._wrapiterator(self._readplaylist())

    def _getobject(self):
        objs = list(self._readobjects())
        if not objs:
            return {}
        return objs[0]

    def _getobjects(self, delimiters):
        return self._wrapiterator(self._readobjects(delimiters))

    def _getsongs(self):
        return self._getobjects(["file"])

    def _getdatabase(self):
        return self._getobjects(["file", "directory", "playlist"])

    def _getoutputs(self):
        return self._getobjects(["outputid"])

    def _getchanges(self):
        return self._getobjects(["cpos"])

    def _getcommandlist(self):
        return self._wrapiterator(self._readcommandlist())

    def _hello(self):
        line = self._sockfile.readline().rstrip("\n")
        if not line.startswith(HELLO_PREFIX):
            raise ProtocolError, "Got invalid MPD hello: '%s'" % line
        self.mpd_version = line[len(HELLO_PREFIX):].strip()

    def _reset(self):
        self.mpd_version = None
        self._commandlist = None
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sockfile = self._sock.makefile("rb+")

    def connect(self, host, port):
        self.disconnect()
        self._sock.connect((host, port))
        self._hello()

    def disconnect(self):
        self._sockfile.close()
        self._sock.close()
        self._reset()

    def command_list_ok_begin(self):
        if self._commandlist is not None:
            raise CommandListError, "Already in command list"
        self._writecommand("command_list_ok_begin")
        self._commandlist = []

    def command_list_end(self):
        if self._commandlist is None:
            raise CommandListError, "Not in command list"
        self._writecommand("command_list_end")
        return self._getcommandlist()


def escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
