# -*- coding: utf-8 -*-
"""
"""

__all__ = ('AbstractMethod',)

class AbstractMethodType:
    __slots__ = ()
    
    @property
    def __name__(self): return "AbstractMethod"
    def __new__(self): return AbstractMethod
    def __call__(self, *args, **kwargs): return NotImplemented
    def __bool__(self): return False
    def __repr__(self): return "AbstractMethod"

AbstractMethod = object.__new__(AbstractMethodType)