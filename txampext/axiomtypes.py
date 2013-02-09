"""
Tools for easier type compatibility for Axiom users.
"""
from axiom import attributes
from twisted.protocols import amp

def typeFor(attr, **kwargs):
    return _typeMap[attr.__class__](**kwargs)


_typeMap = {
    attributes.text: amp.Unicode,
    attributes.bytes: amp.String
}
