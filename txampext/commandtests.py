"""
Tools for helping test Command definitions.

This was inspired by a class in lp:game, by JP Calderone and Christopher
Armstrong, where it was made available under the MIT license. This code
differs from that code in two ways. Firstly, it always defers to the
``Command``'s ``{parse|make}{Arguments|Response}`` class methods, instead of
using internals of Twisted's AMP implementation. Secondly, it allows you to
set a protocol for Arguments that require it, instead of hardcoding ``None``.
"""
class CommandTestMixin(object):
    """
    Mixin for test cases for serialization and parsing of AMP Commands.
    """
    command = None
    """
    The Command subclass that this mixin is supposed to test.
    """

    protocol = None
    """
    A protocol instance for use in parsing or serializing.

    This can be set as an instance attribute.
    """

    argumentObjects = {}
    """
    Example arguments, in unserialized form.
    """

    responseObjects = {}
    """
    Example response, in unserialized form.
    """

    argumentStrings = {}
    """
    Example argument, in serialized form.
    """

    responseStrings = {}
    """
    Example response, in serialized form.
    """

    def test_makeResponse(self):
        """
        ``self.responseObjects`` serializes to ``self.responseStrings``.
        """
        serialize = self.command.makeResponse
        strings = serialize(self.responseObjects, self.protocol)
        self.assertEqual(strings, self.responseStrings)


    def test_parseResponse(self):
        """
        ``self.responseStrings`` parses to ``self.responseObjects.``
        """
        parse = self.command.parseResponse
        objects = parse(self.responseStrings, self.protocol)
        self.assertEqual(objects, self.responseObjects)


    def test_makeArguments(self):
        """
        ``self.argumentObjects`` serializes to ``self.argumentStrings``.
        """
        serialize = self.command.makeArguments
        strings = serialize(self.argumentObjects, self.protocol)
        self.assertEqual(strings, self.argumentStrings)


    def test_parseArguments(self):
        """
        ``self.responseStrings`` parses to ``self.responseObjects.``
        """
        parse = self.command.parseArguments
        objects = parse(self.argumentStrings, self.protocol)
        self.assertEqual(objects, self.argumentObjects)



def stringifyValues(objects):
    """
    Returns a ``dict`` like ``objects``, except with all the values converted
    to ``str``.
    """
    return dict((k, str(v)) for k, v in objects.items())
