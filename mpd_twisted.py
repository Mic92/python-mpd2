# python-mpd2: Python MPD client library
#
# Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
# Copyright (C) 2010  Jasper St. Pierre <jstpierre@mecheye.net>
# Copyright (C) 2010,2011  Oliver Mader <b52@reaktor42.de>
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

from twisted.internet import defer
from twisted.protocols import basic
from types import GeneratorType
import mpd


@mpd.mpd_command_provider
class MPDProtocol(basic.LineReceiver, mpd.MPDClientBase):
    debug = False
    delimiter = "\n"
    _commands = dict()

    def __init__(self, use_unicode=False):
        super(MPDProtocol, self).__init__(use_unicode=use_unicode)
        self.iterate = True
        self._reset()

    @classmethod
    def add_command(cls, name, callback):
        escaped_name = name.replace(" ", "_")
        cls._commands[escaped_name] = callback

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if self.debug:
            logger.info('MPDProtocol.lineReceived: {}'.format(line))
        command_list = self._state and isinstance(self._state[0], list)
        state_list = self._state[0] if command_list else self._state
        if line.startswith(mpd.HELLO_PREFIX):
            self.mpd_version = line[len(mpd.HELLO_PREFIX):].strip()
        elif line.startswith(mpd.ERROR_PREFIX):
            error = line[len(mpd.ERROR_PREFIX):].strip()
            if command_list:
                state_list[0].errback(mpd.CommandError(error))
                for state in state_list[1:-1]:
                    state.errback(
                        mpd.CommandListError("An earlier command failed."))
                state_list[-1].errback(mpd.CommandListError(error))
                del self._state[0]
                del self._command_list_results[0]
            else:
                state_list.pop(0).errback(mpd.CommandError(error))
        elif line == mpd.SUCCESS or (command_list and line == mpd.NEXT):
            parser = state_list.pop(0).callback(self._buffer[:])
            self._buffer = []
            if command_list and line == mpd.SUCCESS:
                del self._state[0]
        else:
            self._buffer.append(line)

    def noidle(self):
        # XXX
        #if not self._pending or self._pending[0] != 'idle':
        #    msg = 'cannot send noidle if send_idle was not called'
        #    raise mpd.CommandError(msg)
        #del self._pending[0]
        #self._write_command("noidle")
        #return self._fetch_list()
        pass

    def command_list_ok_begin(self):
        if self._command_list:
            raise mpd.CommandListError("Already in command list")
        self._write_command("command_list_ok_begin")
        self._command_list = True
        self._command_list_results.append([])
        self._state.append([])

    def command_list_end(self):
        if not self._command_list:
            raise mpd.CommandListError("Not in command list")
        self._write_command("command_list_end")
        deferred = defer.Deferred()
        deferred.addCallback(self._parse_command_list_end)
        self._state[-1].append(deferred)
        self._command_list = False
        return deferred

    def __getattr__(self, attr):
        try:
            return lambda *args: self._execute(attr, args, self._commands[attr])
        except KeyError:
            msg = "'{}' object has no attribute '{}'".format(
                self.__class__.__name__, attr)
            raise AttributeError(msg)

    def _reset(self):
        super(MPDProtocol, self)._reset()
        self.mpd_version = None
        self._command_list = False
        self._command_list_results = []
        self._buffer = []
        self._state = []

    def _execute(self, command, args, parser):
        if self._command_list and not callable(parser):
            msg = "{} not allowed in command list".format(command)
            raise mpd.CommandListError(msg)
        self._write_command(command, args)
        deferred = defer.Deferred()
        (self._state[-1] if self._command_list else self._state).append(deferred)
        if parser is not self.NOOP:
            deferred.addCallback(parser)
            if self._command_list:
                deferred.addCallback(self._parse_command_list_item)
        return deferred

    def _write_command(self, command, args=[]):
        parts = [command]
        parts += ['"{}"'.format(escape(arg.encode('utf-8')) \
            if isinstance(arg, unicode) else str(arg)) for arg in args]
        cmd = " ".join(parts)
        if self.debug:
            logger.info('MPDProtocol._write_command: {}'.format(cmd))
        self.sendLine(cmd)

    def _parse_command_list_item(self, result):
        # TODO: find a better way to do this
        if type(result) == GeneratorType:
            result = list(result)
        self._command_list_results[0].append(result)
        return result

    def _parse_command_list_end(self, lines):
        return self._command_list_results.pop(0)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
