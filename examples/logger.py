import logging, mpd
logging.basicConfig(level=logging.DEBUG)
client = mpd.MPDClient()
client.connect("localhost", 6600)
client.find("any", "house")
