# -*- coding: utf-8 -*-
"""
"""
from .context import Inlet, Outlet
from .phenomenode import PhenomeNode
from .piping import Inlets, Outlets, Stream, as_streams

__all__ = ('Unit',)

class Unit(PhenomeNode):
    default_ins = ()
    default_outs = ()
    n_ins = 1
    n_outs = 1
    
    def __new__(cls, inlets=None, outlets=None, name=None, index=None, **kwargs):
        inlets = [Stream() for i in range(cls.n_ins)] if inlets is None else as_streams(inlets)
        outlets = [Stream() for i in range(cls.n_outs)] if outlets is None else as_streams(outlets)
        ins = sum([i.varnodes for i in inlets], ())
        outs = sum([i.varnodes for i in outlets], ())
        self = super().__new__(cls, ins, outs, name, inlets=inlets, outlets=outlets, **kwargs)
        return self
    
    def prepare(self, ins, outs, inlets, outlets, **kwargs):
        self.inlets = Inlets(self, inlets)
        self.outlets = Outlets(self, outlets)
        super().prepare(ins, outs, **kwargs)