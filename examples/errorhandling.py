#! /usr/bin/env python
#
#Introduction
#
#A python program that continuously polls for song info. Demonstrates how and where to handle errors
#Details
#

from mpd import MPDClient, MPDError, CommandError
import sys


class PollerError(Exception):
    """Fatal error in poller."""


class MPDPoller(object):
    def __init__(self, host="localhost", port="6600", password=None):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()

    def connect(self):
        try:
            self._client.connect(self._host, self._port)
        # Catch socket errors
        except IOError as err:
            errno, strerror = err
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, strerror))

        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as e:
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, e))

        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as e:
                raise PollerError("Could not connect to '%s': "
                                  "password commmand failed: %s" %
                                  (self._host, e))

            # Catch all other possible errors
            except (MPDError, IOError) as e:
                raise PollerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, e))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()

        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()

    def poll(self):
        try:
            song = self._client.currentsong()

        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()

            try:
                self.connect()

            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)

            try:
                song = self._client.currentsong()

            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve current song: %s" % e)

        # Hurray!  We got the current song without any errors!
        print(song)


def main():
    from time import sleep

    poller = MPDPoller()
    poller.connect()

    while True:
        poller.poll()
        sleep(3)


if __name__ == "__main__":
    import sys

    try:
        main()

    # Catch fatal poller errors
    except PollerError as e:
        print("Fatal poller error: %s" % e, file=sys.stderr)
        sys.exit(1)

    # Catch all other non-exit errors
    except Exception as e:
        print("Unexpected exception: %s" % e, file=sys.stderr)
        sys.exit(1)

    # Catch the remaining exit errors
    except:
        sys.exit(0)


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
