from threading import Lock, Thread
from random import choice
from mpd import MPDClient

class LockableMPDClient(MPDClient):
    def __init__(self, use_unicode=False):
        super(LockableMPDClient, self).__init__()
        self.use_unicode = use_unicode
        self._lock = Lock()
    def acquire(self):
        self._lock.acquire()
    def release(self):
        self._lock.release()
    def __enter__(self):
        self.acquire()
    def __exit__(self, type, value, traceback):
        self.release()

client = LockableMPDClient()
client.connect("localhost", 6600)
# now whenever you need thread-safe access
# use the 'with' statement like this:
with client: # acquire lock
    status = client.status()
# if you leave the block, the lock is released
# it is recommend to leave it soon,
# otherwise your other threads will blocked.

# Let's test if it works ....
def fetch_playlist():
    for i in range(10):
        if choice([0, 1]) == 0:
            with client:
                song = client.currentsong()
            assert isinstance(song, dict)
        else:
            with client:
                playlist = client.playlist()
            assert isinstance(playlist, list)

threads = []
for i in range(5):
    t = Thread(target=fetch_playlist)
    threads.append(t)
    t.start()
for t in threads:
    t.join()

print("Done...")
