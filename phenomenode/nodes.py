# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import Variables
from .context import ContextStack
from .functions import functions as f

__all__ = ('Tank', 'Bulk', 'Mix', 'Mixer', 'Split')

class Tank(Node):
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
        assert feed.variables == index.equilibrium
        product.variables = index.bulk
    
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
            f"{f.sum}p {F_in} = {F_out}",
            f"{f.sum}p enthalpy({T_in}, {F_in}) = {H_out}",
            f"{P_in} = {P_out}",
        ]
        

class Mix(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        product, = self.outs
        index = self.index
        for i in self.ins: assert i.variables == index.bulk
        product.variables = index.bulk
    
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
            f"{f.sum}i {F_ins} = {F_out}",
            f"{f.sum}i {H_ins} = {H_out}",
            f"min|i {P_ins} = {P_out}",
        ]
    
    
class Mixer(Node, tag='x'):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        self.bulks = []
        equilibrium = self.index.equilibrium
        ins = []
        for i in self.ins:
            if i.variables == equilibrium:
                bulk = Bulk(ins=i)
                self.bulks.append(bulk)
                ins.append(bulk.outs[0])
            else:
                ins.append(i)
        self.mix = Mix(ins=ins, outs=self.outs[0])
      

class Split(Node):
    n_ins = 1
    n_outs = 2
    
    def load(self):
        inlet, = self.ins
        outs = self.outs
        for i in outs: i.variables = inlet.variables
    
    def equation_list(self, fmt=None, context=None, stack=None, inbound=None):
        if stack: context = self.contextualize(context)
        inlet, = self.ins.framed_variables(context)
        top, bottom = self.outs.framed_variables(context, inbound=inbound)
        index = self.index
        split = index.split
        vars = self.ins[0].variables
        if index.Fc in vars:
            F_in = inlet.Fc(fmt)
            F_top = top.Fc(fmt)
            F_bottom = bottom.Fc(fmt)
            equations = [
                f"{F_in}{f.x}{split} = {F_top}",
                f"{F_in}{f.x}(1 - {split}) = {F_bottom}"
            ]
        elif index.Fcp in vars:
            F_in = inlet.Fcp(fmt)
            F_top = top.Fcp(fmt)
            F_bottom = bottom.Fcp(fmt)
            equations = [
                f"{F_in}{f.x}{split} = {F_top}",
                f"{F_in}{f.x}(1 - {split}) = {F_bottom}"
            ]
        if index.H in vars:
            H_in = inlet.H(fmt)
            H_top = top.H(fmt)
            H_bottom = bottom.H(fmt)
            equations.extend([
                f"{H_in}{f.x}{split} = {H_top}",
                f"{H_in}{f.x}(1 - {split}) = {H_bottom}"
            ])
        elif index.T in vars:
            T_in = inlet.T(fmt)
            T_top = top.T(fmt)
            T_bottom = bottom.T(fmt)
            equations.append(
                f"{T_in} = {T_top} = {T_bottom}"
            )
        if index.P in vars:
            P_in = inlet.P(fmt)
            P_top = top.P(fmt)
            P_bottom = bottom.P(fmt)
            equations.append(
                f"{P_in} = {P_top} = {P_bottom}"
            )
        return equations
                
    