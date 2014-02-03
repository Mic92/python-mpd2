#idle command
#
#cf. official documentation for further details:
#
#http://www.musicpd.org/doc/protocol/ch02.html#id525963
#Example
from select import select

client.send_idle()
# do this periodically, e.g. in event loop
canRead = select([client], [], [], 0)[0]
if canRead:
    changes = client.fetch_idle()
    print(changes) # handle changes
    client.send_idle() # continue idling

#You can also poll the socket FD (returned by client.fileno(), which is called by default by select, poll, etc.) using other tools too.

#For example, with glib/gobject:

def callback(source, condition):
   changes = client.fetch_idle()
   print(changes)
   return False  # removes the IO watcher

client.send_idle()
gobject.io_add_watch(client, gobject.IO_IN, callback)
gobject.MainLoop().run()
