#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from mpd import (MPDClient, CommandError)
from random import choice
from socket import error as SocketError
from sys import exit


## SETTINGS
##
HOST = 'localhost'
PORT = '6600'
PASSWORD = False
###


client = MPDClient()

try:
    client.connect(host=HOST, port=PORT)
except SocketError:
    exit(1)

if PASSWORD:
    try:
        client.password(PASSWORD)
    except CommandError:
        exit(1)

client.add(choice(client.list('file')))
client.disconnect()

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
