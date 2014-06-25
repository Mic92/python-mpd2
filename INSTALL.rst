PyPI:
~~~~~

::

    $ pip install python-mpd2

Debian
~~~~~~

Drop this line in */etc/apt/sources.list.d/python-mpd2.list*::

    deb http://deb.kaliko.me/debian/ testing main
    deb-src http://deb.kaliko.me/debian/ testing main

Import the gpg key as root::

    $ wget -O - http://sima.azylum.org/sima.gpg | apt-key add -

Key fingerprint::

    2255 310A D1A2 48A0 7B59  7638 065F E539 32DC 551D

Controls with *apt-key finger*.

Then simply update/install *python-mpd2* or *python3-mpd2* with apt or
aptitude:

Arch Linux
~~~~~~~~~~

Install `python-mpd2 <http://aur.archlinux.org/packages.php?ID=59276>`__
from AUR.

Gentoo Linux
~~~~~~~~~~~~

Replaces the original python-mpd beginning with version 0.4.2::

    $ emerge -av python-mpd

FreeBSD
~~~~~~~

Install *py-mpd2*::

    $ pkg_add -r py-mpd2

Packages for other distributions are welcome!
