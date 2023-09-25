# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import ActiveVariables

__all__ = ('SurgeTank', 'Bulk', 'Mix', 'Mixer')

class SurgeTank(Node):
    n_ins = 1
    n_outs = 1
    
    def equations(self, fmt=None, context=None, start=None):
        head, dlim, start = self._equations_format(start)
        inlet, = self.ins.framed_variables(context)
        outlet, = self.outs.framed_variables(context)
        return head + dlim.join([f"{i(fmt)} = {j(fmt)}"
                                 for i, j in zip(inlet, outlet)])

class Bulk(Node):
    n_ins = 1
    n_outs = 1
    
    def load(self):
        feed, = self.ins
        product, = self.outs
        index = self.index
        assert feed.variables == {index.Fcp, index.T, index.P}
        product.variables = ActiveVariables(index.Fc, index.H, index.P)
    
    def equations(self, fmt=None, context=None, start=None):
        head, dlim, start = self._equations_format(start)
        inlet, = self.ins.framed_variables(context)
        outlet, = self.outs.framed_variables(context)
        F_in = inlet.Fcp(fmt)
        F_out = outlet.Fc(fmt)
        T_in = inlet.T(fmt)
        H_out = outlet.H(fmt)
        P_in = inlet.P(fmt)
        P_out = outlet.P(fmt)
        return head + dlim.join([
            f"sum|p {F_in} = {F_out}",
            f"sum|p Enthalpy({T_in}, {F_in}) = {H_out}",
            f"{P_in} = {P_out}",
        ])
        

class Mix(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        product, = self.outs
        index = self.index
        bulk_variables = {index.Fc, index.H, index.P}
        for i in self.ins: assert i.variables == bulk_variables
        product.variables = ActiveVariables(index.Fc, index.H, index.P)
    
    def equations(self, fmt=None, context=None, start=None):
        head, dlim, start = self._equations_format(start)
        ins = self.ins.framed_variables(context, family=True)
        outlet, = self.outs.framed_variables(context)
        F_ins = ins.Fci(fmt)
        F_out = outlet.Fc(fmt)
        H_ins = ins.Hi(fmt)
        H_out = outlet.H(fmt)
        P_ins = ins.Pi(fmt)
        P_out = outlet.P(fmt)
        return head + dlim.join([
            f"sum|i {F_ins} = {F_out}",
            f"sum|i {H_ins} = {H_out}",
            f"min|i {P_ins} = {P_out}",
        ])
    
    
class Mixer(Node, tag='mr'):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        self.bulks = []
        for n, i in enumerate(self.ins):
            self.bulks.append(
                Bulk(n, i)
            )
        self.mix = Mix(0, ins=[i.outs[0] for i in self.bulks])
        