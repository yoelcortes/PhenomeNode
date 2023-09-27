# -*- coding: utf-8 -*-
"""
"""

__all__ = ('functions',)

class Functions:
    
    def __init__(self, **functions):
        self.__dict__.update(functions)
        
    def __repr__(self):
        return f"{type(self).__name__}({', '.join([f'{i}={j!r}' for i, j in self.__dict__])})"
    
    
functions = Functions(
    sum='Σ|',
    product='Π|',
    x='·',
)