from twisted.protocols import amp
from zope import interface


class _ExposingArgument(object):
    """
    Superclass for exposing arguments.
    """
    optional = True

    def toBox(self, name, strings, objects, proto):
        """A no-op.

        The exposed value is specific to the local connection. It
        can't be serialized back to the other side, so this method
        does nothing.

        """


@interface.implementer(amp.IArgumentType)
class ExposedBoxSender(_ExposingArgument):
    """
    AMP argument that exposes the box sender to a responder function.

    This only works with responder locators that expose their box
    sender a the ``_exposedBoxSender`` attribute.

    """
    def fromBox(self, name, strings, objects, responderLocator):
        """
        Exposes the cooperating protocol's box sender.

        This exposes ``proto``'s ``_exposedBoxSender`` attribute on
        ``objects`` under ``name``.
        """
        objects[name] = responderLocator._exposedBoxSender



@interface.implementer(amp.IArgumentType)
class ExposedResponderLocator(_ExposingArgument):
    """
    AMP argument that exposes the responder locator to a responder function.
    """
    def fromBox(self, name, strings, objects, responderLocator):
        """
        Exposes the protocol.

        This exposes ``responderLocator`` on ``objects`` under ``name``.
        """
        objects[name] = responderLocator



EXPOSED_BOX_SENDER = "boxSender", ExposedBoxSender()
EXPOSED_RESPONDER_LOCATOR = "responderLocator", ExposedResponderLocator()
