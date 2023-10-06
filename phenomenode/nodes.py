# -*- coding: utf-8 -*-
"""
"""
from .node import Node
from .variable import Variables, Variable
from .context import ContextStack
from .functions import functions as f

__all__ = ('Tank', 'Bulk', 'Mix', 'Mixer', 'Split')

class Tank(Node):
    n_ins = 1
    n_outs = 1
    
    def equations(self):
        inlet, = self.inlet_variables()
        outlet, = self.outlet_variables()
        return [f"{i} = {j}" for i, j in zip(inlet, outlet)]

class Bulk(Node):
    n_ins = 1
    n_outs = 1
    
    def load(self):
        feed, = self.ins
        product, = self.outs
        index = self.index
        assert feed.variables == index.equilibrium
        product.variables = index.bulk
    
    def equations(self):
        inlet, = self.inlet_variables()
        outlet, = self.outlet_variables()
        return [
            f"{f.sum}p {inlet.Fcp} = {outlet.Fc}",
            f"{f.sum}p enthalpy({inlet.Fcp}, {inlet.T}, {inlet.P}) = {outlet.H}",
            f"{inlet.P} = {outlet.P}",
        ]
        

class Mix(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        product, = self.outs
        index = self.index
        for i in self.ins: assert i.variables == index.bulk
        product.variables = index.bulk
    
    def equations(self):
        ins = self.inlet_variables(family=True)
        outlet, = self.outlet_variables()
        F_ins = ins.Fci
        F_out = outlet.Fc
        H_ins = ins.Hi
        H_out = outlet.H
        P_ins = ins.Pi
        P_out = outlet.P
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
    
    def equations(self, fmt=None, context=None, inbound=None):
        inlet, = self.inlet_variables()
        top, bottom = self.outlet_variables()
        index = self.index
        split = index.split
        vars = self.ins[0].variables
        if index.Fc in vars:
            F_in = inlet.Fc
            F_top = top.Fc
            F_bottom = bottom.Fc
            equations = [
                f"{F_in}{f.x}{split} = {F_top}",
                f"{F_in}{f.x}(1 - {split}) = {F_bottom}"
            ]
        elif index.Fcp in vars:
            F_in = inlet.Fcp
            F_top = top.Fcp
            F_bottom = bottom.Fcp
            equations = [
                f"{F_in}{f.x}{split} = {F_top}",
                f"{F_in}{f.x}(1 - {split}) = {F_bottom}"
            ]
        if index.H in vars:
            H_in = inlet.H
            H_top = top.H
            H_bottom = bottom.H
            equations.extend([
                f"{H_in}{f.x}{split} = {H_top}",
                f"{H_in}{f.x}(1 - {split}) = {H_bottom}"
            ])
        elif index.T in vars:
            T_in = inlet.T
            T_top = top.T
            T_bottom = bottom.T
            equations.append(
                f"{T_in} = {T_top} = {T_bottom}"
            )
        if index.P in vars:
            P_in = inlet.P
            P_top = top.P
            P_bottom = bottom.P
            equations.append(
                f"{P_in} = {P_top} = {P_bottom}"
            )
        return equations


class Stage(Node):
    n_ins = 1
    n_outs = 2
    
    def prepare(self, phases):
        if len(phases) != 2:
            raise ValueError('stage must have 2 and only 2 phases')
        if 'g' in phases:
           self.vle = True
           self.lle = False
        elif 'L' in phases:
           self.vle = False
           self.lle = True
        else:
            raise ValueError(f'invalid phases {phases!r}')
    
    def load(self):
        pass
    
    def equations(self):
        pass


class VLE(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        outlet, = self.outs
        index = self.index
        outlet.variables = (index.KVc, index.V)
        
    def equations(self):
        inlet, specs = self.inlet_variables()
        df = len(specs)
        if df != 2:
            raise ValueError('must specify 2 and only 2 degrees of freedom; {df} specified')
        outlet,  = self.outlet_variables()
        inputs = [inlet.Fc]
        if hasattr(specs, 'Q'):
            inputs.append(f"{inlet.H} + {specs.Q}")
        for i in ('T', 'P', 'V'):
            if hasattr(specs, i): inputs.append(f"{getattr(specs, i)}")
        inputs = ', '.join(inputs)
        vle = f"VLE({inputs}) = {outlet.KVc}"
        if not hasattr(specs, 'V'): vle += ", {outlet.V}"
        return [vle]
    

class LLE(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        outlet, = self.outs
        index = self.index
        outlet.variables = Variables(index.KLc, index.L)
    
    def equations(self):
        inlet, specs = self.inlet_variables()
        df = len(specs)
        if df != 2:
            raise ValueError('must specify 2 and only 2 degrees of freedom; {df} specified')
        outlet,  = self.outlet_variables()
        inputs = [inlet.Fc]
        if hasattr(specs, 'Q'):
            inputs.append(f"{inlet.H} + {specs.Q}")
        for i in ('T', 'P', 'V'):
            if hasattr(specs, i): inputs.append(f"{getattr(specs, i)}")
        inputs = ', '.join(inputs)
        vle = f"LLE({inputs}) = {outlet.KVc}"
        if not hasattr(specs, 'V'): vle += ", {outlet.V}"
        return [vle]


class Partition(Node):
    n_ins = 1
    n_outs = 2
    
    def load(self):
        inlet, = self.ins
        top, bottom = self.outs
        index = self.index
        if inlet.variables == Variables(index.KVc, index.V):
            self.vle = True
            self.lle = False
        elif inlet.variables == Variables(index.KLc, index.L):
            self.vle = False
            self.lle = True
        else:
            raise ValueError('inlet variables must be partition coefficients and a phase fraction')
        top.variables = bottom.variables = Variable(index.Fc)
    
    def equations(self):
        inlet, = self.inlet_variables()
        top, bottom = self.outlet_variables()
        if self.vle:
            return [
                f"{top.Fc} = {inlet.Fc}(1 - {inlet.V}) / ({inlet.V} * ({inlet.KVc} - 1) + 1)"
                f"{bottom.Fc} = {inlet.Fc}{inlet.V} / ({inlet.V} * ({inlet.KVc} - 1) + 1)"
            ]
        elif self.lle:
            return [
                f"{top.Fc} = {inlet.Fc}(1 - {inlet.L}) / ({inlet.L} * ({inlet.KLc} - 1) + 1)"
                f"{bottom.Fc} = {inlet.Fc}{inlet.L} / ({inlet.L} * ({inlet.KLc} - 1) + 1)"
            ]
        else:
            raise RuntimeError('unknown error')
            
    