python-mpd2 Changes List
========================

Changes in v3.0.3
-----------------

* asyncio: tolerate early disconnects

Changes in v3.0.2
-----------------

* asyncio: fix disconnect happen before connect
* asyncio: better protection against request cancellation
* asyncio: idle iterator raises error when connection closed


Changes in v3.0.1
-----------------

* 3.0.0 accidentially introduced typing annotation that were not meant to be published yet.


Changes in v3.0.0
-----------------

* Breaking changes: albumart now returns dictionary :code:`{"size": "...",
"binary": b"..."}` instead of just a string
* add readpicture command
* add partition, newpartition and delpartition commands
* add moveoutput command
* removed deprecated `send_` and `fetch_` commands. Use the asyncio or twisted API instead for asynchronous mpd commands.

Changes in v2.0.0
-----------------

* Minimum python version was increased to python3.6, python2.7 support was dropped
* asyncio: fix parsing delimiters
* add support for albumart command

Changes in v1.1.0
-----------------

* Fix list command to work with grouping. Always returns list of dictionaries now.
  Make sure to adopt your code since this is an API change.
* fix compatibility with python3.9
* fix connecting to unix socket in asyncio version
* close asyncio transports on disconnect
* create TCP socket with TCP_NODELAY for better responsiveness


Changes in v1.0.0
-----------------

* Add support for twisted
* Add support for asyncio
* Use @property and @property.setter for MPDClient.timeout
* Deprecate send_* and fetch_* variants of MPD commands: Consider using asyncio/twisted instead
* Port argument is optional when connecting via unix sockets.
* python-mpd will now raise mpd.ConnectionError instead of socket.error, when connection is lost
* Add command outputvolume for forked-daapd


Changes in v0.5.5
-----------------

* fix sended newlines on windows systems
* include tests in source distribution


Changes in v0.5.4
-----------------

* support for listfiles, rangeid, addtagid, cleartagid, mount, umount,
  listmounts, listneighbors


Changes in v0.5.3
-----------------

* noidle command does returns pending changes now


Changes in v0.5.2
-----------------

* add support for readcomments and toggleoutput


Changes in v0.5.1
-----------------

* add support for ranges


Changes in 0.5.0
----------------

* improved support for sticker


Changes in 0.4.6
----------------

* enforce utf8 for encoding/decoding in python3


Changes in 0.4.5
----------------

* support for logging


Changes in 0.4.4
----------------

* fix cleanup after broken connection
* deprecate timeout parameter added in v0.4.2
* add timeout and idletimeout property


Changes in 0.4.3
----------------

* add searchadd and searchaddpl command
* fix commands without a callback function
* transform MPDClient to new style class


Changes in 0.4.2
----------------

* backward compatible unicode handling
* added optional socket timeout parameter


Changes in 0.4.1
----------------

* prio and prioid was spelled wrong
* added config command
* remove deprecated volume command


Changes in 0.4.0
----------------

* python3 support (python2.6 is minimum python version required)
* support for the upcoming client-to-client protocol
* added new commands of mpd (seekcur, prior, priorid)
* methods are explicit declared now, so they are shown in ipython
* added unit tests
* documented API to add new commands (see Future Compatible)


Changes in 0.3.0
----------------

* added replay_gain_mode and replay_gain_status commands
* added mixrampdb and mixrampdelay commands
* added findadd and rescan commands
* added decoders command
* changed license to LGPL
* added sticker commands
* correctly handle errors in command lists (fixes a longstanding bug)
* raise IteratingError instead of breaking horribly when called wrong
* added fileno() to export socket FD (for polling with select et al.)
* asynchronous API (use send_<cmd> to queue, fetch_<cmd> to retrieve)
* support for connecting to unix domain sockets
* added consume and single commands
* added idle and noidle commands
* added listplaylists command


Changes in 0.2.1
----------------

* connect() no longer broken on Windows


Changes in 0.2.0
----------------

* support for IPv6 and multi-homed hostnames
* connect() will fail if already connected
* commands may now raise ConnectionError
* addid and update may now return None
