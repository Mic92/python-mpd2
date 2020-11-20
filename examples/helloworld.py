#!/usr/bin/python
import mpd

client = mpd.MPDClient()
client.connect("localhost", 6600)

for entry in client.lsinfo("/"):
    print("%s" % entry)
for key, value in client.status().items():
    print("%s: %s" % (key, value))
