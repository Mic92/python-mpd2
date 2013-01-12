python-mpd2 Changes List
========================

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
