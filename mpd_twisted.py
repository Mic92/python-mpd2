from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols import basic
import mpd


"""
Callbacks

changes       _fetch_changes, parse_changes
database      _fetch_database, parse_database
idle          _fetch_idle
item          _fetch_item, parse_item
list          _fetch_list, parse_list
messages      _fetch_messages
mounts        _fetch_mounts
neighbors     _fetch_neighbors
nothing       _fetch_nothing, parse_nothing
object        _fetch_object, parse_object
outputs       _fetch_outputs, parse_outputs
playlist      _fetch_playlist
playlists     _fetch_playlists, parse_playlists
plugins       _fetch_plugins, parse_decoders
songs         _fetch_songs, parse_songs
sticker       _fetch_sticker, parse_sticker
stickers      _fetch_stickers, parse_stickers
"""


def mpd_command_provider(cls):
    """Decorator for MPD command providing class.
    """
    cls._command_callbacks = dict()
    for name, ob in cls.__dict__.iteritems():
        if hasattr(ob, "mpd_commands"):
            for command in ob.mpd_commands:
                cls._command_callbacks[command] = ob
    return cls


class mpd_commands(object):
    """Decorator for registering MPD command callbacks.
    """

    def __init__(self, *commands):
        self.commands = commands

    def __call__(self, ob):
        ob.mpd_commands = self.commands
        return ob


class Noop(object):
    mpd_commands = None


