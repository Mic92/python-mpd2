#!/usr/bin/python
import mpd

# use_unicode will enable the utf-8 mode for python2
# see https://python-mpd2.readthedocs.io/en/latest/topics/advanced.html#unicode-handling
client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

for entry in client.lsinfo("/"):
    print("%s" % entry)
for key, value in client.status().items():
    print("%s: %s" % (key, value))
