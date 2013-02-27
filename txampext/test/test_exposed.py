from twisted.trial import unittest
from txampext import exposed


class ExposedBoxSenderTests(unittest.TestCase):
    def setUp(self):
        self.argument = exposed.ExposedBoxSender()


    def test_fromBox(self):
        """
        Tests that ``fromBox`` exposes the box sender from the protocol into
        the ``objects`` dictionary.
        """
        strings, objects, proto = {}, {}, FakeProtocol()
        self.argument.fromBox("boxSender", strings, objects, proto)

        self.assertEqual(objects, {"boxSender": proto._exposedBoxSender})
        self.assertEqual(strings, {})


    def test_toBox(self):
        """
        Tests that ``toBox`` doesn't modify its inputs.
        """
        strings, objects, proto = {}, {}, FakeProtocol()
        self.argument.toBox("boxSender", strings, objects, proto)

        self.assertEqual(strings, {})
        self.assertEqual(objects, {})



class FakeProtocol(object):
    def __init__(self):
        self._exposedBoxSender = object()
