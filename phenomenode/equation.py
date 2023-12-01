# -*- coding: utf-8 -*-
"""
"""

__all__ = ('Equation',)

class Equation:
    __slots__ = ('terms')
    
    def __init__(self, *terms):
        self.terms = terms

    def __str__(self):
        return ' = '.join([format(i) for i in self.terms])

    def __repr__(self):
        return f"{type(self).__name__}{self.terms!r}"
    
