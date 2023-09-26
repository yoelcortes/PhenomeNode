# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import Variables
from .context import ContextStack

__all__ = ('SurgeTank', 'Bulk', 'Mix', 'Mixer')

class SurgeTank(Node):
    n_ins = 1
    n_outs = 1
    
    def equation_list(self, fmt=None, context=None, stack=None, inbound=None):
        if stack: context = self.contextualize(context)
        inlet, = self.ins.framed_variables(context)
        outlet, = self.outs.framed_variables(context, inbound)
        return [f"{i(fmt)} = {j(fmt)}" for i, j in zip(inlet, outlet)]

class Bulk(Node):
    n_ins = 1
    n_outs = 1
    
    def load(self):
        feed, = self.ins
        product, = self.outs
        index = self.index
        assert feed.variables == (index.Fcp, index.T, index.P)
        product.variables = Variables(index.Fc, index.H, index.P)
    
    def equation_list(self, fmt=None, context=None, stack=None, inbound=None):
        if stack: context = self.contextualize(context)
        inlet, = self.ins.framed_variables(context)
        outlet, = self.outs.framed_variables(context, inbound=inbound)
        F_in = inlet.Fcp(fmt)
        F_out = outlet.Fc(fmt)
        T_in = inlet.T(fmt)
        H_out = outlet.H(fmt)
        P_in = inlet.P(fmt)
        P_out = outlet.P(fmt)
        return [
            f"sum|p {F_in} = {F_out}",
            f"sum|p Enthalpy({T_in}, {F_in}) = {H_out}",
            f"{P_in} = {P_out}",
        ]
        

class Mix(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        product, = self.outs
        index = self.index
        bulk_variables = (index.Fc, index.H, index.P)
        for i in self.ins: assert i.variables == bulk_variables
        product.variables = Variables(index.Fc, index.H, index.P)
    
    def equation_list(self, fmt=None, context=None, stack=None, inbound=None):
        if stack: context = self.contextualize(context)
        ins = self.ins.framed_variables(context, family=True)
        outlet, = self.outs.framed_variables(context, inbound=inbound)
        F_ins = ins.Fci(fmt)
        F_out = outlet.Fc(fmt)
        H_ins = ins.Hi(fmt)
        H_out = outlet.H(fmt)
        P_ins = ins.Pi(fmt)
        P_out = outlet.P(fmt)
        return [
            f"sum|i {F_ins} = {F_out}",
            f"sum|i {H_ins} = {H_out}",
            f"min|i {P_ins} = {P_out}",
        ]
    
    
class Mixer(Node, tag='mr'):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        self.bulks = []
        index = self.index
        spread_variables = (index.Fcp, index.T, index.P)
        ins = []
        for n, i in enumerate(self.ins):
            if i.variables == spread_variables:
                bulk = Bulk(n, ins=i)
                self.bulks.append(bulk)
                ins.append(bulk.outs[0])
            else:
                ins.append(i)
        self.mix = Mix(0, ins=ins, outs=self.outs[0])
        