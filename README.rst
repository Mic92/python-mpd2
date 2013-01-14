python-mpd2
===========

.. image:: https://travis-ci.org/Mic92/python-mpd2.png?branch=master
    :target: http://travis-ci.org/Mic92/python-mpd2
    :alt: Build Status

*python-mpd2* is a Python library which provides a client interface for
the `Music Player Daemon <http://musicpd.org>`_.

Difference with python-mpd
--------------------------

python-mpd2 is a fork of
`python-mpd <http://jatreuman.indefero.net/p/python-mpd/>`_. 
python-mpd2 is a fork of `python-mpd`_. While 0.4.x was backwards compatible
with python-mpd, starting with 0.5 provides enhanced features
which are *NOT* backward compatibles with the original `python-mpd`_ package.
(see PORTING.txt for more information)

The following features were added:

-  Python 3 support (but you neead at least Python 2.6)
-  support for the upcoming client-to-client protocol
-  support for new commands from MPD v0.17 (seekcur, prio, prioid,
   config, searchadd, searchaddpl)
-  remove deprecated commands (volume)
-  explicitly declared MPD commands (which is handy when using for
   example `IPython <http://ipython.org>`_)
-  a test suite
-  API documentation to add new commands (see `Future
   Compatible <#future-compatible>`_)
-  support for Unicode strings in all commands (optionally in python2,
   default in python3 - see `Unicode Handling <#unicode-handling>`_)
-  configureable timeouts
-  support for `logging <#logging>`_
-  improved support for sticker

If you like this module, you could try contact the original author
jat@spatialrift.net or join the discussion on the `issue
tracker <http://jatreuman.indefero.net/p/python-mpd/issues/7/>`_ so that
it gets merged upstream.

Getting the latest source code
------------------------------

If you would like to use the latest source code, you can grab a
copy of the development version from Git by running the command::

    $ git clone git://github.com/Mic92/python-mpd2.git

Installing from source
----------------------

To install *python-mpd2* from source, simply run the command::

    $ python setup.py install

You can use the *--help* switch to *setup.py* for a complete list of
commands and their options. See the `Installing Python
Modules <http://docs.python.org/inst/inst.html>`_ document for more
details.

Getting the latest release
--------------------------

The latest stable release of *python-mpd2* can be found on
`PyPI <http://pypi.python.org/pypi?:action=display&name=python-mpd2>`_

PyPI:
~~~~~

::

    $ pip install python-mpd2

Until Linux distributions adapt this package, here are some ready to use
packages to test your applications:

Debian
~~~~~~

Drop this line in */etc/apt/sources.list.d/python-mpd2.list*::

    deb http://sima.azylum.org/debian unstable main

Import the gpg key as root::

    $ wget -O - http://sima.azylum.org/sima.gpg | apt-key add -

Key fingerprint::

    2255 310A D1A2 48A0 7B59  7638 065F E539 32DC 551D

Controls with *apt-key finger*.

Then simply update/install *python-mpd2* or *python3-mpd* with apt or
aptitude:

Arch Linux
~~~~~~~~~~

Install `python-mpd2 <http://aur.archlinux.org/packages.php?ID=59276>`_
from AUR.

Gentoo Linux
~~~~~~~~~~~~

Replaces the original python-mpd beginning with version 0.4.2::

    echo dev-python/python-mpd >> /etc/portage/accept_keywords
    emerge -av python-mpd

Packages for other distributions are welcome!

Using the client library
------------------------

The client library can be used as follows::

    client = mpd.MPDClient()           # create client object
    client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    client.connect("localhost", 6600)  # connect to localhost:6600
    print(client.mpd_version)          # print the MPD version
    print(client.find("any", "house")) # print result of the command "find any house"
    client.close()                     # send the close command
    client.disconnect()                # disconnect from the server

