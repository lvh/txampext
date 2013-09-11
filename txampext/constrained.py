from twisted.protocols import amp


class ConstrainedArgument(amp.Argument):
    """
    An AMP argument, further constrained by a number of callables.
    """
    def __init__(self, baseArgument, *constraints):
        self.baseArgument = baseArgument
        self.constraints = constraints


    def _checkConstraints(self, value):
        for constraint in self.constraints:
            if not constraint(value):
                template = "Constraint {} not satisfied for {}"
                raise ValueError(template.format(constraint, value))


    def toString(self, value):
        """
        If all of the constraints are satisfied with the given value, defers
        to the composed AMP argument's ``toString`` method.
        """
        self._checkConstraints(value)
        return self.baseArgument.toString(value)


    def fromString(self, string):
        """
        Converts the string to a value using the composed AMP argument, then
        checks all the constraints against that value.
        """
        value = self.baseArgument.fromString(string)
        self._checkConstraints(value)
        return value



def inSet(values):
    """
    Creates a constraint that checks a value is one of the provided values.
    """
    def constraint(value):
        return value in values
    return constraint


def notInSet(values):
    """
    Creates a constraint that checks a value is not one of the provided values.
    """
    def constraint(value):
        return value not in values
    return constraint
