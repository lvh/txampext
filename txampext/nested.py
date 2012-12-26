"""
Implementation of a nested AMP box.
"""
from twisted.protocols import amp


class NestedAMPBox(amp.AmpList):
    """
    An AMP box within an AMP box.

    Implemented as an ``amp.AmpList`` of length 1.
    """
    def fromStringProto(self, inString, proto):
        """
        Defers to `amp.AmpList`, then gets the element from the list.
        """
        value, = amp.AmpList.fromStringProto(self, inString, proto)
        return value


    def toStringProto(self, inObject, proto):
        """
        Wraps the object in a list, and then defers to ``amp.AmpList``.
        """
        return amp.AmpList.toStringProto(self, [inObject], proto)
