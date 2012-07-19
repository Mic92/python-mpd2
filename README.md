python-mpd2
===========

Difference with python-mpd
--------------------------

python-mpd2 is a fork of the python-mpd.
It is backward compatible to python-mpd, so it could act as drop-in replacement
(tested with [sonata](http://sonata.berlios.de/)).

Current features list:

 - python3 support (python2.6 is minimum python version required)
 - support for the upcoming client-to-client protocol
 - adding new commands of mpd v0.17 (seekcur, prio, prioid, config, searchadd,
   searchaddpl)
 - remove of deprecated commands (volume)
 - declare mpd commands explicit as method, so they are shown in ipython
 - add unit tests
 - documented API to add new commands (see Future Compatible)
 - use unicode strings in all commands (optionally in python2, default in python3 - see Unicode Handling)

If you like this module, you could try contact the original author <jat@spatialrift.net> or
join the discussion on the [issue tracker](http://jatreuman.indefero.net/p/python-mpd/issues/7/)

Getting the latest source code
------------------------------

If you would instead like to use the latest source code, you can grab a copy
of the development version from git by running the command:

    $ git clone git://github.com/Mic92/python-mpd2.git


Installing from source
----------------------

To install python-mpd from source, simply run the command:

    $ python setup.py install

You can use the *--help* switch to *setup.py* for a complete list of commands
and their options.  See the [Installing Python Modules](http://docs.python.org/inst/inst.html) document for more details.


Getting the latest release
--------------------------

This python-mpd2 can be found on [pypi](http://pypi.python.org/pypi?:action=display&name=python-mpd2)

###pypi:

    $ pip install python-mpd2


Until linux distributions adapt this package, here are some ready to use packages to test your applications:

### Debian

Drop this line in */etc/apt/sources.list.d/python-mpd2.list*:

    deb http://sima.azylum.org/debian unstable main

Import the gpg key as root

    $ wget -O - http://sima.azylum.org/sima.gpg | apt-key add -

Key fingerprint :

2255 310A D1A2 48A0 7B59  7638 065F E539 32DC 551D

Controls with *apt-key finger*.

Then simply update/install *python-mpd2* or *python3-mpd* with apt or aptitude:

### Arch Linux

install [python-mpd2-git](https://aur.archlinux.org/packages.php?ID=57738) from AUR

### Gentoo Linux

An ebuid is available in the `laurentb` overlay.

    echo 'dev-python/python-mpd::laurentb **' >> /etc/portage/accept_keywords
    layman -a laurentb
    emerge -av python-mpd


Packages for other distributions are welcome!


Using the client library
------------------------

The client library can be used as follows:

```python
client = mpd.MPDClient()           # create client object
client.connect("localhost", 6600,  # connect to localhost:6600
                timeout=10)        # optional timeout in seconds (floats allowed), default: None
print(client.mpd_version)          # print the mpd version
print(client.find("any", "house")) # print result of the command "find any house"
client.close()                     # send the close command
client.disconnect()                # disconnect from the server
```

A list of supported commands, their arguments (as MPD currently understands
them), and the functions used to parse their responses can be found in
*doc/commands.txt*.  See the [MPD protocol documentation](http://www.musicpd.org/doc/protocol/) for more details.

Command lists are also supported using *command_list_ok_begin()* and
*command_list_end()*:

```python
client.command_list_ok_begin()       # start a command list
client.update()                      # insert the update command into the list
client.status()                      # insert the status command into the list
results = client.command_list_end()  # results will be a list with the results
```

Commands may also return iterators instead of lists if *iterate* is set to
*True*:

```python
client.iterate = True
for song in client.playlistinfo():
    print song["file"]
```

Each command have a *send_* and a *fetch_* variant, which allows to send a
mpd command and the fetch the result later. This is useful for the idle
command:

```python
client.send_idle()
# do something else ...
events = client.fetch_idle()
```

Some more complex usage example can be found [here](http://jatreuman.indefero.net/p/python-mpd/doc/)


Unicode Handling
----------------
To quote the mpd protocol documentation:

> All data to be sent between the client and server must be encoded in UTF-8.

In python3 unicode strings are default string type. So just pass these strings as arguments for mpd commands.

For backward compatibility with python-mpd the python2 version accept both unicode strings (ex. u"♥") and unicode encoded 8-bit strings (ex. "♥").
It returns unicode encoded strings by default for the same reason.

Using unicode strings should be prefered as it makes the transition to python3 easier.
This way, decoding and encoding strings outside the library, is not needed to make function like len() behave correctly.
To make MPDClient return unicode strings in python2 create the instance with the use_unicode parameter set to true.

```python
>>> import mpd
>>> client = MPDClient(use_unicode=True)
>>> client.urlhandlers()[0]
u'http'
>>> client.use_unicode = False # Can be switched back later
>>> client.urlhandlers()[0]
'http'
```

Use this option in python3 doesn't have an effect.

Future Compatible
-----------------

New commands or special handling of commands can be easily implemented.
Use *add_command()* or *remove_command()* to modify the commands of the
*MPDClient* class and all its instances.

```python
def fetch_cover(client):
    """"Take a MPDClient instance as its arguments and return mimetype and image"""
    # this command may come in the future.
    pass
self.client.add_command("get_cover", fetch_cover)
# remove the command, because it doesn't exist already.
self.client.remove_command("get_cover")
```

Known Issues
------------

Currently python-mpd is **NOT** thread-safe. If you need to access the library from multiple threads, you have to either use [locks](http://docs.python.org/library/threading.html#lock-objects) or use one mpd client per thread.


Contacting the author
---------------------

Just connect me (Mic92) on github or via email (jthalheim@gmail.com).

Usually I hang around on jabber: sonata@conference.codingteam.net

You can contact the original author by emailing J. Alexander Treuman <jat@spatialrift.net>.

He can also be found idling in #mpd on irc.freenode.net as jat.
