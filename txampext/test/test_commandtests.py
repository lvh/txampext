"""
Tests for the tools to help with testing Comamnd definitions.
"""
from twisted.protocols import amp
from twisted.trial import unittest
from txampext.commandtests import CommandTestMixin, stringifyValues


class ProtoDumper(object):
    """
    A test argument that places the protocol it is passed into the box.
    """
    def toBox(self, name, strings, objects, proto):
        strings[name] = proto


    def fromBox(self, name, strings, objects, proto):
        objects[name] = proto



class Add(amp.Command):
    """
    Adds two numbers, and dumps the protocol in arguments and response
    because of reasons.
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


class CommandTestMixinTests(CommandTestMixin, unittest.TestCase):
    """
    Tests for the command testing mixin.
    """
    command = Add
    argumentObjects = {"left": 1, "right": 2}
    argumentStrings = stringifyValues(argumentObjects)
    responseObjects = {"result": 3}
    responseStrings = stringifyValues(responseObjects)

    def setUp(self):
        self.protocol = object()

        argumentDicts = [self.argumentObjects, self.argumentStrings]
        responseDicts = [self.responseObjects, self.responseStrings]
        for d in argumentDicts + responseDicts:
            d["proto"] = self.protocol
