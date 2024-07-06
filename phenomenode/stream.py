# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020-2023, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
This module includes classes and functions concerning Stream objects.
"""
from __future__ import annotations
from .varnode import VarNode
from .variable import index as I

__all__ = ('Stream',)
        

# %% Utilities

def as_streams(streams):
    isa = isinstance
    if isa(streams, Stream):
        return [streams]
    else:
        loaded_streams = []
        for i in streams:
            if isa(i, Stream):
                s = i
            elif i is None:
                s = Stream(None, None)
            else:
                raise ValueError('only stream objects are valid')
            loaded_streams.append(s)
    return loaded_streams
    
# %% Streams

class Stream:
    """Create a stream which defines associated variables."""
    __slots__ = ('Fcp', 'T', 'P', 'dHdE', 'DeltaE')
    
    def __init__(self):
        self.Fcp = VarNode(I.Fcp)
        self.T = VarNode(I.T)
        self.P = VarNode(I.P)
        self.dHdE = VarNode(I.dHdE)
        self.DeltaE = VarNode(I.DeltaE)
    
    def define_energy_parameter(self, name):
        for node in (self.dHdE, self.DeltaE):
            variable = node.variable
            node.variable = variable.copy(name=variable.name.replace('E', name))
    
    def no_energy_parameter(self):
        self.dHdE = 0
        self.DeltaE = 0
    
    @property
    def varnodes(self):
        if self.DeltaE == 0:
            return (self.Fcp, self.T, self.P)
        else:
            return (self.Fcp, self.T, self.P, self.dHdE, self.DeltaE)
    
    def __iter__(self):
        return iter(self.varnodes)
    
    def __repr__(self):
        return f"{type(self).__name__}({self.Fcp!r}, {self.T!r}, {self.P!r})"
