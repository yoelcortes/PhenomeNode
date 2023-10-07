# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn

__all__ = ('Quantity',)

class Quantity:
    
    def __and__(self, other):
        if isinstance(other, Quantities):
            return Quantities(self, *other.quantities)
        else:
            return Quantities(self, other)
    
    def __add__(self, other):
        return phn.Term(self, other, '+')
        
    def __radd__(self, other):
        return phn.Term(other, self, '+')
        
    def __sub__(self, other):
        return phn.Term(self, other, '-')
    
    def __rsub__(self, other):
        return phn.Term(other, self, '-')    
    
    def __mul__(self, other):
        return phn.Term(self, other, '*')
        
    def __rmul__(self, other):
        return phn.Term(other, self, '*')  
        
    def __truediv__(self, other):
        return phn.Term(self, other, '/')
        
    def __rtruediv__(self, other):
        return phn.Term(other, self, '/')
        
    def __pow__(self, other):
        return phn.Term(self, other, '^')
    
class Quantities:
    __slots__ = ('quantities',)
    
    def __init__(self, *quantities):
        self.quantities = quantities
    
    def __and__(self, other):
        if isinstance(other, Quantities):
            return Quantities(*self.quantities, *other.quantities)
        else:
            return Quantities(*self.quantities, other)
    
    def __str__(self):
        return ', '.join([str(i) for i in self.quantities])
    
    def __repr__(self):
        return f"{type(self).__name__}{self.quantities!r}"