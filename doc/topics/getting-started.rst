.. _getting-started:

Using the client library
------------------------

The client library can be used as follows::

    >>> from mpd import MPDClient
    >>> client = MPDClient()               # create client object
    >>> client.timeout = 10                # network timeout in seconds (floats allowed), default: None
    >>> client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
    >>> client.connect("localhost", 6600)  # connect to localhost:6600
    >>> print(client.mpd_version)          # print the MPD version
    >>> print(client.find("any", "house")) # print result of the command "find any house"
    >>> client.close()                     # send the close command
    >>> client.disconnect()                # disconnect from the server

A list of supported commands, their arguments (as MPD currently understands
them), and the functions used to parse their responses can be found in
:doc:`Commands <commands>`. See the `MPD protocol documentation
<http://www.musicpd.org/doc/protocol/>`__ for more details.

Command lists are also supported using *command\_list\_ok\_begin()* and
*command\_list\_end()*::

    >>> client.command_list_ok_begin()       # start a command list
    >>> client.update()                      # insert the update command into the list
    >>> client.status()                      # insert the status command into the list
    >>> results = client.command_list_end()  # results will be a list with the results

Commands may also return iterators instead of lists if *iterate* is set
to *True*::

    client.iterate = True
    for song in client.playlistinfo():
        print song["file"]

Each command have a *send\_* and a *fetch\_* variant, which allows to send a MPD
command and then fetch the result later. This is useful for the idle command::

    >>> client.send_idle()
    # do something else or use function like select(): http://docs.python.org/howto/sockets.html#non-blocking-sockets
    # ex. select([client], [], []) or with gobject: http://jatreuman.indefero.net/p/python-mpd/page/ExampleIdle/
    >>> events = client.fetch_idle()

Some more complex usage examples can be found
`here <http://jatreuman.indefero.net/p/python-mpd/doc/>`_

Some commands support integer ranges as argument.  This is done in python-mpd2
by using two element tuple::

    # move the first three songs
    # after the last in the playlist
    >>> client.status()
    ['file: song1.mp3',
     'file: song2.mp3',
     'file: song3.mp3',
     'file: song4.mp3']
    >>> client.move((0,3), 1)
    >>> client.status()
    ['file: song4.mp3'
     'file: song1.mp3',
     'file: song2.mp3',
     'file: song3.mp3',]

Second element can be omitted. MPD will assumes the biggest possible number then (don't forget the comma!)::
NOTE: mpd versions between 0.16.8 and 0.17.3 contains a bug, so ommiting doesn't work.

    >>> client.delete((1,))     # delete all songs, but the first.
