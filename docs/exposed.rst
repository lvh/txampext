===================================
 Exposed box senders and protocols
===================================

Normally, AMP responders operate in a vacuum. They take some arguments
and return a properly formatted response. They don't know where the
arguments are coming from, or where the response is going to.

Normally, that's a very useful abstraction. Sometimes, you would like
command locators to have access to the box sender or the protocol. For
example:

- Your responder may want to switch the box receiver.
- Your responder may want to know information about the transport.

In vanilla AMP as implemented by Twisted, the box sender and the
protocol are always the same object, an instance of the
``BinaryBoxProtocol`` class. The distinction made here has two
advantages:

- It also works for more exotic AMP setups
- It conveys intent about what you want to do

Exposed box senders
===================

In your command definition, add ``txampext.exposed.EXPOSED_PROTOCOL``
to the arguments. Your responder will be called with a ``boxSender``
argument, which is the box sender.

Exposing the current box sender requires cooperation from the
protocol.

Example
-------

.. code-block:: python

   from twisted.protocols import amp
   from txampext import exposed

   class CommandWithExposedBoxSender(amp.Command):
       arguments = [exposed.EXPOSED_BOX_SENDER]
       response = []



   class Locator(amp.ResponderLocator):
       @CommandWithExposedBoxSender.responder
       def responder(self, boxSender):
           # Do something with the box sender here...
           return {}

TODO: demo how to get access to the box sender

Exposed protocols
=================

In your command definition, add ``txampext.exposed.EXPOSED_PROTOCOL``
to the arguments. Your responder will be called with a ``protocol``
argument, which is the current protocol instance.

Exposing the protocol requires no cooperation from the protocol, and
works with vanilla AMP classes.

Example
-------

.. code-block:: python

   from twisted.protocols import amp
   from txampext import exposed

   class CommandWithExposedProtocol(amp.Command):
       arguments = [exposed.EXPOSED_PROTOCOL]
       response = []



   class Locator(amp.ResponderLocator):
       @CommandWithExposedProtocol.responder
       def responder(self, protocol):
           # Do something with the protocol here...
           return {}
