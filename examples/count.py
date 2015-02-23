#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
count command is not covering 100% use case.
count can take a grouping tag which is conditionning MPD answer format.

The module is only supporting a partial set of tags defined in mpd.COUNT_GROUPING

You can add yours in order to use groupping tag not yet supported.
"""

from mpd import MPDClient, COUNT_GROUPING

HOST = 'localhost'
PORT = '6600'

COUNT_GROUPING += ['date', 'musicbrainz_artistid']


def main():
    cli = MPDClient()
    cli.connect(host=HOST, port=PORT)
    mbidc = cli.count('group', 'musicbrainz_artistid')
    datec = cli.count('group', 'date')
    cli.disconnect()

# Script starts here
if __name__ == '__main__':
    main()

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
