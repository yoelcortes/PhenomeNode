# -*- coding: utf-8 -*-
"""
"""
from .phenomenode import PhenomeNode
from .stream import Stream, as_streams

__all__ = ('Unit',)

class Unit(PhenomeNode):
    default_ins = ()
    default_outs = ()
    n_ins = 1
    n_outs = 1
    
    def __new__(cls, ins=None, outs=None, name=None, index=None, **kwargs):
        ins = [Stream() for i in range(cls.n_ins)] if ins is None else as_streams(ins)
        outs = [Stream() for i in range(cls.n_outs)] if outs is None else as_streams(outs)
        self = super().__new__(cls, ins, outs, name, **kwargs)
        return self
    