@mpd_command_provider
class MPDProtocol(basic.LineReceiver, mpd.MPDClientBase):
    debug = False
    delimiter = "\n"

    def __init__(self, use_unicode=False):
        super(MPDProtocol, self).__init__(use_unicode=use_unicode)
        self.iterate = True

    def __getattr__(self, attr):
        attr = attr.replace("_", " ")
        try:
            return lambda *args: self._execute(attr, args, self.commands[attr])
        except KeyError:
            msg = "'{}' object has no attribute '{}'".format(
                self.__class__.__name__, attr)
            raise AttributeError(msg)

    def _execute(self, command, args, parser):
        if self.command_list and not callable(parser):
            msg = "{} not allowed in command list".format(command)
            raise CommandListError(msg)
        self._write_command(command, args)
        deferred = defer.Deferred()
        (self.state[-1] if self.command_list else self.state).append(deferred)
        if parser is not None:
            deferred.addCallback(parser)
            if self.command_list:
                deferred.addCallback(self.parse_command_list_item)
        return deferred

    def _write_command(self, command, args=[]):
        parts = [command]
        parts += ['"{}"'.format(escape(arg.encode('utf-8')) \
            if isinstance(arg, unicode) else str(arg)) for arg in args]
        cmd = " ".join(parts)
        if self.debug:
            logger.info('MPDProtocol._write_command: {}'.format(cmd))
        self.sendLine(cmd)

    #@iterator_wrapper
    def parse_pairs(self, lines, separator=": "):
        return (line.split(separator, 1) for line in lines)

    #@iterator_wrapper
    def parse_list(self, lines):
        seen = None
        for key, value in self.parse_pairs(lines):
            if key != seen:
                if seen is not None:
                    raise ProtocolError("Expected key '%s', got '%s'" %
                                        (seen, key))
                seen = key
            yield value

    #@iterator_wrapper
    def parse_playlist(self, lines):
        for key, value in self.read_pairs(lines, ":"):
            yield value

    #@iterator_wrapper
    def parse_objects(self, lines, delimiters=[]):
        obj = {}
        for key, value in self.parse_pairs(lines):
            key = key.lower()
            if key in delimiters and obj:
                yield obj
                obj = {}
            if key in obj:
                if not isinstance(obj[key], list):
                    obj[key] = [obj[key], value]
                else:
                    obj[key].append(value)
            else:
                obj[key] = value
        if obj:
            yield obj

    def parse_object(self, lines):
        objs = list(self.parse_objects(lines))
        if not objs:
            return {}
        return objs[0]

    def parse_item(self, lines):
        pairs = list(self.parse_pairs(lines))
        if len(pairs) != 1:
            return
        return pairs[0][1]

    def parse_nothing(self, lines):
        return

    def parse_songs(self, lines):
        return self.parse_objects(lines, ["file"])

    def parse_playlists(self, lines):
        return self.parse_objects(lines, ["playlist"])

    def parse_database(self, lines):
        return self.parse_objects(lines, ["file", "directory", "playlist"])

    def parse_outputs(self, lines):
        return self.parse_objects(lines, ["outputid"])

    def parse_changes(self, lines):
        return self.parse_objects(lines, ["cpos"])

    def parse_decoders(self, lines):
        return self.parse_objects(lines, ["plugin"])

    def parse_sticker(self, lines):
        return self.parse_item(lines).split("=", 1)[1]

    def parse_stickers(self, lines):
        return dict(x.split("=", 1) for x in self.parse_list(lines))

    #@iterator_wrapper
    def parse_stickers_find(self, lines):
        for x in self.parse_objects(lines, ["file"]):
            x["sticker"] = x["sticker"].split("=", 1)[1]
            yield x

    def parse_command_list_item(self, result):
        # TODO: find a better way to do this
        if type(result) == GeneratorType:
            result = list(result)
        self.command_list_results[0].append(result)
        return result

    def parse_command_list_end(self, lines):
        return self.command_list_results.pop(0)

    def noidle(self):
        if not self._pending or self._pending[0] != 'idle':
            msg = 'cannot send noidle if send_idle was not called'
            raise CommandError(msg)
        del self._pending[0]
        self._write_command("noidle")
        return self._fetch_list()

    def command_list_ok_begin(self):
        if self.command_list:
            raise CommandListError("Already in command list")
        self._write_command("command_list_ok_begin")
        self.command_list = True
        self.command_list_results.append([])
        self.state.append([])

    def command_list_end(self):
        if not self.command_list:
            raise CommandListError("Not in command list")
        self._write_command("command_list_end")
        deferred = defer.Deferred()
        deferred.addCallback(self.parse_command_list_end)
        self.state[-1].append(deferred)
        self.command_list = False
        return deferred

    def reset(self):
        self.mpd_version = None
        self.command_list = False
        self.command_list_results = []
        self.buffer = []
        self.state = []

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if self.debug:
            logger.info('MPDProtocol.lineReceived: {}'.format(line))
        command_list = self.state and isinstance(self.state[0], list)
        state_list = self.state[0] if command_list else self.state
        if line.startswith(HELLO_PREFIX):
            self.mpd_version = line[len(HELLO_PREFIX):].strip()
        elif line.startswith(ERROR_PREFIX):
            error = line[len(ERROR_PREFIX):].strip()
            if command_list:
                state_list[0].errback(CommandError(error))
                for state in state_list[1:-1]:
                    state.errback(
                        CommandListError("An earlier command failed."))
                state_list[-1].errback(CommandListError(error))
                del self.state[0]
                del self.command_list_results[0]
            else:
                state_list.pop(0).errback(CommandError(error))
        elif line == SUCCESS or (command_list and line == NEXT):
            parser = state_list.pop(0).callback(self.buffer[:])
            self.buffer = []
            if command_list and line == SUCCESS:
                del self.state[0]
        else:
            self.buffer.append(line)

    NOOP = mpd_commands('close', 'kill')(Noop())

    @mpd_commands('plchangesposid')
    def _receive_changes(self):
        if self.debug:
            msg = "``MPDProtocol._receive_changes`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('listall', 'listallinfo', 'listfiles', 'lsinfo')
    def _receive_database(self):
        if self.debug:
            msg = "``MPDProtocol._receive_database`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('idle')
    def _receive_idle(self):
        if self.debug:
            msg = "``MPDProtocol._receive_idle`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('addid', 'config', 'replay_gain_status', 'rescan', 'update')
    def _receive_item(self):
        if self.debug:
            msg = "``MPDProtocol._receive_item`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands(
        'channels', 'commands', 'list', 'listplaylist', 'notcommands',
        'tagtypes', 'urlhandlers')
    def _receive_list(self):
        if self.debug:
            msg = "``MPDProtocol._receive_list`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('readmessages')
    def _receive_messages(self):
        if self.debug:
            msg = "``MPDProtocol._receive_messages`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('listmounts')
    def _receive_mounts(self):
        if self.debug:
            msg = "``MPDProtocol._receive_mounts`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('listneighbors')
    def _receive_neighbors(self):
        if self.debug:
            msg = "``MPDProtocol._receive_neighbors`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands(
        'add', 'addtagid', 'clear', 'clearerror', 'cleartagid', 'consume',
        'crossfade', 'delete', 'deleteid', 'disableoutput', 'enableoutput',
        'findadd', 'load', 'mixrampdb', 'mixrampdelay', 'mount', 'move', 
        'moveid', 'next', 'password', 'pause', 'ping', 'play', 'playid', 
        'playlistadd', 'playlistclear', 'playlistdelete', 'playlistmove',
        'previous', 'prio', 'prioid', 'random', 'rangeid', 'rename', 'repeat',
        'replay_gain_mode', 'rm', 'save', 'searchadd', 'searchaddpl', 'seek',
        'seekcur', 'seekid', 'sendmessage', 'setvol', 'shuffle', 'single', 
        'sticker delete', 'sticker set', 'stop', 'subscribe', 'swap', 'swapid',
        'toggleoutput', 'umount', 'unsubscribe')
    def _receive_nothing(self):
        if self.debug:
            msg = "``MPDProtocol._receive_nothing`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('count', 'currentsong', 'readcomments', 'stats', 'status')
    def _receive_object(self):
        if self.debug:
            msg = "``MPDProtocol._receive_object`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('outputs')
    def _receive_outputs(self):
        if self.debug:
            msg = "``MPDProtocol._receive_outputs`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('playlist')
    def _receive_playlist(self):
        if self.debug:
            msg = "``MPDProtocol._receive_playlist`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('listplaylists')
    def _receive_playlists(self):
        if self.debug:
            msg = "``MPDProtocol._receive_playlists`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('decoders')
    def _receive_plugins(self):
        if self.debug:
            msg = "``MPDProtocol._receive_plugins`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands(
        'find', 'listplaylistinfo', 'playlistfind', 'playlistid',
        'playlistinfo', 'playlistsearch', 'plchanges', 'search', 'sticker find')
    def _receive_songs(self):
        if self.debug:
            msg = "``MPDProtocol._receive_songs`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('sticker get')
    def _receive_sticker(self):
        if self.debug:
            msg = "``MPDProtocol._receive_sticker`` triggered"
            logger.debug(msg)
        pass

    @mpd_commands('sticker list')
    def _receive_stickers(self):
        if self.debug:
            msg = "``MPDProtocol._receive_stickers`` triggered"
            logger.debug(msg)
        pass

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
