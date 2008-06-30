#! /usr/bin/env python

from distutils.core import setup


DESCRIPTION = """\
An MPD (Music Player Daemon) client library written in pure Python.\
"""

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

LICENSE = """\
Copyright (C) 2008  J. Alexander Treuman <jat@spatialrift.net>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.\
"""


setup(
    name="python-mpd",
    version="0.2.1",
    description="Python MPD client library",
    long_description=DESCRIPTION,
    author="J. Alexander Treuman",
    author_email="jat@spatialrift.net",
    url="http://www.musicpd.org/~jat/python-mpd/",
    download_url="http://pypi.python.org/pypi/python-mpd/",
    py_modules=["mpd"],
    classifiers=CLASSIFIERS,
    #license=LICENSE,
    keywords=["mpd"],
    #platforms=["Independant"],
)


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
