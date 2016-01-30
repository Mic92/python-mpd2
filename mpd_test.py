#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import sys
import types
import warnings

import mpd

try:
    # is required for python2.6
    # python2.7 works with this module too
    import unittest2 as unittest
except ImportError:
    # required for python3
    # python2.7 works with this module too!
    if sys.version_info >= (2, 7):
        import unittest
    else:
        print("Please install unittest2 from PyPI to run tests!")
        sys.exit(1)

try:
    import mock
except ImportError:
    print("Please install mock from PyPI to run tests!")
    sys.exit(1)

# show deprecation warnings
warnings.simplefilter('default')


TEST_MPD_HOST, TEST_MPD_PORT = ('example.com', 10000)


class TestMPDClient(unittest.TestCase):

    longMessage = True

    def setUp(self):
        self.socket_patch = mock.patch("mpd.socket")
        self.socket_mock = self.socket_patch.start()
        self.socket_mock.getaddrinfo.return_value = [range(5)]

        self.socket_mock.socket.side_effect = (
            lambda *a, **kw:
            # Create a new socket.socket() mock with default attributes,
            # each time we are calling it back (otherwise, it keeps set
            # attributes across calls).
            # That's probablyy what we want, since reconnecting is like
            # reinitializing the entire connection, and so, the mock.
            mock.MagicMock(name="socket.socket"))

        self.client = mpd.MPDClient()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)
        self.client._sock.reset_mock()
        self.MPDWillReturn("ACK don't forget to setup your mock\n")

    def tearDown(self):
        self.socket_patch.stop()

    def MPDWillReturn(self, *lines):
        # Return what the caller wants first, then do as if the socket was
        # disconnected.
        self.client._rfile.readline.side_effect = itertools.chain(
            lines, itertools.repeat(''))

    def assertMPDReceived(self, *lines):
        self.client._wfile.write.assert_called_with(*lines)

    def test_metaclass_commands(self):
        # just some random functions
        self.assertTrue(hasattr(self.client, "commands"))
        self.assertTrue(hasattr(self.client, "save"))
        self.assertTrue(hasattr(self.client, "random"))
        # space should be replaced
        self.assertFalse(hasattr(self.client, "sticker get"))
        self.assertTrue(hasattr(self.client, "sticker_get"))
        # each command should have prefixe
        self.assertTrue(hasattr(self.client, "close"))
        self.assertTrue(hasattr(self.client, "fetch_close"))
        self.assertTrue(hasattr(self.client, "send_close"))

    def test_duplicate_tags(self):
        self.MPDWillReturn('Track: file1\n', 'Track: file2\n', 'OK\n')
        song = self.client.currentsong()
        self.assertIsInstance(song, dict)
        self.assertIsInstance(song["track"], list)
        self.assertMPDReceived('currentsong\n')

    def test_fetch_nothing(self):
        self.MPDWillReturn('OK\n', 'OK\n')

        self.assertIsNone(self.client.ping())
        self.assertMPDReceived('ping\n')

        self.assertIsNone(self.client.clearerror())
        self.assertMPDReceived('clearerror\n')

    def test_fetch_list(self):
        self.MPDWillReturn('OK\n')

        self.assertIsInstance(self.client.list("album"), list)
        self.assertMPDReceived('list "album"\n')

    def test_fetch_item(self):
        self.MPDWillReturn('updating_db: 42\n', 'OK\n')
        self.assertIsNotNone(self.client.update())

    def test_fetch_object(self):
        # XXX: _read_objects() doesn't wait for the final OK
        self.MPDWillReturn('volume: 63\n', 'OK\n')
        status = self.client.status()
        self.assertMPDReceived('status\n')
        self.assertIsInstance(status, dict)

        # XXX: _read_objects() doesn't wait for the final OK
        self.MPDWillReturn('OK\n')
        stats = self.client.stats()
        self.assertMPDReceived('stats\n')
        self.assertIsInstance(stats, dict)

    def test_fetch_songs(self):
        self.MPDWillReturn("file: my-song.ogg\n",
                           "Pos: 0\n",
                           "Id: 66\n",
                           "OK\n")
        playlist = self.client.playlistinfo()

        self.assertMPDReceived('playlistinfo\n')
        self.assertIsInstance(playlist, list)
        self.assertEqual(1, len(playlist))
        e = playlist[0]
        self.assertIsInstance(e, dict)
        self.assertEqual('my-song.ogg', e['file'])
        self.assertEqual('0', e['pos'])
        self.assertEqual('66', e['id'])

    def test_send_and_fetch(self):
        self.MPDWillReturn("volume: 50\n", "OK\n")
        result = self.client.send_status()
        self.assertEqual(None, result)
        self.assertMPDReceived('status\n')

        status = self.client.fetch_status()
        self.assertEqual(1, self.client._wfile.write.call_count)
        self.assertEqual({'volume': '50'}, status)

    def test_readcomments(self):
        self.MPDWillReturn("major_brand: M4V\n",
                           "minor_version: 1\n",
                           "lyrics: Lalala\n",
                           "OK\n")
        comments = self.client.readcomments()
        self.assertMPDReceived('readcomments\n')
        self.assertEqual(comments['major_brand'], "M4V")
        self.assertEqual(comments['minor_version'], "1")
        self.assertEqual(comments['lyrics'], "Lalala")

    def test_iterating(self):
        self.MPDWillReturn("file: my-song.ogg\n",
                           "Pos: 0\n",
                           "Id: 66\n",
                           "OK\n")
        self.client.iterate = True
        playlist = self.client.playlistinfo()
        self.assertMPDReceived('playlistinfo\n')
        self.assertIsInstance(playlist, types.GeneratorType)
        for song in playlist:
            self.assertIsInstance(song, dict)
            self.assertEqual('my-song.ogg', song['file'])
            self.assertEqual('0', song['pos'])
            self.assertEqual('66', song['id'])

    def test_idle(self):
        self.MPDWillReturn('OK\n')  # nothing changed after idle-ing
        self.client.idletimeout = 456
        res = self.client.idle()
        self.assertMPDReceived('idle\n')
        self.client._sock.settimeout.assert_has_calls([mock.call(456),
                                                       mock.call(None)])
        self.assertEqual([], res)

        self.client.send_idle()
        # new event
        self.MPDWillReturn('changed: update\n', 'OK\n')

        event = self.client.fetch_idle()
        self.assertEqual(event, ['update'])

    def test_noidle(self):
        self.MPDWillReturn('OK\n')  # nothing changed after idle-ing
        self.client.send_idle()
        self.MPDWillReturn('OK\n')  # nothing changed after noidle
        self.assertEqual(self.client.noidle(), [])
        self.assertMPDReceived('noidle\n')
        self.MPDWillReturn("volume: 50\n", "OK\n")
        self.client.status()
        self.assertMPDReceived('status\n')

    def test_noidle_while_idle_started_sending(self):
        self.MPDWillReturn('OK\n')  # nothing changed after idle-ing
        self.client.send_idle()
        self.MPDWillReturn('changed: player\n', 'OK\n')  # noidle response
        self.assertEqual(self.client.noidle(), ['player'])
        self.MPDWillReturn("volume: 50\n", "OK\n")
        status = self.client.status()
        self.assertEqual({'volume': '50'}, status)

    def test_throw_when_calling_noidle_withoutidling(self):
        self.assertRaises(mpd.CommandError, self.client.noidle)
        self.client.send_status()
        self.assertRaises(mpd.CommandError, self.client.noidle)

    def test_add_and_remove_command(self):
        self.MPDWillReturn("ACK awesome command\n")

        self.client.add_command("awesome command",
                                mpd.MPDClient._fetch_nothing)
        self.assertTrue(hasattr(self.client, "awesome_command"))
        self.assertTrue(hasattr(self.client, "send_awesome_command"))
        self.assertTrue(hasattr(self.client, "fetch_awesome_command"))
        # should be unknown by mpd
        self.assertRaises(mpd.CommandError, self.client.awesome_command)

        self.client.remove_command("awesome_command")
        self.assertFalse(hasattr(self.client, "awesome_command"))
        self.assertFalse(hasattr(self.client, "send_awesome_command"))
        self.assertFalse(hasattr(self.client, "fetch_awesome_command"))

        # remove non existing command
        self.assertRaises(ValueError, self.client.remove_command,
                          "awesome_command")

    def test_client_to_client(self):
        # client to client is at this time in beta!

        self.MPDWillReturn('OK\n')
        self.assertIsNone(self.client.subscribe("monty"))
        self.assertMPDReceived('subscribe "monty"\n')

        self.MPDWillReturn('channel: monty\n', 'OK\n')
        channels = self.client.channels()
        self.assertMPDReceived('channels\n')
        self.assertEqual(["monty"], channels)

        self.MPDWillReturn('OK\n')
        self.assertIsNone(self.client.sendmessage("monty", "SPAM"))
        self.assertMPDReceived('sendmessage "monty" "SPAM"\n')

        self.MPDWillReturn('channel: monty\n', 'message: SPAM\n', 'OK\n')
        msg = self.client.readmessages()
        self.assertMPDReceived('readmessages\n')
        self.assertEqual(msg, [{"channel": "monty", "message": "SPAM"}])

        self.MPDWillReturn('OK\n')
        self.assertIsNone(self.client.unsubscribe("monty"))
        self.assertMPDReceived('unsubscribe "monty"\n')

        self.MPDWillReturn('OK\n')
        channels = self.client.channels()
        self.assertMPDReceived('channels\n')
        self.assertEqual([], channels)

    def test_unicode_as_command_args(self):
        if sys.version_info < (3, 0):
            self.MPDWillReturn("OK\n")
            res = self.client.find("file", unicode("☯☾☝♖✽", 'utf-8'))
            self.assertIsInstance(res, list)
            self.assertMPDReceived('find "file" "☯☾☝♖✽"\n')

            self.MPDWillReturn("OK\n")
            res2 = self.client.find("file", "☯☾☝♖✽")
            self.assertIsInstance(res2, list)
            self.assertMPDReceived('find "file" "☯☾☝♖✽"\n')
        else:
            self.MPDWillReturn("OK\n")
            res = self.client.find("file", "☯☾☝♖✽")
            self.assertIsInstance(res, list)
            self.assertMPDReceived('find "file" "☯☾☝♖✽"\n')

    @unittest.skipIf(sys.version_info >= (3, 0),
                     "Test special unicode handling only if python2")
    def test_unicode_as_reponse(self):
        self.MPDWillReturn("handler: http://\n", "OK\n")
        self.client.use_unicode = True
        self.assertIsInstance(self.client.urlhandlers()[0], unicode)

        self.MPDWillReturn("handler: http://\n", "OK\n")
        self.client.use_unicode = False
        self.assertIsInstance(self.client.urlhandlers()[0], str)

    def test_numbers_as_command_args(self):
        self.MPDWillReturn("OK\n")
        self.client.find("file", 1)
        self.assertMPDReceived('find "file" "1"\n')

    def test_commands_without_callbacks(self):
        self.MPDWillReturn("\n")
        self.client.close()
        self.assertMPDReceived('close\n')

        # XXX: what are we testing here?
        self.client._reset()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)

    def test_set_timeout_on_client(self):
        self.client.timeout = 1
        self.client._sock.settimeout.assert_called_with(1)
        self.assertEqual(self.client.timeout, 1)

        self.client.timeout = None
        self.client._sock.settimeout.assert_called_with(None)
        self.assertEqual(self.client.timeout, None)

    def test_set_timeout_from_connect(self):
        self.client.disconnect()
        with warnings.catch_warnings(record=True) as w:
            self.client.connect("example.com", 10000, timeout=5)
            self.client._sock.settimeout.assert_called_with(5)
            self.assertEqual(len(w), 1)
            self.assertIn('Use MPDClient.timeout', str(w[0].message))

    def test_connection_lost(self):
        # Simulate a connection lost: the socket returns empty strings
        self.MPDWillReturn('')

        with self.assertRaises(mpd.ConnectionError):
            self.client.status()

        # consistent behaviour, solves bug #11 (github)
        with self.assertRaises(mpd.ConnectionError):
            self.client.status()

        self.assertIs(self.client._sock, None)

    @unittest.skipIf(sys.version_info < (3, 0),
                     "Automatic decoding/encoding from the socket is only "
                     "available in Python 3")
    def test_force_socket_encoding_to_utf8(self):
        # Force the reconnection to refill the mock
        self.client.disconnect()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)
        self.assertEqual([mock.call('r', encoding="utf-8", newline="\n"),
                          mock.call('w', encoding="utf-8", newline="\n")],
                         # We are onlyy interested into the 2 first entries,
                         # otherwise we get all the readline() & co...
                         self.client._sock.makefile.call_args_list[0:2])

    def test_ranges_as_argument(self):
        self.MPDWillReturn('OK\n')
        self.client.move((1, 2), 2)
        self.assertMPDReceived('move "1:2" "2"\n')

        self.MPDWillReturn('OK\n')
        self.client.move((1,), 2)
        self.assertMPDReceived('move "1:" "2"\n')

        # old code still works!
        self.MPDWillReturn('OK\n')
        self.client.move("1:2", 2)
        self.assertMPDReceived('move "1:2" "2"\n')

        # empty ranges
        self.MPDWillReturn('OK\n')
        self.client.rangeid(1, ())
        self.assertMPDReceived('rangeid "1" ":"\n')

        with self.assertRaises(ValueError):
            self.MPDWillReturn('OK\n')
            self.client.move((1, "garbage"), 2)
            self.assertMPDReceived('move "1:" "2"\n')

    def test_read_stickers(self):
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client._read_stickers()
        self.assertEqual([('foo', 'bar')], list(res))

        self.MPDWillReturn("sticker: foo=bar\n", "sticker: l=b\n", "OK\n")
        res = self.client._read_stickers()
        self.assertEqual([('foo', 'bar'), ('l', 'b')], list(res))

    def test_fetch_database(self):
        self.MPDWillReturn('directory: foo\n',
                           'Last-Modified: 2014-01-23T16:42:46Z\n',
                           'file: bar.mp3\n',
                           'size: 59618802\n',
                           'Last-Modified: 2014-11-02T19:57:00Z\n',
                           'OK\n')
        self.client.listfiles("/")

    def test_read_sticker_with_special_value(self):
        self.MPDWillReturn("sticker: foo==uv=vu\n", "OK\n")
        res = self.client._read_stickers()
        self.assertEqual([('foo', '=uv=vu')], list(res))

    def test_parse_sticket_get_one(self):
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client.sticker_get('song', 'baz', 'foo')
        self.assertEqual('bar', res)

    def test_parse_sticket_get_no_sticker(self):
        self.MPDWillReturn("ACK [50@0] {sticker} no such sticker\n")
        self.assertRaises(mpd.CommandError,
                          self.client.sticker_get, 'song', 'baz', 'foo')

    def test_parse_sticker_list(self):
        self.MPDWillReturn("sticker: foo=bar\n", "sticker: lom=bok\n", "OK\n")
        res = self.client.sticker_list('song', 'baz')
        self.assertEqual({'foo': 'bar', 'lom': 'bok'}, res)

        # Even with only one sticker, we get a dict
        self.MPDWillReturn("sticker: foo=bar\n", "OK\n")
        res = self.client.sticker_list('song', 'baz')
        self.assertEqual({'foo': 'bar'}, res)

if __name__ == '__main__':
    unittest.main()
