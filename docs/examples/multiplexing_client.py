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
        log.msg("Creating multiplexed AMP connection...")
        d = self._callRemote(multiplexing.Connect, factory="hello")
        d.addCallback(self._multiplexedConnectionMade)


    def _multiplexedConnectionMade(self, response):
        """Stores a reference to the connection, registers this protocol on
        the factory as one related to a multiplexed AMP connection,
        and sends currently buffered data. Gets rid of the buffer
        afterwards.

        """
        log.msg("Multiplexed AMP connection made!")

        self.connection = response["connection"]
        self.factory.protocols[self.connection] = self

        bufferedData, self._buffer = self._buffer.getvalue(), None
        if bufferedData:
            log.msg("Sending buffered data...")
            self._sendData(bufferedData)
        else:
            log.msg("No buffered data to send!")


    def dataReceived(self, data):
        """Received some data from the local side.

        If we have set up the multiplexed connection, sends the data
        over the multiplexed connection. Otherwise, buffers.

        """
        log.msg("{} bytes of data received locally".format(len(data)))
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


    def connectionLost(self, reason):
        """If we already have an AMP connection registered on the factory,
        get rid of it.

        """
        if self.connection is not None:
            del self.factory.protocols[self.connection]



class ProxyingFactory(protocol.ServerFactory):
    """A local listening factory that will proxy bytes to a remote server
    using an AMP multiplexed connection.

    """
    protocol = ProxyingProtocol

    def __init__(self, remote):
        self.remote = remote
        remote.localFactory = self
        self.protocols = {}



class ProxyingAMPProtocol(amp.AMP):
    """The AMP instance that receives commands related to a multiplexed
    connection, such as incoming data or a disconnect request, and
    replays it on the local counterpart.

    """
    localFactory = None

    def getLocalProtocol(self, connectionIdentifier):
        """Attempts to get a local protocol by connection identifier.

        """
        if self.localFactory is None:
            raise multiplexing.NoSuchConnection()

        try:
            return self.localFactory.protocols[connectionIdentifier]
        except KeyError:
            raise multiplexing.NoSuchConnection()


    @multiplexing.Transmit.responder
    def remoteDataReceived(self, connection, data):
        """Some data was received from the remote end. Find the matching
        protocol and replay it.

        """
        proto = self.getLocalProtocol(connection)
        proto.transport.write(data)
        return {}


    @multiplexing.Disconnect.responder
    def disconnect(self, connection):
        """The other side has asked us to disconnect.

        """
        proto = self.getLocalProtocol(connection)
        proto.transport.loseConnection()
        return {}



ampEndpoint = endpoints.TCP4ClientEndpoint(reactor, "localhost", 8884)
listeningEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8885)



def _connected(client):
    """
    Connected to AMP server, start listening locally, and give the AMP
    client a reference to the local listening factory.
    """
    log.msg("Connected to AMP server, starting to listen locally...")
    localFactory = ProxyingFactory(client)
    return listeningEndpoint.listen(localFactory)



if __name__ == "__main__":
    log.startLogging(stdout)
    log.msg("Connecting to the AMP server...")
    d = endpoints.connectProtocol(ampEndpoint, ProxyingAMPProtocol())
    d.addCallback(_connected)
    reactor.run()
