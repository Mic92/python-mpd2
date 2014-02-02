#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
import sys
import pprint

from mpd import (MPDClient, CommandError)
from socket import error as SocketError

HOST = 'localhost'
PORT = '6600'
PASSWORD = False
##
CON_ID = {'host':HOST, 'port':PORT}
##  

## Some functions
def mpdConnect(client, con_id):
    """
    Simple wrapper to connect MPD.
    """
    try:
        client.connect(**con_id)
    except SocketError:
        return False
    return True

def mpdAuth(client, secret):
    """
    Authenticate
    """
    try:
        client.password(secret)
    except CommandError:
        return False
    return True
##

def main():
    ## MPD object instance
    client = MPDClient()
    if mpdConnect(client, CON_ID):
        print('Got connected!')
    else:
        print('fail to connect MPD server.')
        sys.exit(1)

    # Auth if password is set non False
    if PASSWORD:
        if mpdAuth(client, PASSWORD):
            print('Pass auth!')
        else:
            print('Error trying to pass auth.')
            client.disconnect()
            sys.exit(2)

    ## Fancy output
    pp = pprint.PrettyPrinter(indent=4)

    ## Print out MPD stats & disconnect
    print('\nCurrent MPD state:')
    pp.pprint(client.status())

    print('\nMusic Library stats:')
    pp.pprint(client.stats())

    client.disconnect()
    sys.exit(0)

# Script starts here
if __name__ == "__main__":
    main()
