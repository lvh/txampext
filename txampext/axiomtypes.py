"""
Tools for easier type compatibility for Axiom users.
"""
from axiom import attributes
from twisted.protocols import amp

def typeFor(attr, **kwargs):
    return _typeMap[attr.__class__](**kwargs)


_typeMap = {
    attributes.text: amp.Unicode,
    attributes.bytes: amp.String,
    attributes.integer: amp.Integer,
    attributes.money: amp.Decimal,
    attributes.ieee754_double: amp.Float,
    attributes.timestamp: amp.DateTime,
    attributes.boolean: amp.Boolean
}

for precision in range(1, 11):
    decimalType = getattr(attributes, "point{}decimal".format(precision))
    _typeMap[decimalType] = amp.Decimal
