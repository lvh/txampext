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
        """
        objects[name] = proto._exposedBoxSender


    def toBox(self, name, strings, objects, proto):
        """
        A no-op.

        The exposed box sender can't be serialized back to the other side, so
        this method does nothing.
        """



EXPOSED_BOX_SENDER = "boxSender", ExposedBoxSender()
