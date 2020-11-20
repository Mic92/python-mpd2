#! /usr/bin/env python

from setuptools import find_packages
from setuptools import setup
from setuptools.command.test import test as TestCommand
import mpd
import os
import sys


if sys.version_info[0] == 2:
    from io import open


VERSION = ".".join(map(str, mpd.VERSION))

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

LICENSE = """\
Copyright (C) 2008-2010  J. Alexander Treuman <jat@spatialrift.net>
Copyright (C) 2012-2017  Joerg Thalheim <joerg@thalheim.io>
Copyright (C) 2016  Robert Niederreiter <rnix@squarewave.at>

python-mpd2 is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python-mpd2 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.  You should have received a copy of the GNU Lesser General Public License
along with python-mpd2.  If not, see <http://www.gnu.org/licenses/>.\
"""


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def read(fname):
    with open(os.path.join(os.path.dirname(__file__),  fname),
              encoding="utf8") as fd:
        return fd.read()


setup(
    name="python-mpd2",
    version=VERSION,
    python_requires='>=3.6',
    description="A Python MPD client library",
    long_description=read('README.rst'),
    classifiers=CLASSIFIERS,
    author="Joerg Thalheim",
    author_email="joerg@thalheim.io",
    license="GNU Lesser General Public License v3 (LGPLv3)",
    url="https://github.com/Mic92/python-mpd2",
    packages=find_packages(),
    zip_safe=True,
    keywords=["mpd"],
    test_suite="mpd.tests",
    tests_require=[
        'tox',
        'mock',
        'Twisted'
    ],
    cmdclass={
        'test': Tox
    },
    extras_require={
        'twisted': ['Twisted']
    }
)

# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
