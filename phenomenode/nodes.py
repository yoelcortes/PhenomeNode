# -*- coding: utf-8 -*-
"""
"""
from .phenomenode import PhenomeNode
from .edge import Stream
from .variable import ActiveVariables

class SurgeTank(PhenomeNode):
    n_ins = 1
    n_outs = 1
    etype = Stream
    
    def equations(self, fmt=None, context=None, start=None):
        head, dlim, start = self._equations_format(start)
        inlet, = self.ins.framed_variables(context)
        outlet, = self.outs.framed_variables(context)
        return head + dlim.join([f"{i(fmt)} = {j(fmt)}"
                                 for i, j in zip(inlet, outlet)])

class Bulk(PhenomeNode):
    n_ins = 1
    n_outs = 1
    etype = Stream
    
    def load(self):
        feed, = self.ins
        product, = self.outs
        assert feed.variables == {feed.Fcp, feed.T, feed.P}
        product.variables = ActiveVariables(product.Fc, product.H, product.P)
    
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
        

class Mix(PhenomeNode):
    n_ins = 2
    n_outs = 1
    etype = Stream
    
    def load(self):
        product, = self.outs
        for i in self.ins: assert i.variables == {i.Fc, i.H, i.P}
        product.variables = ActiveVariables(product.Fc, product.H, product.P)
    
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
    
    
class Mixer(PhenomeNode, tag='mr'):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        self.bulks = []
        for n, i in enumerate(self.ins):
            self.bulks.append(
                Bulk(n, i)
            )
        self.mix = Mix(0, ins=[i.outs[0] for i in self.bulks])
        