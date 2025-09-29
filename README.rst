python-mpd2
===========

.. image:: https://travis-ci.org/Mic92/python-mpd2.png?branch=master
    :target: http://travis-ci.org/Mic92/python-mpd2
    :alt: Build Status

*python-mpd2* is a Python library which provides a client interface for
the `Music Player Daemon <http://musicpd.org>`__.


Getting the latest source code
------------------------------

If you would like to use the latest source code, you can grab a
copy of the development version from Git by running the command::

    $ git clone https://github.com/Mic92/python-mpd2.git


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
and their options. See the `Installing Python Modules <http://docs.python.org/inst/inst.html>`__ document for more details.


Documentation
-------------

`Documentation <https://python-mpd2.readthedocs.io/en/latest/>`__

`Getting Started <https://python-mpd2.readthedocs.io/en/latest/topics/getting-started.html>`__

`Command Reference <https://python-mpd2.readthedocs.io/en/latest/topics/commands.html>`__

`Examples <examples>`__


Testing
-------

Just run::

    $ python setup.py test

This will install `Tox <http://tox.testrun.org/>`__. Tox will take care of
testing against all the supported Python versions (at least available) on our
computer, with the required dependencies

If you have nix, you can also use the provided `default.nix` to bring all supported
python versions in scope using `nix-shell`. In that case run `tox` directly instead
of using `setup.py`::

     $ nix-shell --command 'tox'


Building Documentation
----------------------

Install Sphinx::

    $ pip install Sphinx

Change to the source directory and run::

    $ python ./setup.py build_sphinx

The command reference is generated from the official mpd protocol documentation.
In order to update it, install python-lxml and run the following command::

    $ python ./doc/generate_command_reference.py > ./doc/topics/commands.rst


.. _python-mpd: https://pypi.python.org/pypi/python-mpd/
