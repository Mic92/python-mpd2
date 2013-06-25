python-mpd2
===========

.. image:: https://travis-ci.org/Mic92/python-mpd2.png?branch=master
    :target: http://travis-ci.org/Mic92/python-mpd2
    :alt: Build Status

*python-mpd2* is a Python library which provides a client interface for
the `Music Player Daemon <http://musicpd.org>`__.

Difference with python-mpd
--------------------------

python-mpd2 is a fork of `python-mpd`_.  While 0.4.x was backwards compatible
with python-mpd, starting with 0.5 provides enhanced features which are *NOT*
backward compatibles with the original `python-mpd`_ package.  (see PORTING.txt
for more information)

The following features were added:

-  Python 3 support (but you need at least Python 2.6)
-  support for the upcoming client-to-client protocol
-  support for new commands from MPD v0.17 (seekcur, prio, prioid,
   config, searchadd, searchaddpl)
-  remove deprecated commands (volume)
-  explicitly declared MPD commands (which is handy when using for
   example `IPython <http://ipython.org>`__)
-  a test suite
-  API documentation to add new commands (see `Future Compatible`_)
-  support for Unicode strings in all commands (optionally in python2,
   default in python3 - see `Unicode Handling`_)
-  configureable timeouts
-  support for `logging`_
-  improved support for sticker
-  improved support for ranges

If you like this module, you could try contact the original author
jat@spatialrift.net or join the discussion on the 
`issue tracker <http://jatreuman.indefero.net/p/python-mpd/issues/7/>`__ so that
it gets merged upstream.

Getting the latest source code
------------------------------

If you would like to use the latest source code, you can grab a
copy of the development version from Git by running the command::

    $ git clone git://github.com/Mic92/python-mpd2.git

Getting the latest release
--------------------------

The latest stable release of *python-mpd2* can be found on
`PyPI <http://pypi.python.org/pypi?:action=display&name=python-mpd2>`__

PyPI:
~~~~~

::

    $ pip install python-mpd2

Installation in Linux/BSD distributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Until Linux distributions adapt this package, here are some ready to use
packages to test your applications:

See `INSTALL.rst <INSTALL.rst>`__

Installing from source
----------------------

To install *python-mpd2* from source, simply run the command::

    $ python setup.py install

You can use the *--help* switch to *setup.py* for a complete list of commands
and their options. See the `Installing Python Modules
<http://docs.python.org/inst/inst.html>`__ document for more details.

Documentation
-------------

`Getting Started`

`Command Reference`

Testing
-------

Just run::

    $ python setup.py test

This will install `Tox <http://tox.testrun.org/>`__. Tox will take care of
testing against all the supported Python versions (at least available) on our
computer, with the required dependencies

Building Documentation
----------------------

Install Sphinx::

    $ easy_install -U Sphinx

Change to the source directory an run::

    $ python ./setup.py build_sphinx

Contacting the author
---------------------

Just contact me (Mic92) on Github or via email (joerg@higgsboson.tk).

Usually I hang around on Jabber: sonata@conference.codingteam.net

You can contact the original author by emailing
J. Alexander Treuman jat@spatialrift.net.

He can also be found idling in #mpd on irc.freenode.net as jat.

.. |Build Status| image:: https://travis-ci.org/Mic92/python-mpd2.png

.. _python-mpd: http://jatreuman.indefero.net/p/python-mpd/
