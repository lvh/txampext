"""
Tools for helping test Command definitions.

This was inspired by a class in lp:game, by JP Calderone and Christopher
Armstrong, where it was made available under the MIT license. This code
differs from that code in two ways. Firstly, it always defers to the
``Command``'s ``{parse|make}{Arguments|Response}`` class methods, instead of
using internals of Twisted's AMP implementation. Secondly, it allows you to
set a protocol for Arguments that require it, instead of hardcoding ``None``.
Thirdly, it allows you to test for registered AMP errors.
"""
from functools import wraps


def _requiredAttributes(*attrs):
    if not attrs:
        raise ValueError("At least one attribute name must be specified")

    def decorator(f):
        @wraps(f)
        def decorated(self, _attrs=attrs, *args, **kwargs):
            unset = [attr for attr in _attrs if
                     getattr(CommandTestMixin, attr) is getattr(self, attr)]
            if unset:
                attrs = " and ".join(n + " attribute" for n in unset)
                raise ValueError("The {0} must be set.".format(attrs.strip()))

            return f(self, *args, **kwargs)
        return decorated
    return decorator



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

    This should be ``dict`` with ``bytes`` keys and parsed objects
    (``int``s, ``unicode``s...).
    """

    responseObjects = {}
    """
    Example response, in unserialized form.

    This should be ``dict`` with ``bytes`` keys and parsed objects
    (``int``s, ``unicode``s...).
    """

    argumentStrings = {}
    """
    Example argument, in serialized form.

    This should be ``dict`` with ``bytes`` keys and ``bytes`` values
    representing serialized objects.
    """

    responseStrings = {}
    """
    Example response, in serialized form.

    This should be ``dict`` with ``bytes`` keys and ``bytes`` values
    representing serialized objects.
    """

    errors = {}
    """
    Possible errors. This should be a mapping of exception classes to
    descriptions (``bytes``).
    """


    fatalErrors = {}
    """
    Possible errors that will terminate the connection. A mapping of
    exception classes to descriptions (``bytes``).
    """


    @_requiredAttributes("command", "responseObjects", "responseStrings")
    def test_makeResponse(self):
        """
        ``self.responseObjects`` serializes to ``self.responseStrings``.
        """
        serialize = self.command.makeResponse
        strings = serialize(self.responseObjects, self.protocol)
        self.assertEqual(strings, self.responseStrings)


    @_requiredAttributes("command", "responseObjects", "responseStrings")
    def test_parseResponse(self):
        """
        ``self.responseStrings`` parses to ``self.responseObjects.``
        """
        parse = self.command.parseResponse
        objects = parse(self.responseStrings, self.protocol)
        self.assertEqual(objects, self.responseObjects)


    @_requiredAttributes("command", "argumentObjects", "argumentStrings")
    def test_makeArguments(self):
        """
        ``self.argumentObjects`` serializes to ``self.argumentStrings``.
        """
        serialize = self.command.makeArguments
        strings = serialize(self.argumentObjects, self.protocol)
        self.assertEqual(strings, self.argumentStrings)


    @_requiredAttributes("command", "argumentObjects", "argumentStrings")
    def test_parseArguments(self):
        """
        ``self.argumentStrings`` parses to ``self.argumentObjects.``
        """
        parse = self.command.parseArguments
        objects = parse(self.argumentStrings, self.protocol)
        self.assertEqual(objects, self.argumentObjects)


    @_requiredAttributes("command", "fatalErrors")
    def test_fatalErrors(self):
        """
        Tests that all expected fatal errors are registered.
        """
        for cls, expectedDescription in self.fatalErrors.iteritems():
            description = self.command.fatalErrors.get(cls)
            self.assertEqual(description, expectedDescription)


    @_requiredAttributes("command", "errors")
    def test_errors(self):
        """
        Tests that all expected non-fatal errors are registered.
        """
        for cls, expectedDescription in self.errors.iteritems():
            description = self.command.errors.get(cls)
            self.assertEqual(description, expectedDescription)



def stringifyValues(objects):
    """
    Returns a ``dict`` like ``objects``, except with all the values converted
    to ``str``.
    """
    return dict((k, str(v)) for k, v in objects.items())
