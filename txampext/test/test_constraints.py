from twisted.protocols import amp
from twisted.trial import unittest
from txampext import constraints


class ConstraintsTests(unittest.TestCase):
    def setUp(self):
        self.argument = amp.Integer()


    def _testConstraints(self, constraints, goodValues, badValues):
        for goodValue in goodValues:
            goodString = self.argument.toString(goodValue)
            self.assertEqual(constraints.fromString(goodString), goodValue)
            self.assertEqual(constraints.toString(goodValue), goodString)

        for badValue in badValues:
            badString = self.argument.toString(badValue)
            self.assertRaises(ValueError, constraints.fromString, badString)
            self.assertRaises(ValueError, constraints.toString, badValue)


    def test_singleConstraint(self):
        """
        Tests a constraints AMP argument with a single constraint.
        """
        c = constraints.ConstrainedArgument(self.argument, _isPositive)
        self._testConstraints(c, [1], [0])


    def test_multipleConstraints(self):
        """
        Tests a constraints AMP argument with multiple constraints.
        """
        c = constraints.ConstrainedArgument(self.argument,
                                            _isPositive, _isEven)
        self._testConstraints(c, [2, 4], [0, 1, -1])



def _isPositive(v):
    return v > 0


def _isEven(v):
    return v % 2 == 0



class ConstraintTests(unittest.TestCase):
    def test_inSet(self):
        c = constraints.inSet("ABC")
        self.assertTrue(c("A"))
        self.assertFalse(c("1"))


    def test_notInSet(self):
        c = constraints.notInSet("ABC")
        self.assertTrue(c("1"))
        self.assertFalse(c("A"))
