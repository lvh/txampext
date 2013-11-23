"""
JSON AMP dialect.

This is a *huge* hack.
"""
from json import dumps, loads
from twisted.internet import defer, protocol
from twisted.protocols import amp, basic
from txampext import exposed


def _objectHook(obj):
    """
    An object hook for type hinting.
    """
    try:
        for name, newType in obj.pop("__type__").iteritems():
            assert type(newType) is list
            assert newType[0] == "str"
            obj[name] = [s.encode("utf-8") for s in obj[name]]
    except KeyError:
        pass

    return obj


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
        request = loads(string, object_hook=_objectHook)

        identifier = request.pop("_ask")
        # DISGUSTING IMPLEMENTATION DETAIL EXPLOITING HACK
        src = self._amp.boxReceiver.locator
        responder = src.locateResponder(request.pop("_command"))
        responderFunction = responder.func_closure[1].cell_contents
        command = responder.func_closure[2].cell_contents

        for key, ampType in command.arguments:
            ampClass = ampType.__class__

            if ampClass is exposed.ExposedResponderLocator:
                request[key] = self._amp
                continue

            transformer = _ampTypeMap.get(ampClass)
            if transformer is not None:
                request[key] = transformer(request[key])

        d = defer.maybeDeferred(responderFunction, **request)

        def _wrapAnswer(response):
            """
            Wrap the answer and return the response.
            """
            response["_answer"] = identifier
            return response

        def _report(failure):
            """
            Encode the error.
            """
            key = failure.trap(*command.allErrors)
            response = {
                "_error_code": command.allErrors[key],
                "_error_description": str(failure.value),
                "_error": identifier
            }
            return response

        d.addCallbacks(_wrapAnswer, _report)

        @d.addCallback
        def writeResponse(response):
            encoded = dumps(response, default=_default)
            self.transport.write(encoded)


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
