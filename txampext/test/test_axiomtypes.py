try:
    from txampext import axiomtypes; axiomtypes
    from axiom import attributes
except ImportError:
    axiomtypes = None

from twisted.protocols import amp
from twisted.trial import unittest


class TypeForTests(unittest.TestCase):
    skip = axiomtypes is None

    def _test_typeFor(self, attr, expectedType, **kwargs):
        asAMP = axiomtypes.typeFor(attributes.integer, **kwargs)
        self.assertTrue(isinstance(asAMP, expectedType))
        return asAMP


    def test_integers(self):
        self._test_typeFor(attributes.integer, amp.Integer)


    def test_optional(self):
        asAMP = axiomtypes.typeFor(attributes.integer, optional=True)
        self.assertTrue(asAMP.optional)


    def test_text(self):
        self._test_typeFor(attributes.text, amp.Unicode)


    def test_bytes(self):
        self._test_typeFor(attributes.bytes, amp.String)
