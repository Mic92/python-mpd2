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
