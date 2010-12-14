python-mpd
==========

Getting python-mpd
------------------

The latest release of python-mpd can be found at
http://pypi.python.org/pypi/python-mpd/[].


Getting the latest source code
------------------------------

If you would instead like to use the latest source code, you can grab a copy
of the development version from git by running the command:

  git clone git://jatreuman.indefero.net/jatreuman/python-mpd.git


Installing from source
----------------------

To install python-mpd from source, simply run the command:

  python setup.py install

You can use the `--help` switch to `setup.py` for a complete list of commands
and their options.  See the http://docs.python.org/inst/inst.html[Installing
Python Modules] document for more details.


Using the client library
------------------------

The client library can be used as follows:

------------------------------------------------------------------------------
client = mpd.MPDClient()           # create client object
client.connect("localhost", 6600)  # connect to localhost:6600
print client.mpd_version           # print the mpd version
print client.cmd("one", 2)         # print result of the command "cmd one 2"
client.close()                     # send the close command
client.disconnect()                # disconnect from the server
------------------------------------------------------------------------------

A list of supported commands, their arguments (as MPD currently understands
them), and the functions used to parse their responses can be found in
`doc/commands.txt`.  See the
http://www.musicpd.org/doc/protocol/[MPD protocol documentation] for more
details.

Command lists are also supported using `command_list_ok_begin()` and
`command_list_end()`:

------------------------------------------------------------------------------
client.command_list_ok_begin()       # start a command list
client.update()                      # insert the update command into the list
client.status()                      # insert the status command into the list
results = client.command_list_end()  # results will be a list with the results
------------------------------------------------------------------------------

Commands may also return iterators instead of lists if `iterate` is set to
`True`:

------------------------------------------------------------------------------
client.iterate = True
for song in client.playlistinfo():
    print song["file"]
------------------------------------------------------------------------------


Contacting the author
---------------------

You can contact the author by emailing J. Alexander Treuman
<mailto:jat@spatialrift.net[]>.  He can also be found idling in #mpd on
irc.freenode.net as jat.
