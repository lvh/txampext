"""
Tests for the tools to help with testing Comamnd definitions.
"""
from twisted.protocols import amp
from twisted.trial.unittest import SynchronousTestCase
from txampext.commandtests import CommandTestMixin, stringifyValues
from txampext.commandtests import _requiredAttributes


class ProtoDumper(object):
    """
    A test argument that places the protocol it is passed into the box.
    """
    def toBox(self, name, strings, objects, proto):
        strings[name] = proto


    def fromBox(self, name, strings, objects, proto):
        objects[name] = proto



class Divide(amp.Command):
    """
    Divides two numbers, and dumps the protocol in arguments and
    response because of reasons.
    """
    arguments = [
        ("left", amp.Integer()),
        ("right", amp.Integer()),
        ("proto", ProtoDumper())
    ]
    response = [
        ("result", amp.Integer()),
        ("proto", ProtoDumper())
    ]
    errors = {ZeroDivisionError: "DIVIDE_BY_ZERO"}
    fatalErrors = {MemoryError: "MEMORY_ERROR"}



class CommandTestMixinTests(CommandTestMixin, SynchronousTestCase):
    """
    Tests for the command testing mixin.
    """
    command = Divide
    argumentObjects = {"left": 2, "right": 2}
    argumentStrings = stringifyValues(argumentObjects)
    responseObjects = {"result": 1}
    responseStrings = stringifyValues(responseObjects)
    errors = {ZeroDivisionError: "DIVIDE_BY_ZERO"}
    fatalErrors = {MemoryError: "MEMORY_ERROR"}

    def setUp(self):
        self.protocol = object()

        argumentDicts = [self.argumentObjects, self.argumentStrings]
        responseDicts = [self.responseObjects, self.responseStrings]
        for d in argumentDicts + responseDicts:
            d["proto"] = self.protocol



class RequiredAttributesDecoratorTests(SynchronousTestCase):
    """
    Tests for the decorator used to implement the required attributes behavior.
    """
    def test_mustSpecifyAtLeastOne(self):
        """
        The decorator must be invoked with at least one attribute.
        """
        self.assertRaises(ValueError, _requiredAttributes)


    def test_oneAttribute(self):
        """
        The decorator can be invoked with one attribute.
        """
        _requiredAttributes("protocol", "errors")


    def test_multipleAttributes(self):
        """
        The decorator can be invoked with multiple attributes.
        """
        _requiredAttributes("protocol", "errors")



class CommandTestMixinRequiredAttributesTests(SynchronousTestCase):
    """
    When using ``CommandTestMixin``, all class attributes must be
    manually specified.
    """
    def setUp(self):
        self.mixin = CommandTestMixin()
        self.mixin.assertNotIdentical = self.assertNotIdentical


    def assertFailsWithErrorMessage(self, method, attrs):
        e = self.assertRaises(ValueError, method)

        attrs = " and ".join(n + " attribute" for n in attrs)
        expected = "The {} must be set.".format(attrs.strip())
        self.assertEqual(e.message, expected)


    def test_makeResponse(self):
        """
        The command class, response objects and strings must be specified
        in order to make a response.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_makeResponse,
            ["command", "responseObjects", "responseStrings"])


    def test_parseResponse(self):
        """
        The command class, response objects and strings must be specified
        in order to parse a response.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_parseResponse,
            ["command", "responseObjects", "responseStrings"])


    def test_makeArguments(self):
        """
        The command class, argument objects and strings must be specified
        in order to make arguments.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_makeArguments,
            ["command", "argumentObjects", "argumentStrings"])


    def test_parseArguments(self):
        """
        The command class, argument objects and strings must be specified
        in order to parse arguments.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_parseArguments,
            ["command", "argumentObjects", "argumentStrings"])


    def test_errors(self):
        """
        The command class and expected errors must be specified in order
        to check if errors are registered.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_errors,
            ["command", "errors"])


    def test_fatalErrors(self):
        """
        The command class and expected fatal errors must be specified in
        order to check if fatal errors are registered.
        """
        self.assertFailsWithErrorMessage(
            self.mixin.test_fatalErrors,
            ["command", "fatalErrors"])
