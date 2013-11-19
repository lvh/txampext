# txampext

`txampext` is a collection of third-party extensions and tools for Twisted's
implementation of [AMP](http://amp-protocol.net/).

# What's new

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