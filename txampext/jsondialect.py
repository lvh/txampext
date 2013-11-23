"""
JSON AMP dialect.

This is a *huge* hack.
"""
from json import dumps, loads
from twisted.internet import defer, protocol
from twisted.protocols import amp, basic
from txampext import exposed


def _default(obj):
    try:
        return list(obj)
    except TypeError:
        return obj.isoformat()



class JSONAMPDialectReceiver(basic.NetstringReceiver):
    """
    JSON AMP dialect speaking protocol.
    """
    def __init__(self, amp):
        self._amp = amp


    def stringReceived(self, string):
        """Handle a JSON AMP dialect request.

        First, the JSON is parsed. Then, all JSON dialect specific
        values in the request are turned into the correct objects.
        Then, finds the correct responder function, calls it, and
        serializes the result (or error).

        """
        request = loads(string)

        identifier = request.pop("_ask")
        commandName = request.pop("_command")
        command, responder = self._getCommandAndResponder(commandName)

        self._parseRequestValues(request, command)

        d = defer.maybeDeferred(responder, **request)

        def _addIdentifier(response):
            """Return the response with an ``_answer`` key.

            """
            response["_answer"] = identifier
            return response

        def _serializeFailure(failure):
            """
            If the failure is serializable by this AMP command, serialize it.
            """
            key = failure.trap(*command.allErrors)
            response = {
                "_error_code": command.allErrors[key],
                "_error_description": str(failure.value),
                "_error": identifier
            }
            return response

        d.addCallbacks(_addIdentifier, _serializeFailure)

        @d.addCallback
        def writeResponse(response):
            encoded = dumps(response, default=_default)
            self.transport.write(encoded)


    def _getCommandAndResponder(self, commandName):
        """Gets the command class and matching responder function for the
        given command name.

        """
        # DISGUSTING IMPLEMENTATION DETAIL EXPLOITING HACK
        locator = self._amp.boxReceiver.locator
        responder = locator.locateResponder(commandName)
        responderFunction = responder.func_closure[1].cell_contents
        command = responder.func_closure[2].cell_contents
        return command, responderFunction


    def _parseRequestValues(self, request, command):
        """
        Parses all the values in the request that are in a form specifi to
        the JSON AMP dialect.
        """
        for key, ampType in command.arguments:
            ampClass = ampType.__class__

            if ampClass is exposed.ExposedResponderLocator:
                request[key] = self._amp
                continue

            transformer = _ampTypeMap.get(ampClass)
            if transformer is not None:
                request[key] = transformer(request[key])


    def connectionLost(self, reason):
        """
        Tells the box receiver to stop receiving boxes.
        """
        self._amp.boxReceiver.stopReceivingBoxes(reason)
        return basic.NetstringReceiver.connectionLost(self, reason)



_ampTypeMap = {
    amp.String: lambda u: u.encode("utf-8")
}



class JSONAMPDialectFactory(protocol.Factory):
    """
    A factory for JSON AMP dialects.
    """
    def __init__(self, ampFactory):
        self._ampFactory = ampFactory


    def buildProtocol(self, addr):
        """
        Builds a bridge and associates it with an AMP protocol instance.
        """
        ampProto = self._ampFactory.buildProtocol(addr)
        return JSONAMPDialectReceiver(ampProto)
