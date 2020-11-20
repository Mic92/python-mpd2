Future Compatible
-----------------

New commands or special handling of commands can be easily implemented.  Use
``add_command()`` or ``remove_command()`` to modify the commands of the
*MPDClient* class and all its instances.::

    def fetch_cover(client):
        """"Take a MPDClient instance as its arguments and return mimetype and image"""
        # this command may come in the future.
        pass

    client.add_command("get_cover", fetch_cover)
    # you can then use:
    client.get_cover()

    # remove the command, because it doesn't exist already.
    client.remove_command("get_cover")


Thread-Safety
-------------

Currently ``MPDClient`` is **NOT** thread-safe. As it use a socket internaly,
only one thread can send or receive at the time.

But ``MPDClient`` can be easily extended to be thread-safe using `locks
<http://docs.python.org/library/threading.html#lock-objects>`__.  Take a look at
``examples/locking.py`` for further informations.


Unicode Handling
----------------

To quote the `mpd protocol documentation
<https://www.musicpd.org/doc/protocol/request_syntax.html>`_:

> All data between the client and the server is encoded in UTF-8.

With Python 3:
~~~~~~~~~~~~~~

In Python 3, Unicode string is the default string type. So just pass these
strings as arguments for MPD commands and *python-mpd2* will also return such
Unicode string.
