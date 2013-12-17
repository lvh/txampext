from sys import stdout
from twisted.internet import endpoints, reactor
from twisted.protocols import amp
from twisted.python import log
from txampext import multiplexing

ampEndpoint = endpoints.TCP4ClientEndpoint(reactor, "localhost", 8884)
listeningEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8885)


class AMP(amp.AMP, multiplexing.ProxyingAMPLocator):
    """
    The AMP protocol, which includes the ProxyingAMPLocator.
    """


def main():
    log.startLogging(stdout)

    log.msg("Connecting to the AMP server...")
    d = endpoints.connectProtocol(ampEndpoint, AMP())

    d.addCallback(_connected)
    reactor.run()


def _connected(client):
    """
    Connected to AMP server, start listening locally, and give the AMP
    client a reference to the local listening factory.
    """
    log.msg("Connected to AMP server, starting to listen locally...")
    localFactory = multiplexing.ProxyingFactory(client, "hello")
    return listeningEndpoint.listen(localFactory)


if __name__ == "__main__":
    main()
