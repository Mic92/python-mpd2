python-mpd2
===========

.. image:: https://travis-ci.org/Mic92/python-mpd2.png?branch=master
    :target: http://travis-ci.org/Mic92/python-mpd2
    :alt: Build Status

This is a fork of **[python-mpd2](https://github.com/Mic92/python-mpd2)**.

It's only purpose is to solve [an issue](https://github.com/Mic92/python-mpd2/issues/64)
where a generic Python Exception with an `[Errno 32] Broken pipe` is thrown,
whenever a script using python-mpd2 is idle for a couple of hours on Linux
systems. I experienced this behavior on Debian Linux with timeouts of +4 hours.

This fork catches the broken pipe and throws a ConnectionError (defined in the
original library) and resets the connection. As a lot of people already catch
this error, users shouldn't need to change anything, the library would only get
a bit more stable.

When a broken pipe is rethrown as ConnectionError, the traceback of the original
error is added, so no information should be lost. This holds for Python 3 as
well as for Python 2.

Please contact me for questions or requests on this fork. I really hope my
changes can be pulled to upstream sooner or later.

Find more information on the original library at **[python-mpd2](https://github.com/Mic92/python-mpd2)**.
