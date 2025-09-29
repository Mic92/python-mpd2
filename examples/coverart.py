#!/usr/bin/env python
# -*- coding: utf-8 -*-

# IMPORTS
from mpd import MPDClient, CommandError, FailureResponseCode
from socket import error as SocketError
from sys import exit
from PIL import Image
from io import BytesIO

## SETTINGS
##
HOST = "localhost"
PORT = "6600"
PASSWORD = False
SONG = ""
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

try:
    missing_cover_art = client.albumart("does/not/exist")
except CommandError as error:
    # Asking for media that does not exist or media that has no
    # albumart should raise:
    #   mpd.base.CommandError: [50@0] {albumart} No file exists
    if error.errno is not FailureResponseCode.NO_EXIST:
        raise error

try:
    cover_art = client.readpicture(SONG)
except CommandError:
    exit(1)

if "binary" not in cover_art:
    # The song exists but has no embedded cover art
    print("No embedded art found!")
    exit(1)

if "type" in cover_art:
    print("Cover art of type " + cover_art["type"])

with Image.open(BytesIO(cover_art["binary"])) as img:
    img.show()

client.disconnect()

# VIM MODLINE
# vim: ai ts=4 sw=4 sts=4 expandtab
