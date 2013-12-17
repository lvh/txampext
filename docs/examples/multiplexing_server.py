from sys import stdout
from twisted.internet import endpoints, protocol, reactor
from twisted.protocols import amp
from twisted.python import log
from twisted.web import resource, server
from txampext.multiplexing import MultiplexingCommandLocator


class HelloResource(resource.Resource):
    """
    A resource that says hello.
    """
    isLeaf = True

    def render_GET(self, request):
        return "Hello from the web server!"



webFactory = server.Site(HelloResource())



class MultiplexingServerProtocol(amp.AMP, MultiplexingCommandLocator):
    def __init__(self, *args, **kwargs):
        amp.AMP.__init__(self, *args, **kwargs)
        MultiplexingCommandLocator.__init__(self, *args, **kwargs)



class Factory(protocol.ServerFactory):
    def buildProtocol(self, addr):
        proto = MultiplexingServerProtocol()
        proto.addFactory("hello", webFactory)
        return proto



ampEndpoint = endpoints.TCP4ServerEndpoint(reactor, 8884)



if __name__ == "__main__":
    log.startLogging(stdout)
    ampEndpoint.listen(Factory())
    reactor.run()
