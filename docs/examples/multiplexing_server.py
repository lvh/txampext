from twisted.internet import endpoints, protocol, reactor
from twisted.protocols import amp
from twisted.web import resource, server
from txampext import multiplexing

class HelloResource(resource.Resource):
    """
    A resource that says hello.
    """
    def render_GET(self, request):
        return "Hello from the web server!"


webFactory = server.Site(HelloResource())
locator = multiplexing.MultiplexingCommandLocator()
locator.addFactory("hello", webFactory)


class Factory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        return amp.AMP(locator=locator)


ampEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8884)

if __name__ == "__main__":
    import pudb; pudb.set_trace()
    ampEndpoint.listen(Factory())
    reactor.run()
