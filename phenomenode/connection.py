# -*- coding: utf-8 -*-
"""
"""
from typing import NamedTuple, Optional

__all__ = ('Connection',)

class Connection:
    __slots__ = ('phenomenode', 'varnode')
    def __init__(self, phenomenode, varnode):
        self.phenomenode = phenomenode
        self.varnode = varnode
    
    def __hash__(self):
        return hash((self.phenomenode, self.varnode))
    
    def __eq__(self, other):
        return (self.phenomenode, self.varnode) == (other.phenomenode, other.varnode)
    
