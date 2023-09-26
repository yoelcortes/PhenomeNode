# -*- coding: utf-8 -*-
"""
"""
from typing import NamedTuple
from .node import PhenomeNode
from .edge import Edge

__all__ = ('Connection',)

class Connection(NamedTuple):
    source: PhenomeNode
    source_index: int
    edge: Edge
    sink_index: int
    sink: PhenomeNode
    
    @classmethod
    def from_edge(cls, edge):
        return cls(
            source:=edge.source,
            source.outs.index(edge) if source else None,
            edge,
            sink.ins.index(edge) if (sink:=edge.sink) else None,
            sink,
        )
