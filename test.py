#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import types
import sys
from socket import error as SocketError
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
        print("Please install unittest2 from pypi to run tests!")
        sys.exit(1)

def setup_environment():
    # Alternate this to your setup
    # Make sure you have at least one song on your playlist
    global TEST_MPD_HOST, TEST_MPD_PORT, TEST_MPD_PASSWORD

    if 'TEST_MPD_PORT' not in os.environ:
        sys.stderr.write(
            "You should set the TEST_MPD_PORT environment variable to point "
            "to your test MPD running instance.\n")
        sys.exit(255)

    TEST_MPD_HOST     = os.environ.get('TEST_MPD_HOST', "localhost")
    TEST_MPD_PORT     = int(os.environ['TEST_MPD_PORT'])
    TEST_MPD_PASSWORD = os.environ.get('TEST_MPD_PASSWORD')

setup_environment()


class TestMPDClient(unittest.TestCase):

    longMessage = True

    @classmethod
    def setUpClass(self):
        global TEST_MPD_HOST, TEST_MPD_PORT, TEST_MPD_PASSWORD
        self.client = mpd.MPDClient()
        self.idleclient = mpd.MPDClient()
        try:
            self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT)
            self.idleclient.connect(TEST_MPD_HOST, TEST_MPD_PORT)
            self.commands = self.client.commands()
        except SocketError as e:
            raise Exception("Can't connect mpd! Start it or check the configuration: %s" % e)
        if TEST_MPD_PASSWORD != None:
            try:
                self.client.password(TEST_MPD_PASSWORD)
                self.idleclient.password(TEST_MPD_PASSWORD)
            except mpd.CommandError as e:
                raise Exception("Fail to authenticate to mpd.")
    @classmethod
    def tearDownClass(self):
        self.client.disconnect()
        self.idleclient.disconnect()
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
    def test_fetch_nothing(self):
        self.assertIsNone(self.client.ping())
        self.assertIsNone(self.client.clearerror())
    def test_fetch_list(self):
        self.assertIsInstance(self.client.list("album"), list)
    def test_fetch_item(self):
        self.assertIsNotNone(self.client.update())
    def test_fetch_object(self):
        status = self.client.status()
        stats = self.client.stats()
        self.assertIsInstance(status, dict)
        # some keys should be there
        self.assertIn("volume", status)
        self.assertIn("song", status)
        self.assertIsInstance(stats, dict)
        self.assertIn("artists", stats)
        self.assertIn("uptime", stats)
    def test_fetch_songs(self):
        playlist = self.client.playlistinfo()
        self.assertTrue(type(playlist) is list)
        if len(playlist) > 0:
                self.assertIsInstance(playlist[0], dict)
    def test_send_and_fetch(self):
        self.client.send_status()
        self.client.fetch_status()
    def test_iterating(self):
        self.client.iterate = True
        playlist = self.client.playlistinfo()
        self.assertIsInstance(playlist, types.GeneratorType)
        for song in playlist:
                self.assertIsInstance(song, dict)
        self.client.iterate = False
    def test_idle(self):
        # clean event mask
        self.idleclient.idle()

        self.idleclient.send_idle()
        # new event
        self.client.update()
        event = self.idleclient.fetch_idle()
        self.assertEqual(event, ['update'])
    def test_add_and_remove_command(self):
        self.client.add_command("awesome command", mpd.MPDClient._fetch_nothing)
        self.assertTrue(hasattr(self.client, "awesome_command"))
        self.assertTrue(hasattr(self.client, "send_awesome_command"))
        self.assertTrue(hasattr(self.client, "fetch_awesome_command"))
        # should be unknown by mpd
        with self.assertRaises(mpd.CommandError):
            self.client.awesome_command()
        self.client.remove_command("awesome_command")
        self.assertFalse(hasattr(self.client, "awesome_command"))
        self.assertFalse(hasattr(self.client, "send_awesome_command"))
        self.assertFalse(hasattr(self.client, "fetch_awesome_command"))
        # remove non existing command
        self.assertRaises(ValueError, self.client.remove_command,
                          "awesome_command")
    def test_client_to_client(self):
        # client to client is at this time in beta!
        if not "channels" in self.client.commands():
            return
        self.assertIsNone(self.client.subscribe("monty"))
        channels = self.client.channels()
        self.assertIn("monty", channels)

        self.assertIsNone(self.client.sendmessage("monty", "SPAM"))
        msg = self.client.readmessages()
        self.assertEqual(msg, [{"channel":"monty", "message": "SPAM"}])

        self.assertIsNone(self.client.unsubscribe("monty"))
        channels = self.client.channels()
        self.assertNotIn("monty", channels)

    def test_commands_list(self):
        """
        Test if all implemented commands are valid
        and all avaible commands are implemented.
        This test may fail, if a implement command isn't
        avaible on older versions of mpd
        """
        avaible_cmds = set(self.client.commands() + self.client.notcommands())
        imple_cmds   = set(mpd._commands.keys())
        sticker_cmds = set(["sticker get", "sticker set", "sticker delete",
                        "sticker list", "sticker find"])
        imple_cmds = (imple_cmds - sticker_cmds)
        imple_cmds.add("sticker")
        imple_cmds.remove("noidle")

        self.assertEqual(set(), avaible_cmds - imple_cmds,
                         "Not all commands supported by mpd are implemented!")

        long_desc = (
            "Not all commands implemented by this library are supported by "
            "the current mpd.\n"  +
            "This either means the command list is wrong or mpd is not "
            "up-to-date.")

        self.assertEqual(set(), imple_cmds - avaible_cmds, long_desc)

    def test_unicode_as_command_args(self):
        if sys.version_info < (3, 0):
            raw_unicode = "☯☾☝♖✽".decode("utf-8")
            res = self.client.find("file", raw_unicode)
            self.assertIsInstance(res, list)

            encoded_str = "☯☾☝♖✽"
            res2 = self.client.find("file", encoded_str)
            self.assertIsInstance(res2, list)
        else:
            res = self.client.find("file","☯☾☝♖✽")
            self.assertIsInstance(res, list)

    @unittest.skipIf(sys.version_info >= (3, 0),
                     "Test special unicode handling only if python2")
    def test_unicode_as_reponse(self):
        self.client.use_unicode = True
        self.assertIsInstance(self.client.urlhandlers()[0], unicode)
        self.client.use_unicode = False
        self.assertIsInstance(self.client.urlhandlers()[0], str)

    def test_numbers_as_command_args(self):
        res = self.client.find("file", 1)

    def test_timeout(self):
        self.client.disconnect()
        self.client.connect(TEST_MPD_HOST, TEST_MPD_PORT, timeout=5)
        self.assertEqual(self.client._sock.gettimeout(), 5)

if __name__ == '__main__':
    unittest.main()
