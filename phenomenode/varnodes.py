# -*- coding: utf-8 -*-
"""
"""
from .varnode import VarNode

__all__ = ('Variables')

class VarNodes:
    
    def __init__(self, varnodes):
        self.varnodes = tuple([i if isinstance(i, VarNode) else VarNode(i) 
                               for i in varnodes])
    
    def __repr__(self):
        return f"{type(self).__name__}({self.variables})"