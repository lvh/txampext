"""
Multiplexed stream connections over AMP.
"""
from twisted.internet import interfaces, protocol
from twisted.protocols import amp
from twisted.python import log
from txampext import errors
from uuid import uuid4
from zope import interface


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO



class NoSuchFactory(errors.Error):
    """
    The referenced factory does not exist.
    """



class ConnectionRefused(errors.Error):
    """
    The factory refused to create a protocol.
    """



class NoSuchConnection(errors.Error):
    """
    The referenced connection does not exist.
    """



class Connect(amp.Command):
    """
    Creates a connection to be multiplexed over this AMP connection.
    """
    arguments = [
        ("factory", amp.String())
    ]
    response = [
        ("connection", amp.String())
    ]
    errors = dict([
        NoSuchFactory.asAMP(),
        ConnectionRefused.asAMP()
    ])



class Transmit(amp.Command):
    """Sends some data over a multiplexed connection.

    """
    arguments = [
        ("connection", amp.String()),
        ("data", amp.String())
    ]
    response = []
    errors = dict([NoSuchConnection.asAMP()])



class Disconnect(amp.Command):
    """Disconnect the multiplexed connection.

    Further attempts to use the connection will fail. This is a
    symmetric disconnect: the transport will also cease to work in the
    other direction.

    """
    arguments = [
        ("connection", amp.String())
    ]
    response = []
    errors = dict([NoSuchConnection.asAMP()])



class MultiplexingCommandLocator(amp.CommandLocator):
    """An AMP locator for multiplexing stream connections over AMP.

    This is for the "server" or "listening" end of the multiplexed
    stream connections. Of course, since AMP is symmetrical, both
    sides can have such an object.

    """
    def __init__(self):
        self._factories = {}
        self._protocols = {}


    def addFactory(self, identifier, factory):
        """Adds a factory.

        After calling this method, remote clients will be able to
        connect to it.

        This will call ``factory.doStart``.

        """
        factory.doStart()
        self._factories[identifier] = factory


    def removeFactory(self, identifier):
        """Removes a factory.

        After calling this method, remote clients will no longer be
        able to connect to it.

        This will call the factory's ``doStop`` method.

        """
        factory = self._factories.pop(identifier)
        factory.doStop()
        return factory


    def getProtocol(self):
        """Gets the AMP protocol.

        By default, this assumes that this responder locator is also
        the protocol. If there is some other relation between the two,
        override this method.

        """
        return self


    @Connect.responder
    def connect(self, factory):
        """Attempts to connect using a given factory.

        This will find the requested factory and use it to build a
        protocol as if the AMP protocol's peer was making the
        connection. It will create a transport for the protocol and
        connect it immediately. It will then store the protocol under
        a unique identifier, and return that identifier.

        """
        try:
            factory = self._factories[factory]
        except KeyError:
            raise NoSuchFactory()

        remote = self.getProtocol()
        addr = remote.transport.getPeer()
        proto = factory.buildProtocol(addr)
        if proto is None:
            raise ConnectionRefused()

        identifier = uuid4().hex
        transport = MultiplexedTransport(identifier, remote)
        proto.makeConnection(transport)

        self._protocols[identifier] = proto
        return {"connection": identifier}


    @Transmit.responder
    def receiveData(self, connection, data):
        """
        Receives some data for the given protocol.
        """
        try:
            protocol = self._protocols[connection]
        except KeyError:
            raise NoSuchConnection()

        protocol.dataReceived(data)
        return {}


    @Disconnect.responder
    def disconnect(self, connection):
        """
        Disconnects the given protocol.
        """
        proto = self._protocols.pop(connection)
        proto.transport = None
        return {}



@interface.implementer(interfaces.ITransport)
class MultiplexedTransport(object):
    """
    A local transport that makes calls over the AMP connection.
    """
    disconnecting = False  # Due to a bug in LineReceiver: tm.tl/6606

    def __init__(self, identifier, remote):
        self.identifier = identifier
        self.remote = remote


    def _callRemote(self, command, **kwargs):
        """Calls the command remotely for this transport with ``kwargs``.

        This passes the ``connection`` keyword argument to
        ``callRemote``, with the connection's identifier.

        """
        self.remote.callRemote(command, connection=self.identifier, **kwargs)


    def write(self, data):
        """Sends some data to the other side for writing.

        """
        self._callRemote(Transmit, data=data)


    def writeSequence(self, seq):
        """Write a bunch of pieces of data sequentially.

        """
        for data in seq:
            self.write(data)


    def loseConnection(self):
        """Tells the other side to disconnect.

        """
        self._callRemote(Disconnect)


    def getPeer(self):
        """Gets the AMP connection's peer.

        """
        return self.remote.transport.getPeer()


    def getHost(self):
        """Gets the AMP connection's host.

        """
        return self.remote.transport.getHost()



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

        Connect to the AMP server's multiplexed factory using the
        identifier (defined by this class' factory). When done, stores
        the connection reference and causes buffered data to be sent.

        """
        log.msg("Creating multiplexed AMP connection...")
        remoteFactoryIdentifier = self.factory.remoteFactoryIdentifier
        d = self._callRemote(Connect, factory=remoteFactoryIdentifier)
        d.addCallback(self._multiplexedConnectionMade)


    def _multiplexedConnectionMade(self, response):
        """Stores a reference to the connection, registers this protocol on
        the factory as one related to a multiplexed AMP connection,
        and sends currently buffered data. Gets rid of the buffer
        afterwards.

        """
        self.connection = conn = response["connection"]
        self.factory.protocols[conn] = self

        log.msg("Multiplexed AMP connection ({!r}) made!".format(conn))

        data, self._buffer = self._buffer.getvalue(), None
        if data:
            log.msg("Sending {} bytes of buffered data...".format(len(data)))
            self._sendData(data)
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
        d = self._callRemote(Transmit, connection=self.connection, data=data)
        d.addErrback(log.err)


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

    def __init__(self, remote, remoteFactoryIdentifier):
        self.remote = remote
        remote.localFactories.add(self)
        self.remoteFactoryIdentifier = remoteFactoryIdentifier
        self.protocols = {}



class ProxyingAMPLocator(amp.CommandLocator):
    """The AMP command locator that receives commands related to a
    multiplexed connection, such as incoming data or a disconnect
    request, and replays it on the local counterpart.

    """
    def __init__(self):
        self.localFactories = set()


    def getLocalProtocol(self, connectionIdentifier):
        """Attempts to get a local protocol by connection identifier.

        """
        for factory in self.localFactories:
            try:
                return factory.protocols[connectionIdentifier]
            except KeyError:
                continue

        raise NoSuchConnection()


    @Transmit.responder
    def remoteDataReceived(self, connection, data):
        """Some data was received from the remote end. Find the matching
        protocol and replay it.

        """
        proto = self.getLocalProtocol(connection)
        proto.transport.write(data)
        return {}


    @Disconnect.responder
    def disconnect(self, connection):
        """The other side has asked us to disconnect.

        """
        proto = self.getLocalProtocol(connection)
        proto.transport.loseConnection()
        return {}
