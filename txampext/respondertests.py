"""
Tests for testing responder implementations.
"""
from twisted.trial.unittest import FailTest

class ResponderTestMixin(object):
    """
    A test mixin for testing CommandLocator subclasses.
    """
    command = None
    """The command.

    """

    locator = None
    """The responder locator instance.

    """

    responder = None
    """The expected responder method.

    """

    def test_locateResponder(self):
        """There is a responder for this command.

        """
        if self.command is None:
            raise FailTest("The command must be specified.")
        if self.locator is None:
            raise FailTest("The locator must be specified.")

        responder = self.locator.locateResponder(self.command.__name__)
        if responder is None:
            template = "The locator did not have a {0} responder."
            raise FailTest(template.format(self.command))

        # this is where it gets gross
        responderFunction = responder.func_closure[0].cell_contents.im_func
        self.assertIdentical(responderFunction, self.responder.im_func)
