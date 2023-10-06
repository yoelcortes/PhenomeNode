# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn

__all__ = ('Quantity',)

class Quantity:
    
    def __add__(self, other):
        phn.Expression(self, other, '+')
        
    def __sub__(self, other):
        phn.Expression(self, other, '-')
        
    def __mul__(self, other):
        phn.Expression(self, other, '*')
        
    def __truediv__(self, other):
        phn.Expression(self, other, '/')
        
    def __pow__(self, other):
        phn.Expression(self, other, '^')