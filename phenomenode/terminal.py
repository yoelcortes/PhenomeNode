# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import Variable, Variables
from .equality import Equality as EQ
from .graphics import terminal_graphics

__all__ = ('Terminal',)

class Terminal(Node):
    graphics = terminal_graphics
    
    
    @classmethod
    def repeat(cls, inlet, n_outs, outs=None, name=None, index=None):
        return cls.__new__(cls,
            inlet, outs, name, index, 
            matches=[(0, i, inlet.variables) for i in range(n_outs)]
        )
    
    @classmethod
    def distribute(cls, inlet, variables, n_outs, outs=None, name=None, index=None):
        return cls.__new__(cls,
            inlet, outs, name, index, 
            matches=[(0, 0, [i for i in inlet.variables]),
                     *[(0, i, variables) for i in range(1, n_outs)]]
        )
    
    @classmethod
    def merge(cls, ins, outlet=None, name=None, index=None):
        return cls.__new__(cls,
            ins, outlet, name, index, 
            matches=[(i, 0, j.variables) for i, j in enumerate(ins)]
        )
    
    @classmethod
    def pop(cls, inlet, variables, n_outs, outs=None, name=None, index=None):
        return cls.__new__(cls,
            inlet, outs, name, index, 
            matches=[(0, 0, [i for i in inlet.variables if i not in variables]),
                     *[(0, i, variables) for i in range(1, n_outs)]]
        )
    
    @classmethod
    def filter(cls, inlet, variables, outs=None, name=None, index=None):
        return cls.__new__(cls,
            inlet, outs, name, index, 
            matches=[(0, 0, [i for i in inlet.variables if i not in variables])]
        )
    
    def prepare(self, ins, outs, matches):
        self.n_ins = max([i[0] for i in matches]) + 1
        self.n_outs = max([i[1] for i in matches]) + 1
        self.init_ins(ins)
        self.init_outs(outs, Variables())
        self.matches = matches
        ins = self.ins
        outs = self.outs
        outlet_variables = {i: [] for i in range(self.n_outs)}
        # inlet_variables = {i: [] for i in range(self.n_ins)}
        for i, o, variables in matches:
            inlet = ins[i]
            # invars = inlet_variables[i]
            outvars = outlet_variables[o]
            for v in variables:
                if v in inlet.variables:
                    # invars.append(v)
                    outvars.append(v)
                else:
                    raise ValueError(f'inlet has no variable {v}')
        for i, j in outlet_variables.items():
            outs[i].variables = Variables(*j)
        # for i, j in inlet_variables.items():
        #     ins[i].variables = Variables(*j)
        
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
                
