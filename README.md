# txampext

`txampext` is a collection of third-party extensions and tools for Twisted's
implementation of [AMP](http://amp-protocol.net/).

# What's new

## 0.0.7 (WIP)

Features:

- Added `txampext.jsondialect`, a JSON AMP dialect, intended for browsers.

## 0.0.6

Bugfixes:

- ExposedProtocol has been renamed to ExposedResponderLocator, because
  it's actually always the responder locator (which sometimes happens
  to be the protocol) due to an implementation detail of AMP in
  Twisted.

Features:

- A new iteration of the protocol multiplexing logic. Assumes that
  you're using ``AMP`` subclasses, so that the responder locator is
  also the protocol. There's a hook you can override in case there's a
  different way to get to the protocol class from the responder
  locator. The examples do the latter.
- The documentation now has an example that listens locally for TCP
  connections and then forwards them over an AMP connection using a
  multiplexed AMP connection.

For the next release, I hope to clean up the example, and add it to
the `multiplexing` module.

## 0.0.5

Features:

- Command testing tools require explicit specification of all attributes. This takes care of a few silent failure cases. When some of the attributes aren't specified, an exception is raised detailing the missing attributes (and only the missing attributes).
- ``constrained`` has been renamed ``constraints``.
- Preliminary work on protocol multiplexing. This feature will require work in Twisted itself to complete.

Bugfixes:

- One of the command testing tool docstrings pointed to the wrong classattr.

Miscellaneous:

- Refactoring.
- Test cases use `SynchronousTestCase` where possible.

## 0.0.4

- Composed responder locators, which merge multiple responder locators into one.

## 0.0.3

First public release.

- Nested AMP box implementation.

## 0.0.2 and 0.0.1

These were internal versions. Includes stuff like CI setup, packaging metadata, et cetera.