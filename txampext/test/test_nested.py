"""
Tests for nested AMP boxes.
"""
from twisted.protocols import amp
from twisted.trial import unittest
from txampext import nested


class NestedAMPBoxTests(unittest.TestCase):
    """
    Tests for nested AMP boxes.
    """
    def setUp(self):
        boxSchema = [("a", amp.Integer()), ("b", amp.String())]
        self.boxContents = {"a": 1, "b": "hi"}

        self.ampList = amp.AmpList(boxSchema)
        self.nestedBox = nested.NestedAMPBox(boxSchema)


    def test_fromStringProto(self):
        """
        Creates a wire string with an ``AmpList``, and then parses it with
        ``NestedAMPBox``. Verifies that the data roundtrips correctly.
        """
        wireString = self.ampList.toStringProto([self.boxContents], None)
        roundTripped = self.nestedBox.fromStringProto(wireString, None)
        self.assertEqual(roundTripped, self.boxContents)


    def test_toStringProtocol(self):
        """
        Creates a wire string with ``NestedAMPBox``, and then parses it with
        `AmpList`. Verifies that the data roundtrips correctly.
        """
        wireString = self.nestedBox.toStringProto(self.boxContents, None)
        roundTripped = self.ampList.fromStringProto(wireString, None)
        self.assertEqual(roundTripped, [self.boxContents])


    def test_multipleBoxes(self):
        """
        Tests the failure mode when multiple boxes are given to a
        ``NestedAMPBox``. This is supported by ``AmpList``, so it may be
        produced by a peer that is using it as a compatibility layer.
        """
        wireString = self.ampList.toStringProto([self.boxContents] * 3, None)
        parse = lambda: self.nestedBox.fromStringProto(wireString, None)
        self.assertRaises(ValueError, parse)
