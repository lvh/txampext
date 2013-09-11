======================
 Argument constraints
======================

AMP provides many basic argument types, such as byte strings, text
strings, integers, et cetera. Sometimes, you want additional
constraints, for example, integers between 0 and 100.

Using constraints
=================

The ``ConstrainedArgument`` class takes a base argument and zero or
more constraints. The base argument is passed as the first positional
argument to ``ConstrainedArgument``, the constraints are passed as
subsequent arguments. It can be used as a regular AMP argument in a
command definition.

For example:

.. code-block:: python

    ConstrainedArgument(Integer, InSet(set([1, 2, 3, 4, 5])))


Built-in constraints
====================

A few simple constraints are shipped with this module.

 .. autofunction:: txampext.constraints.inSet
 .. autofunction:: txampext.constraints.notInSet

Creating your own constraints
=============================

A constraint is a very simple callable that takes the actual argument
value and returns ``True`` if the constraint is satisfied, and
``False`` otherwise. This makes it very easy to write your own
constraints, for example:

.. code-block:: python

    def divisibleBy11(value):
        return value % 11 == 0
