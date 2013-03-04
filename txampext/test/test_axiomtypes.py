try:
    from txampext import axiomtypes; axiomtypes
    from axiom import attributes
except ImportError:  # pragma: no cover
    axiomtypes = None

from twisted.protocols import amp
from twisted.trial import unittest


class TypeForTests(unittest.TestCase):
    skip = axiomtypes is None

    def _test_typeFor(self, attr, expectedType, **kwargs):
        asAMP = axiomtypes.typeFor(attr, **kwargs)
        self.assertTrue(isinstance(asAMP, expectedType))
        return asAMP


    def test_optional(self):
        asAMP = axiomtypes.typeFor(attributes.text(), optional=True)
        self.assertTrue(asAMP.optional)


    def test_text(self):
        self._test_typeFor(attributes.text(), amp.Unicode)


    def test_bytes(self):
        self._test_typeFor(attributes.bytes(), amp.String)


    def test_integer(self):
        self._test_typeFor(attributes.integer(), amp.Integer)


    def test_decimals(self):
        for precision in range(1, 11):
            attr = getattr(attributes, "point{}decimal".format(precision))
            self._test_typeFor(attr(), amp.Decimal)

        self._test_typeFor(attributes.money(), amp.Decimal)


    def test_float(self):
        self._test_typeFor(attributes.ieee754_double(), amp.Float)


    def test_timestamp(self):
        self._test_typeFor(attributes.timestamp(), amp.DateTime)


    def test_boolean(self):
        self._test_typeFor(attributes.boolean(), amp.Boolean)
