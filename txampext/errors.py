"""
Helpers for errors that can be raised from AMP responders.
"""
import re


class Error(RuntimeError):
    """
    An error that automatically exposes an AMP-compatible ``errors`` entry.
    """
    @classmethod
    def asAMP(cls):
        """
        Returns the exception's name in an AMP Command friendly format.

        For example, given a class named ``ExampleExceptionClass``, returns
        ``"EXAMPLE_EXCEPTION_CLASS"``.
        """
        parts = groupByUpperCase(cls.__name__)
        return cls, "_".join(part.upper() for part in parts)



groupByUpperCase = re.compile(r"[A-Z]+(?=[A-Z]|$)|[A-Z][a-z]*").findall
