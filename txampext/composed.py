"""
Tools for composing responder locators.
"""
from twisted.protocols import amp
from zope import interface


@interface.implementer(amp.IResponderLocator)
class ComposedLocator(object):
    """
    A responder locator consisting of other responder locators.
    """
    def __init__(self, locators):
        self._locators = locators


    def locateResponder(self, name):
        """
        Locates a responder from all the component responders.
        """
        for locator in self._locators:
            responder = locator.locateResponder(name)
            if responder is not None:
                return responder



class DeclarativeComposedLocator(ComposedLocator):
    """
    A responder locator that consists of other locators, declaratively
    specified.
    """
    class __metaclass__(type):
        def __new__(meta, name, bases, attrs):
            """
            Endows the subclass with an independent list of locator classes.
            """
            attrs["_locatorClasses"] = []
            return type.__new__(meta, name, bases, attrs)


    def __init__(self, *args, **kwargs):
        """
        Initializes all of the component locators with the given arguments.
        """
        locators = []
        for locatorClass in self._locatorClasses:
            locator = locatorClass(*args, **kwargs)
            locator._composer = self
            locators.append(locator)

        ComposedLocator.__init__(self, locators)


    @classmethod
    def component(cls, locatorClass):
        """
        Registers a component locator.
        """
        cls._locatorClasses.append(locatorClass)
        return locatorClass
