from sys import stdout
from twisted.internet import endpoints, protocol, reactor
from twisted.protocols import amp
from twisted.python import log
from txampext import multiplexing

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


class ProxyingProtocol(protocol.Protocol):
    """Proxies local connection over AMP.

    """
    def __init__(self):
        self.connection = None
        self._buffer = StringIO()


    def _callRemote(self, command, **kwargs):
        """Shorthand for ``callRemote``.

        This uses the factory's connection to the AMP peer.

        """
        return self.factory.remote.callRemote(command, **kwargs)


    def connectionMade(self):
        """Create a multiplexed stream connection.

        Connect to the AMP server's ``hello`` factory. When done,
        stores the connection reference and causes buffered data to be
        sent.

        """
        log.msg("Local connection made, creating AMP connection...")
        d = self._callRemote(multiplexing.Connect, factory="hello")
        d.addCallback(self._multiplexedConnectionMade)


    def _multiplexedConnectionMade(self, response):
        """Stores a reference to the connection and sends currently buffered
        data. Gets rid of the buffer afterwards.

        """
        self.connection = response["connection"]

        bufferedData, self._buffer = self._buffer.getvalue(), None
        if bufferedData:
            log.msg("Sending buffered data...")
            self._sendData(bufferedData)
        else:
            log.msg("No buffered data to send!")


    def dataReceived(self, data):
        """Receives some data.

        If we have set up the multiplexed connection, sends the data
        over the multiplexed connection. Otherwise, buffers.

        """
        log.msg("{} bytes of data received!".format(len(data)))
        if self.connection is None:
            # we haven't finished connecting yet
            log.msg("Connection not made yet, buffering...")
            self._buffer.write(data)
        else:
            log.msg("Sending data...")
            self._sendData(data)


    def _sendData(self, data):
        """Actually sends data over the wire.

        """
        self._callRemote(multiplexing.Transmit,
                         connection=self.connection,
                         data=data)



class Factory(protocol.ServerFactory):
    protocol = ProxyingProtocol

    def __init__(self, remote):
        self.remote = remote



AMPFactory = protocol.ClientFactory.forProtocol(amp.AMP)
ampEndpoint = endpoints.TCP4ClientEndpoint(reactor, "localhost", 8884)
listeningEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8885)


def _connected(client):
    """
    Connected to AMP server, start listening.
    """
    log.msg("Connected to AMP server, starting to listen locally...")
    factory = Factory(client)
    return listeningEndpoint.listen(factory)


if __name__ == "__main__":
    log.startLogging(stdout)
    log.msg("Connecting to the AMP server...")
    ampEndpoint.connect(AMPFactory).addCallback(_connected)
    reactor.run()
