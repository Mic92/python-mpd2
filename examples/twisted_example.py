from __future__ import print_function
from mpd import MPDProtocol
from twisted.internet import protocol
from twisted.internet import reactor


class MPDApp(object):
    # Example application which deals with MPD

    def __init__(self, protocol):
        self.protocol = protocol

    def __call__(self, result):
        # idle result callback
        print('Subsystems: {}'.format(list(result)))

        def status_success(result):
            # status query success
            print('Status success: {}'.format(result))

        def status_error(result):
            # status query failure
            print('Status error: {}'.format(result))

        # query player status
        self.protocol.status()\
            .addCallback(status_success)\
            .addErrback(status_error)


class MPDClientFactory(protocol.ClientFactory):
    protocol = MPDProtocol

    def buildProtocol(self, addr):
        print('Create MPD protocol')
        protocol = self.protocol()
        protocol.factory = self
        protocol.idle_result = MPDApp(protocol)
        return protocol

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed - goodbye!: {}'.format(reason))
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print('Connection lost - goodbye!: {}'.format(reason))
        if reactor.running:
            reactor.stop()


if __name__ == '__main__':
    factory = MPDClientFactory()
    reactor.connectTCP('localhost', 6600, factory)
    reactor.run()
