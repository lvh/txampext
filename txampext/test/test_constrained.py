from twisted.protocols import amp
from twisted.trial import unittest
from txampext import constrained


class ConstrainedTests(unittest.TestCase):
    def setUp(self):
        self.reference = amp.Integer()


    def _testConstrained(self, constrained, goodValues, badValues):
        for goodValue in goodValues:
            goodString = self.reference.toString(goodValue)
            self.assertEqual(constrained.fromString(goodString), goodValue)
            self.assertEqual(constrained.toString(goodValue), goodString)

        for badValue in badValues:
            badString = self.reference.toString(badValue)
            self.assertRaises(ValueError, constrained.fromString, badString)
            self.assertRaises(ValueError, constrained.toString, badValue)


    def test_singleConstraint(self):
        """
        Tests a constrained AMP argument with a single constraint.
        """
        c = constrained.Constrained(self.reference, _isPositive)
        self._testConstrained(c, [1], [0])


    def test_multipleConstraints(self):
        """
        Tests a constrained AMP argument with multiple constraints.
        """
        c = constrained.Constrained(self.reference, _isPositive, _isEven)
        self._testConstrained(c, [2, 4], [0, 1, -1])



def _isPositive(v):
    return v > 0


def _isEven(v):
    return v % 2 == 0



class ConstraintTests(unittest.TestCase):
    def test_inSet(self):
        c = constrained.inSet("ABC")
        self.assertTrue(c("A"))
        self.assertFalse(c("1"))


    def test_notInSet(self):
        c = constrained.notInSet("ABC")
        self.assertTrue(c("1"))
        self.assertFalse(c("A"))
