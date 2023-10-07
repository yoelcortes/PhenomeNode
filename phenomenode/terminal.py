# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import Variable, Variables
from .equality import Equality as EQ

__all__ = ('Terminal',)

class Terminal(Node):
    
    def prepare(self, ins, outs, matches):
        self.n_ins = max([i[0] for i in matches]) + 1
        self.n_outs = max([i[1] for i in matches]) + 1
        self.init_ins(ins)
        self.init_outs(outs, Variables())
        self.matches = matches
        ins = self.ins
        outs = self.outs
        outlet_variables = {i: [] for i in range(self.n_outs)}
        for i, o, variables in matches:
            inlet = ins[i]
            outvars = outlet_variables[o]
            for v in variables:
                if v in inlet.variables:
                    outvars.append(v)
                else:
                    raise ValueError(f'inlet has no variable {v}')
        for i, j in outlet_variables.items():
            outs[i].variables = Variables(*j)
        
    def equations(self):
        ins = self.inlet_variables()
        outs = self.outlet_variables()
        eqs = []
        for i, o, variables in self.matches:
            inlet = ins[i]
            outlet = outs[o]
            for v in variables:
                eqs.append(
                    EQ(getattr(inlet, str(v)), getattr(outlet, str(v)))
                )
        return eqs
                
