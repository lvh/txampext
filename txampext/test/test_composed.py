"""
Tests for composing responder locators.
"""
from twisted.protocols import amp
from twisted.trial import unittest
from txampext import composed


class ComposedCommandLocatorTests(unittest.TestCase):
    """
    Tests for a composing responder locator.
    """
    def test_locateResponder(self):
        """
        Creates a composed locator, adds compnents to it, and then tries to
        locate responders on it.
        """
        class ComposedLocator(composed.ComposedLocator):
            pass

        nop = lambda self: None  # pragma: no cover

        @ComposedLocator.component
        class FirstResponder(amp.SimpleStringLocator):
            amp_A = nop

        @ComposedLocator.component
        class SecondResponder(amp.SimpleStringLocator):
            amp_B = nop


        locate = ComposedLocator().locateResponder
        self.assertEqual(locate("a").im_func, nop)
        self.assertEqual(locate("b").im_func, nop)
        self.assertEqual(locate("c"), None)


    def test_composer(self):
        """
        Tests that the composing locator is available to component locators.
        """
        class ComposedLocator(composed.ComposedLocator):
            pass

        @ComposedLocator.component
        class ComponentLocator(amp.SimpleStringLocator):
            pass

        locator = ComposedLocator()
        self.assertIdentical(locator._locators[0]._composer, locator)


    def test_unique(self):
        """
        Tests that composed command locators don't affect each other.
        """
        class L1(composed.ComposedLocator):
            pass

        class L2(composed.ComposedLocator):
            pass

        @L1.component
        class C1(object):
            pass

        @L2.component
        class C2(object):
            pass


        def assertComponent(component, locator):
            self.assertIn(component, locator._locatorClasses)


        def assertNotComponent(component, locator):
            self.assertNotIn(component, locator._locatorClasses)


        assertComponent(C1, L1)
        assertNotComponent(C1, L2)

        assertNotComponent(C2, L1)
        assertComponent(C2, L2)

