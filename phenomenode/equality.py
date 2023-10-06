# -*- coding: utf-8 -*-
"""
"""

__all__ = ('Equality',)

class Equality:
    __slots__ = ('terms')
    
    def __init__(self, *terms):
        self.terms = terms

    def __str__(self):
        return ' = '.join([str(i) for i in self.terms])

    def __repr__(self):
        return f"{type(self).__name__}{self.terms!r}"
    
