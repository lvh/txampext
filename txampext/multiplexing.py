"""
Multiplexed stream connections over AMP.
"""
from twisted.internet import interfaces
from twisted.protocols import amp
from txampext import errors
from uuid import uuid4
from zope import interface



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
