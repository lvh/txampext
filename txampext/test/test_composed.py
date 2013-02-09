"""
Tests for composing responder locators.
"""
from twisted.protocols import amp
from twisted.trial import unittest
from txampext import composed


nop = lambda self: None  # pragma: no cover


class FirstLocator(amp.SimpleStringLocator):
    amp_A = nop



class SecondLocator(amp.SimpleStringLocator):
    amp_B = nop



class ComposedLocatorTests(unittest.TestCase):
    """
    Tests for a locator consisting of other locators.
    """
    def test_locateResponder(self):
        locator = composed.ComposedLocator([FirstLocator(), SecondLocator()])
        locate = locator.locateResponder

        self.assertEqual(locate("a").im_func, nop)
        self.assertEqual(locate("b").im_func, nop)
        self.assertEqual(locate("c"), None)



class DeclarativeComposedLocatorTests(unittest.TestCase):
    """
    Tests for the declarative composing responder locator.
    """
    def test_locateResponder(self):
        """
        Creates a composed locator, adds compnents to it, and then tries to
        locate responders on it.
        """
        class Locator(composed.DeclarativeComposedLocator):
            pass

        def addAndVerify(responderClass):
            componentReturnValue = Locator.component(responderClass)
            self.assertIdentical(responderClass, componentReturnValue)

        addAndVerify(FirstLocator)
        addAndVerify(SecondLocator)

        locate = Locator().locateResponder
        self.assertEqual(locate("a").im_func, nop)
        self.assertEqual(locate("b").im_func, nop)
        self.assertEqual(locate("c"), None)


    def test_composer(self):
        """
        Tests that the composing locator is available to component locators.
        """
        class Locator(composed.DeclarativeComposedLocator):
            pass

        @Locator.component
        class ComponentLocator(amp.SimpleStringLocator):
            pass

        locator = Locator()
        self.assertIdentical(locator._locators[0]._composer, locator)


    def test_unique(self):
        """
        Tests that composed command locators don't affect each other.
        """
        class L1(composed.DeclarativeComposedLocator):
            pass

        class L2(composed.DeclarativeComposedLocator):
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

