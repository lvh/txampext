"""
JSON AMP dialect.

This is a *huge* hack.
"""
from json import dumps, loads
from twisted.internet import defer, protocol
from twisted.protocols import amp, basic
from txampext import exposed


def _default(obj):
    # TODO: Seriously? This? What the ugh.
    try:
        return list(obj)
    except TypeError:
        return obj.isoformat()



class JSONAMPDialectReceiver(basic.NetstringReceiver):
    """
    JSON AMP dialect speaking protocol.
    """
    def __init__(self, remote):
        self._remote = remote


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
        d = self._runResponder(responder, request, command, identifier)
        d.addCallback(self._writeResponse)


    def _getCommandAndResponder(self, commandName):
        """Gets the command class and matching responder function for the
        given command name.

        """
        # DISGUSTING IMPLEMENTATION DETAIL EXPLOITING HACK
        locator = self._remote.boxReceiver.locator
        responder = locator.locateResponder(commandName)
        responderFunction = responder.func_closure[1].cell_contents
        command = responder.func_closure[2].cell_contents
        return command, responderFunction


    def _parseRequestValues(self, request, command):
        """Parses all the values in the request that are in a form specific
        to the JSON AMP dialect.

        """
        for key, ampType in command.arguments:
            ampClass = ampType.__class__

            if ampClass is exposed.ExposedResponderLocator:
                request[key] = self._remote
                continue

            decoder = _decoders.get(ampClass)
            if decoder is not None:
                value = request.get(key)
                request[key] = decoder(value, self)


    def _runResponder(self, responder, request, command, identifier):
        """Run the responser function. If it succeeds, add the _answer key.
        If it fails with an error known to the command, serialize the
        error.

        """
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
        return d


    def _writeResponse(self, response):
        """
        Serializes the response to JSON, and writes it to the transport.
        """
        encoded = dumps(response, default=_default)
        self.transport.write(encoded)


    def connectionLost(self, reason):
        """
        Tells the box receiver to stop receiving boxes.
        """
        self._remote.boxReceiver.stopReceivingBoxes(reason)
        return basic.NetstringReceiver.connectionLost(self, reason)



_decoders = {}
def _addDecoder(ampClass):
    """
    Registers a method as a decoder for a given AMP argument class.
    """
    def decorator(method):
        _decoders[ampClass] = method
        return method
    return decorator


@_addDecoder(amp.String)
def _unicodeToString(value, _receiver):
    """
    Encodes the unicode string as UTF-8.
    """
    return value.encode("utf-8")



class JSONAMPDialectFactory(protocol.Factory):
    """
    A factory for JSON AMP dialects.
    """
    def __init__(self, factory):
        """
        Initializes a JSON AMP dialect factory.
        """
        self._factory = factory


    def buildProtocol(self, addr):
        """
        Builds a bridge and associates it with an AMP protocol instance.
        """
        proto = self._factory.buildProtocol(addr)
        return JSONAMPDialectReceiver(proto)
