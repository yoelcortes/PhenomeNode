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
from .variable import variable_index as index

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
    __slots__ = ('Fcp', 'T', 'P', 'varnodes')
    
    def __init__(self):
        self.Fcp = Fcp = VarNode(index.Fcp)
        self.T = T = VarNode(index.T)
        self.P = P = VarNode(index.P)
        self.varnodes = (Fcp, T, P)
        
    def __repr__(self):
        return f"{type(self).__name__}({self.Fcp!r}, {self.T!r}, {self.P!r}))"