A list of supported commands, their arguments (as MPD currently
understands them), and the functions used to parse their responses can
be found in *doc/commands.txt*. See the `MPD protocol
documentation <http://www.musicpd.org/doc/protocol/>`_ for more details.

Command lists are also supported using *command\_list\_ok\_begin()* and
*command\_list\_end()*::

    client.command_list_ok_begin()       # start a command list
    client.update()                      # insert the update command into the list
    client.status()                      # insert the status command into the list
    results = client.command_list_end()  # results will be a list with the results

Commands may also return iterators instead of lists if *iterate* is set
to *True*::

    client.iterate = True
    for song in client.playlistinfo():
        print song["file"]

Each command have a *send\_* and a *fetch\_* variant, which allows to
send a MPD command and then fetch the result later. This is useful for
the idle command::

    client.send_idle()
    # do something else or use function like select(): http://docs.python.org/howto/sockets.html#non-blocking-sockets
    # ex. select([client], [], []) or with gobject: http://jatreuman.indefero.net/p/python-mpd/page/ExampleIdle/
    events = client.fetch_idle()

Some more complex usage examples can be found
`here <http://jatreuman.indefero.net/p/python-mpd/doc/>`_

Unicode Handling
----------------

To quote the mpd protocol documentation:

> All data to be sent between the client and server must be encoded in UTF-8.

With Python 3:
~~~~~~~~~~~~~~

In Python 3, Unicode string is the default string type. So just pass
these strings as arguments for MPD commands and *python-mpd2* will also
return such Unicode string.

With Python 2.x
~~~~~~~~~~~~~~~

For backward compatibility with *python-mpd*, when running with Python
2.x, *python-mpd2* accepts both Unicode strings (ex. u"♥") and UTF-8
encoded strings (ex. "♥").

In order for *MPDClient* to return Unicode strings with Python 2, create
the instance with the ``use_unicode`` parameter set to ``True``.

Using Unicode strings should be prefered as it is done transparently by
the library for you, and makes the transition to Python 3 easier.

``python >>> import mpd >>> client = MPDClient(use_unicode=True) >>> client.urlhandlers()[0] u'http' >>> client.use_unicode = False # Can be switched back later >>> client.urlhandlers()[0] 'http'``
Using this option in Python 3 doesn't have any effect.

Logging
-------

By default messages are sent to the logger named ``mpd``::

    >>> import logging, mpd
    >>> logging.basicConfig(level=logging.DEBUG)
    >>> client = mpd.MPDClient()
    >>> client.connect("localhost", 6600)
    INFO:mpd:Calling MPD connect('localhost', 6600, timeout=None)
    >>> client.find('any', 'dubstep')
    DEBUG:mpd:Calling MPD find('any', 'dubstep')

For more information about logging configuration, see
http://docs.python.org/2/howto/logging.html

Future Compatible
-----------------

New commands or special handling of commands can be easily implemented.
Use ``add_command()`` or ``remove_command()`` to modify the commands of
the *MPDClient* class and all its instances.::

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

Currently ``MPDClient`` is **NOT** thread-safe. As it use a socket
internaly, only one thread can send or receive at the time.

But ``MPDClient`` can be easily extended to be thread-safe using
`locks <http://docs.python.org/library/threading.html#lock-objects>`_.
Take a look at ``examples/locking.py`` for further informations.

Testing
-------

Just run::

    $ python setup.py test

This will install `Tox <http://tox.testrun.org/>`_.
Tox will take care of testing against all the supported Python versions (at least available) on our computer, with the required dependencies

Contacting the author
---------------------

Just contact me (Mic92) on Github or via email (joerg@higgsboson.tk).

Usually I hang around on Jabber: sonata@conference.codingteam.net

You can contact the original author by emailing J. Alexander Treuman
jat@spatialrift.net.

He can also be found idling in #mpd on irc.freenode.net as jat.

.. |Build Status| image:: https://travis-ci.org/Mic92/python-mpd2.png
