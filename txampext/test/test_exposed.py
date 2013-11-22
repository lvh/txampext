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
        strings, objects, proto = {}, {}, FakeResponderLocator()
        self.argument.toBox(self.argumentKey, strings, objects, proto)

        self.assertEqual(strings, {})
        self.assertEqual(objects, {})


    def _fromBox(self):
        strings, objects, locator = {}, {}, FakeResponderLocator()
        self.argument.fromBox(self.argumentKey, strings, objects, locator)
        return strings, objects, locator



class ExposedBoxSenderTests(_ExposedTests, unittest.TestCase):
    def setUp(self):
        self.argument = exposed.ExposedBoxSender()
        self.argumentKey = "boxSender"


    def test_fromBox(self):
        """
        Tests that ``fromBox`` exposes the box sender from the protocol
        through the ``objects`` dictionary.
        """
        strings, objects, locator = self._fromBox()
        self.assertEqual(objects, {"boxSender": locator._exposedBoxSender})
        self.assertEqual(strings, {})



class ExposedResponderLocatorTests(_ExposedTests, unittest.TestCase):
    def setUp(self):
        self.argument = exposed.ExposedResponderLocator()
        self.argumentKey = "locator"


    def test_fromBox(self):
        """
        Tests that ``fromBox`` exposes the responder locator through the ``objects``
        dictionary.
        """
        strings, objects, locator = self._fromBox()
        self.assertEqual(objects, {self.argumentKey: locator})
        self.assertEqual(strings, {})



class FakeResponderLocator(object):
    def __init__(self):
        self._exposedBoxSender = object()
