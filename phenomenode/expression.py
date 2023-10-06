# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn

__all__ = ('Expression',)

class Expression:
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
        expressions = {self.left, self.right}
        variables = []
        while expressions:
            for i in tuple(expressions):
                if isinstance(i, phn.Variable):
                    variables.append(i)
                    expressions.remove(i)
                elif isinstance(i, phn.FunctionCall):
                    expressions.update(i.parameters)
                else:
                    expressions.update([i.left, i.right])
        return variables
                
    def __repr__(self):
        left = self.left
        right = self.right
        operator = self.operator
        order = self.order_of_operations
        priority = order[operator]
        if isinstance(left, Expression):
            if priority > order[left.operator]:
               left = f"({left})"
        if isinstance(right, Expression):
            if priority > order[right.operator]:
               right = f"({right})"
        return f"{left} {operator} {right}"