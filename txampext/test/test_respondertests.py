from twisted.protocols.amp import Command, CommandLocator, Integer
from twisted.trial.unittest import FailTest, SynchronousTestCase
from txampext.respondertests import ResponderTestMixin
from txampext.test.test_commandtests import Divide


class Sum(Command):
    arguments = [
        ('a', Integer()),
        ('b', Integer())
    ]
    response = [
        ('total', Integer())
    ]



class Locator(CommandLocator):
    @Sum.responder
    def add(self, a, b): # pragma: no cover
        """Adds two numbers.

        """
        return a + b



class ResponderTestMixinTests(SynchronousTestCase):
    def setUp(self):
        self.locator = Locator()
        self.mixin = ResponderTestMixin()
        self.mixin.assertIdentical = self.assertIdentical


    def test_noCommand(self):
        """When no command class is specified, FailTest is raised with an
        appropriate message.

        """
        e = self.assertRaises(FailTest, self.mixin.test_locateResponder)
        self.assertIn("command", e.message)


    def test_noLocator(self):
        """When a command class but no locator is specified, FailTest is
        raised with an appropriate message.

        """
        self.mixin.command = Sum
        e = self.assertRaises(FailTest, self.mixin.test_locateResponder)
        self.assertIn("locator", e.message)


    def test_noResponder(self):
        """When the locator does not have an appropriate responder, FailTest
        is raised.

        """
        self.mixin.locator = self.locator
        self.mixin.command = Divide
        self.assertRaises(FailTest, self.mixin.test_locateResponder)


    def test_hasResponder(self):
        """When the locator has a responder for the command, the test
        succeeds.

        """
        self.mixin.locator = self.locator
        self.mixin.command = Sum
        self.mixin.test_locateResponder()
