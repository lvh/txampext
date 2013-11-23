=====================
 Multiplexed streams
=====================

.. py:module:: txampext.multiplexing
    :synopsis: Multiplexed stream transports over AMP

You can multiplex virtual stream transports over AMP. This means that
there are multiple virtual stream connections, where the actual bytes
are being transported over an existing AMP connection.

Unlike TCP, these virtual stream transports are symmetric, so there is
no "half-close".

Multiplexed connections use the following simple AMP commands:

 .. autoclass:: Connect

 .. autoclass:: Transmit

 .. autoclass:: Disconnect

A connection is started as follows:

.. ditaa::

     Server side (AMP peer)                        Client side (AMP peer)

    +-----------+                                   +------------------+
    | Protocol  |  (1) AMP Connect request          | AMP client       |
    | factory   |<----------------------------------+ c1FF             |
    | cPNK      |                                   |                  |
    |           +---------------------------------->|                  |
    |           |  (2) AMP Connect response         |                  |
    +-+---------+                                   +------------------+
      |
      |
      | (2) Factory builds protocol with unique id & transport
      |
      V
    +----------+
    | Protocol |
    | cGRE     |
    |          |
    |          |+-----------+
    |          || Transport |
    |          || cYEL      |
    +----------++-----------+


The AMP peer playing the role of the server in a stream connection
must implement all three. The obvious way to do that is to use the
:py:class:`MultiplexingCommandLocator` command locator.

The AMP peer playing the role of a client does not have to implement
the :py:class:`Connect` command, of course. However, since the server
side can disconnect, the client must implement :py:class:`Disconnect`.
Since the stream transport is bidirectional, the client must of course
also implement a :py:class:`Transmit` responder, to receive data
coming from the server.

Local proxying
==============

.. ditaa::

     Server side (AMP peer)                        Client side (AMP peer)

    +----------+                                +-----------++----------+
    | Protocol |     AMP Transmit request       | Transport || Protocol |
    | cGRE     |<-------------------------------+ cYEL      || cGRE     |
    |          |                                +-----------+|          |
    |          |+-----------+                                |          |
    |          || Transport +------------------------------->|          |
    |          || cYEL      |     AMP Transmit request       |          |
    +----------++-----------+                                +----------+
