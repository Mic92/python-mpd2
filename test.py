#!/usr/bin/env python
import unittest
from mpd import MPDClient, CommandError

# Alternate this to your setup
# Make sure you have at least one song on your playlist
MPD_HOST = "localhost"
MPD_PORT = 6600

class TestMPDClient(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.client = MPDClient()
        self.idleclient = MPDClient()
        self.client.connect(MPD_HOST, MPD_PORT)
        self.idleclient.connect(MPD_HOST, MPD_PORT)
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
        self.assertTrue(type(self.client.list("album")) == list)
    def test_fetch_item(self):
        self.assertIsNotNone(self.client.update())
    def test_fetch_object(self):
        status = self.client.status()
        stats = self.client.stats()
        self.assertTrue(type(status) is dict)
        # some keys should be there
        self.assertTrue("volume" in status)
        self.assertTrue("song" in status)
        self.assertTrue(type(stats) is dict)
        self.assertTrue("artists" in stats)
        self.assertTrue("uptime" in stats)
    def test_fetch_songs(self):
        playlist = self.client.playlistinfo()
        self.assertTrue(type(playlist) is list)
        if len(playlist) > 0:
                self.assertTrue(type(playlist[0]) is dict)
    def test_send_and_fetch(self):
        self.client.send_status()
        self.client.fetch_status()
    def test_idle(self):
        self.idleclient.send_idle()
        self.client.update()
        event = self.idleclient.fetch_idle()
        self.assertEqual(event, ['update'])
    def test_add_and_remove_command(self):
        self.client.add_command("awesome command", MPDClient._fetch_nothing)
        self.assertTrue(hasattr(self.client, "awesome_command"))
        self.assertTrue(hasattr(self.client, "send_awesome_command"))
        self.assertTrue(hasattr(self.client, "fetch_awesome_command"))
        # should be unknown by mpd
        with self.assertRaises(CommandError):
            self.client.awesome_command()
        self.client.remove_command("awesome_command")
        self.assertFalse(hasattr(self.client, "awesome_command"))
        self.assertFalse(hasattr(self.client, "send_awesome_command"))
        self.assertFalse(hasattr(self.client, "fetch_awesome_command"))

if __name__ == '__main__':
    unittest.main()
