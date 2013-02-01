"""
Tests for error classes.
"""
from twisted.trial import unittest
from txampext import errors


class AsAMPTests(unittest.TestCase):
    """
    Tests for exceptions that are easy to use in AMP Command specifications.
    """
    def _testAsAMP(self, exceptionClass, expectedName):
        cls, name = exceptionClass.asAMP()
        self.assertIdentical(cls, exceptionClass)
        self.assertEqual(name, expectedName)


    def test_simple(self):
        """
        Tests if automatic error code generation works for simple cases.
        """
        class AnExampleException(errors.Error):
            pass
        self._testAsAMP(AnExampleException, "AN_EXAMPLE_EXCEPTION")


    def test_capitalsInFront(self):
        """
        Tests if automatic error code generation works when there are several
        capitals at the start of the class name.
        """
        class AMPException(errors.Error):
            pass
        self._testAsAMP(AMPException, "AMP_EXCEPTION")


    def test_capitalsEverywhere(self):
        """
        Tests if automatic error code generation works when the capitals are
        spread across the class name.
        """
        class ExceptionWithAMPThere(errors.Error):
            pass
        self._testAsAMP(ExceptionWithAMPThere, "EXCEPTION_WITH_AMP_THERE")
