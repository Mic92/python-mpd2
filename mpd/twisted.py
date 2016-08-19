# python-mpd2: Python MPD client library
#
# Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
# Copyright (C) 2010  Jasper St. Pierre <jstpierre@mecheye.net>
# Copyright (C) 2010,2011  Oliver Mader <b52@reaktor42.de>
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

from __future__ import absolute_import
from mpd.base import CommandError
from mpd.base import CommandListError
from mpd.base import ERROR_PREFIX
from mpd.base import HELLO_PREFIX
from mpd.base import MPDClientBase
from mpd.base import NEXT
from mpd.base import SUCCESS
from mpd.base import logger
from mpd.base import mpd_command_provider
from mpd.base import mpd_commands
from twisted.internet import defer
from twisted.protocols import basic
from types import GeneratorType


def _create_command(wrapper, name, callback):
    def mpd_command(self, *args):
        def bound_callback(lines):
            return callback(self, lines)
        return wrapper(self, name, args, bound_callback)
    return mpd_command


@mpd_command_provider
class MPDProtocol(basic.LineReceiver, MPDClientBase):
    debug = False
    delimiter = "\n"

    def __init__(self, idle=True, use_unicode=False):
        super(MPDProtocol, self).__init__(use_unicode=use_unicode)
        # flag whether idle by default
#         self._idle = idle
#         self._noidle = False
        self._reset()

    @classmethod
    def add_command(cls, name, callback):
        func = _create_command(cls._execute, name, callback)
        escaped_name = name.replace(" ", "_")
        setattr(cls, escaped_name, func)

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if self.debug:
            logger.info('MPDProtocol.lineReceived: {}'.format(line))
        command_list = self._state and isinstance(self._state[0], list)
        state_list = self._state[0] if command_list else self._state
        if line.startswith(HELLO_PREFIX):
            self.mpd_version = line[len(HELLO_PREFIX):].strip()

#             if self._idle:
#                 if self.debug:
#                     logger.info('MPDProtocol.lineReceived: enter idle')
#                 self.idle().addCallback(self._dispatch_idle_result)

        elif line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            if command_list:
                state_list[0].errback(CommandError(error))
                for state in state_list[1:-1]:
                    state.errback(
                        CommandListError("An earlier command failed."))
                state_list[-1].errback(CommandListError(error))
                del self._state[0]
                del self._command_list_results[0]
            else:
                state_list.pop(0).errback(CommandError(error))
        elif line == SUCCESS or (command_list and line == NEXT):
            parser = state_list.pop(0).callback(self._rcvd_lines[:])
            self._rcvd_lines = []
            if command_list and line == SUCCESS:
                del self._state[0]
        else:
            self._rcvd_lines.append(line)

    @mpd_commands(
        *MPDClientBase._parse_nothing.mpd_commands + ('noidle',))
    def _parse_nothing(self, lines):
        return

    def command_list_ok_begin(self):
        if self._command_list:
            raise CommandListError("Already in command list")
        self._write_command("command_list_ok_begin")
        self._command_list = True
        self._command_list_results.append([])
        self._state.append([])

    def command_list_end(self):
        if not self._command_list:
            raise CommandListError("Not in command list")
        self._write_command("command_list_end")
        deferred = defer.Deferred()
        deferred.addCallback(self._parse_command_list_end)
        self._state[-1].append(deferred)
        self._command_list = False
        return deferred

    def _reset(self):
        super(MPDProtocol, self)._reset()
        self.mpd_version = None
        self._command_list = False
        self._command_list_results = []
        self._rcvd_lines = []
        self._state = []

    def _execute(self, command, args, parser):
        if self._command_list and not callable(parser):
            msg = "{} not allowed in command list".format(command)
            raise CommandListError(msg)

#         if self._idle and not self._noidle:
#             self._noidle = True
#             if self.debug:
#                 logger.info('MPDProtocol._execute: enter noidle')
#             self.noidle().addCallback(self._dispatch_idle_result)

        self._write_command(command, args)
        deferred = defer.Deferred()
        (self._state[-1] \
            if self._command_list else self._state).append(deferred)
        if parser is not self.NOOP:
            deferred.addCallback(parser)
            if self._command_list:
                deferred.addCallback(self._parse_command_list_item)

#         if self._idle and not self._command_list:
#             def enter_idle(*args):
#                 if self.debug:
#                     logger.info('MPDProtocol._execute: enter idle')
#                 self.idle().addCallback(self._dispatch_idle_result)
#                 self._noidle = False
#             deferred.addCallback(enter_idle)

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

#     def _dispatch_idle_result(self, lines):
#         lines = list(lines) if lines else lines
#         logger.info('DISPATCH IDLE RESULT: {}'.format(lines))
#         if not self._noidle:
#             self.idle().addCallback(self._dispatch_idle_result)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
