# -*- coding: utf-8 -*-
"""
"""
from sympy import symbols, IndexedBase, Idx

M = IndexedBase('M')

i, j = symbols('i j=0', cls=Idx)

M[i, j]
