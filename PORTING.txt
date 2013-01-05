=============
Porting guide
=============

Until the versions 0.4.x, `python-mpd2`_ was a drop-in replacement for application
which were using the original `python-mpd`_. That is, you could just replace the
package's content of the latter one by the former one, and *things should just
work*.

However, starting from version 0.5, `python-mpd2`_ provides enhanced features
which are *NOT* backward compatibles with the original `python-mpd`_ package.
This goal of this document is to explains the differences the releases and if it
makes sense, how to migrate from one version to another.


Stickers API
============

When fetching stickers, `python-mpd2`_ used to return mostly the raw results MPD
was providing::

    >>> client.sticker_get('song', 'foo.mp3', 'my-sticker')
    'my-sticker=some value'
    >>> client.sticker_list('song', 'foo.mp3')
    ['my-sticker=some value', 'foo=bar']

Starting from version 0.5, `python-mpd2`_ provides a higher-level representation
of the stickers' content::

    >>> client.sticker_get('song', 'foo.mp3', 'my-sticker')
    'some value'
    >>> client.sticker_list('song', 'foo.mp3')
    {'my-sticker': 'some value', 'foo': 'bar'}

This removes the burden from the application to do the interpretation of the
stickers' content by itself.

.. versionadded:: 0.5


.. _python-mpd: http://jatreuman.indefero.net/p/python-mpd/
.. _python-mpd2: https://github.com/Mic92/python-mpd2/

.. vim:ft=rst
