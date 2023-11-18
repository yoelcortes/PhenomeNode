# -*- coding: utf-8 -*-
"""
"""
from typing import NamedTuple, Optional
from .phenomenode import PhenomeNode
from .varnode import VarNode

__all__ = ('Connection',)

class Connection(NamedTuple):
    source: Optional[PhenomeNode|VarNode] = None
    sink: Optional[PhenomeNode|VarNode] = None
