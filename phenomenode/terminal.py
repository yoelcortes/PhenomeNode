# -*- coding: utf-8 -*-
"""
"""
from .phenomenode import Node
from .variables import Variables

__all__ = ('Terminal',)

class Terminal(Node):
    n_ins = 1
    
    def prepare(self, ins, outs, allocation):
        self.n_outs = len(allocation)
        self.init_ins(ins)
        self.init_outs(outs)
        inlet, = self.ins
        outs = self.outs
        for i, variables in enumerate(allocation):
            outlet_variables = []
            for v in variables:
                if hasattr(inlet, v):
                    outlet_variables.append(getattr(inlet, v))
                else:
                    raise ValueError(f'inlet has no variable {v}')
            outs[i].variables = Variables(*outlet_variables)
        
    def equations(self):
        inlet, = self.inlet_variables()
        outs = self.outlet_variables()
        return [f"{getattr(inlet, str(v))} = {v}" for outlet in outs for v in outlet]
                
