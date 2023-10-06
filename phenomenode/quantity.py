# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn

__all__ = ('Quantity',)

class Quantity:
    
    def __add__(self, other):
        phn.Term(self, other, '+')
        
    def __radd__(self, other):
        phn.Term(other, self, '+')
        
    def __sub__(self, other):
        phn.Term(self, other, '-')
    
    def __rsub__(self, other):
        phn.Term(other, self, '-')    
    
    def __mul__(self, other):
        phn.Term(self, other, '*')
        
    def __rmul__(self, other):
        phn.Term(other, self, '*')  
        
    def __truediv__(self, other):
        phn.Term(self, other, '/')
        
    def __rtruediv__(self, other):
        phn.Term(other, self, '/')
        
    def __pow__(self, other):
        phn.Term(self, other, '^')