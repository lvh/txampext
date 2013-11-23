==================
 JSON AMP dialect
==================

.. py:module:: txampext.jsondialect
    :synopsis: A JSON dialect of AMP.

``txampext`` comes with a tool for speaking a dialect of AMP in JSON.
This is intended so you can speak AMP with (bad) browsers over
WebSockets or SockJS.

.. warning::

   This is a huge, huge hack. It relies on a bunch of internal
   implementation details. It does crazy things like access function
   closures. Expect this to break.

This dialect prefers to use JSON's native types instead of just using
a JSON objects with values being binary AMP encoded values. Since IE8
and IE9 are supported platforms, but don't have ``Uint8Array``, it's
impossible to produce AMP's protocol bytes on the client side. Also,
since there's less serialization and deserialization going on, it's
(slightly) faster. Unfortunately, this decision also means the
implementation has to sidestep much of AMP's internals, which is why
it is quite brittle and hacky.

If only good browsers have to be supported (with ``Uint8Array``,
binary WebSockets), please speak regular AMP over WebSockets instead.

This also affects types. AMP has richer type support than JSON. For
example, JSON has only one string type, which is semantically Unicode.
AMP has both bytestrings (:py:class:`twisted.protocols.amp.String`)
and Unicode strings (:py:class:`twisted.protocols.amp.Unicode`).

JSON has one number type, which can encode integers and floats. AMP
supports integers (:py:class:`twisted.protocols.amp.Integer`), floats
(:py:class:`twisted.protocols.amp.Float`), and decimals
(:py:class:`twisted.protocols.amp.Decimal`).
