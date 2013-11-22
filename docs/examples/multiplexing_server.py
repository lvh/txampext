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



class MultiplexingCommandLocator(multiplexing.MultiplexingCommandLocator):
    def getProtocol(self):
        return self.proto



class Factory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        locator = MultiplexingCommandLocator()
        locator.addFactory("hello", webFactory)

        proto = amp.AMP(locator=locator)
        locator.proto = proto

        return proto



ampEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8884)



if __name__ == "__main__":
    ampEndpoint.listen(Factory())
    reactor.run()
