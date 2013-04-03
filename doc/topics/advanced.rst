Future Compatible
-----------------

New commands or special handling of commands can be easily implemented.  Use
``add_command()`` or ``remove_command()`` to modify the commands of the
*MPDClient* class and all its instances.::

    def fetch_cover(client):
        """"Take a MPDClient instance as its arguments and return mimetype and image"""
        # this command may come in the future.
        pass

    self.client.add_command("get_cover", fetch_cover)
    # you can then use:
    self.client.fetch_cover()

    # remove the command, because it doesn't exist already.
    self.client.remove_command("get_cover")


Thread-Safety
-------------

Currently ``MPDClient`` is **NOT** thread-safe. As it use a socket internaly,
only one thread can send or receive at the time.

But ``MPDClient`` can be easily extended to be thread-safe using `locks
<http://docs.python.org/library/threading.html#lock-objects>`__.  Take a look at
``examples/locking.py`` for further informations.


Unicode Handling
----------------

To quote the mpd protocol documentation:

> All data to be sent between the client and server must be encoded in UTF-8.

With Python 3:
~~~~~~~~~~~~~~

In Python 3, Unicode string is the default string type. So just pass these
strings as arguments for MPD commands and *python-mpd2* will also return such
Unicode string.

With Python 2.x
~~~~~~~~~~~~~~~

For backward compatibility with *python-mpd*, when running with Python 2.x,
*python-mpd2* accepts both Unicode strings (ex. u"♥") and UTF-8 encoded strings
(ex. "♥").

In order for *MPDClient* to return Unicode strings with Python 2, create the
instance with the ``use_unicode`` parameter set to ``True``.

Using Unicode strings should be prefered as it is done transparently by the
library for you, and makes the transition to Python 3 easier::

    >>> import mpd
    >>> client = MPDClient(use_unicode=True)
    >>> client.urlhandlers()[0]
    u'http'
    >>> client.use_unicode = False # Can be switched back later
    >>> client.urlhandlers()[0]
    'http'

Using this option in Python 3 doesn't have any effect.
