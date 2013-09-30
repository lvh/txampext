from twisted.protocols import amp
from twisted.trial import unittest
from txampext import exposed
from zope.interface import verify


class _ExposedTests(object):
    """
    Common unit tests.
    """
    def test_implements(self):
        """
        Verifies that the argument implements ``IArgumentType``.
        """
        verify.verifyObject(amp.IArgumentType, self.argument)

        # IArgumentType doesn't have the optional attr, see tm.tl/6765
        self.assertEqual(self.argument.optional, True)


    def test_toBox(self):
        """
        Tests that ``toBox`` doesn't modify its inputs.
        """
        strings, objects, proto = {}, {}, FakeProtocol()
        self.argument.toBox(self.argumentKey, strings, objects, proto)

        self.assertEqual(strings, {})
        self.assertEqual(objects, {})



class ExposedBoxSenderTests(_ExposedTests, unittest.TestCase):
    def setUp(self):
        self.argument = exposed.ExposedBoxSender()
        self.argumentKey = "boxSender"


    def test_fromBox(self):
        """
        Tests that ``fromBox`` exposes the box sender from the protocol
        through the ``objects`` dictionary.
        """
        strings, objects, proto = {}, {}, FakeProtocol()
        self.argument.fromBox("boxSender", strings, objects, proto)

        self.assertEqual(objects, {"boxSender": proto._exposedBoxSender})
        self.assertEqual(strings, {})


class ExposedProtocolTests(unittest.TestCase):
    def setUp(self):
        self.argument = exposed.ExposedProtocol()
        self.argumentKey = "protocol"


    def test_fromBox(self):
        """
        Tests that ``fromBox`` exposes the protocol through the ``objects``
        dictionary.
        """
        strings, objects, proto = {}, {}, FakeProtocol()
        self.argument.fromBox("protocol", strings, objects, proto)

        self.assertEqual(objects, {"protocol": proto})
        self.assertEqual(strings, {})



class FakeProtocol(object):
    def __init__(self):
        self._exposedBoxSender = object()
