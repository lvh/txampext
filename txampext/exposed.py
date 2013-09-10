from twisted.protocols import amp
from zope import interface


@interface.implementer(amp.IArgumentType)
class ExposedBoxSender(object):
    """
    AMP argument that exposes the box sender to a responder function.

    This only works with protocols (usually responder locators) that expose
    their box sender a the ``_exposedBoxSender`` attribute.
    """
    def fromBox(self, name, strings, objects, proto):
        """
        Exposes the cooperating protocol's box sender.

        This exposes ``proto``'s ``_exposedBoxSender`` attribute on
        ``objects`` under ``name``.
        """
        objects[name] = proto._exposedBoxSender


    def toBox(self, name, strings, objects, proto):
        """
        A no-op.

        The exposed box sender can't be serialized back to the other side, so
        this method does nothing.
        """



@interface.implementer(amp.IArgumentType)
class ExposedProtocol(object):
    """
    AMP argument that exposes the protocol instance to a responder function.
    """
    def fromBox(self, name, strings, objects, proto):
        """
        Exposes the protocol.

        This exposes ``proto`` on ``objects`` under ``name``.
        """
        objects[name] = proto


    def toBox(self, name, strings, objects, proto):
        """
        A no-op.

        The exposed protocol can't be serialized back to the other
        side, so this method does nothing.
        """



EXPOSED_BOX_SENDER = "boxSender", ExposedBoxSender()
EXPOSED_PROTOCOL = "protocol", ExposedProtocol()
