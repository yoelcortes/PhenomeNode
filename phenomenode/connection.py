# -*- coding: utf-8 -*-
"""
"""
from typing import NamedTuple, Optional
from .phenomenode import PhenomeNode
from .varnode import VarNode

__all__ = ('Connection',)

class Connection:
    __slots__ = ('source', 'sink')
    def __init__(self, source, sink):
        self.source = source
        self.sink = sink
    
    @property
    def phenomenode(self):
        if isinstance(self.source, PhenomeNode):
            return self.source
        else:
            return self.sink
        
    @property
    def varnode(self):
        if isinstance(self.source, VarNode):
            return self.source
        else:
            return self.sink
    
    
