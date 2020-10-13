#!/usr/bin/python
import mpd

# use_unicode will enable the utf-8 mode for python2
# see https://python-mpd2.readthedocs.io/en/latest/topics/advanced.html#unicode-handling
client = mpd.MPDClient(use_unicode=True)
client.connect("localhost", 6600)

withalbumart = list(client.albumart("ji/intro.mp3"))
print("albumart:",withalbumart)
nocoverfile = list(client.readpicture("nocoverfile/intro.mp3"))
print("readpicture", nocoverfile)
notfound = list(client.readpicture("nocover/file.mp3"))
print("readpicture, no data",notfound)

for entry in client.lsinfo("/"):
    print("%s" % entry)
for key, value in client.status().items():
    print("%s: %s" % (key, value))
