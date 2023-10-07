# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .quantity import Quantity

__all__ = ('Term',)

class Term(Quantity):
    __slots__ = ('left', 'right', 'operator')
    order_of_operations = {
        '+': 0,
        '-': 1,
        '·': 2,
        '*': 2,
        '/': 3,
        '^': 4,
    }
    
    def __init__(self, left, right, operator):
        self.left = left
        self.right = right
        self.operator = '·' if operator == '*' else operator
        
    def variables(self):
        terms = {self.left, self.right}
        variables = []
        while terms:
            for i in tuple(terms):
                if isinstance(i, phn.Variable):
                    variables.append(i)
                    terms.remove(i)
                elif isinstance(i, phn.FunctionCall):
                    terms.update(i.parameters)
                else:
                    terms.update([i.left, i.right])
        return variables
                
    def __repr__(self):
        left = self.left
        right = self.right
        operator = self.operator
        order = self.order_of_operations
        priority = order[operator]
        if isinstance(left, Term):
            if priority > order[left.operator]:
               left = f"({left})"
        if isinstance(right, Term):
            if priority > order[right.operator]:
               right = f"({right})"
        return f"{left} {operator} {right}"