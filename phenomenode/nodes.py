# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .node import Node
from .variable import Variables, Variable
from .function import function_index as f
from .equality import Equality as EQ
from .terminal import Terminal

__all__ = ('Bulk', 'Mix', 'Mixer', 'Split', 'LLEStage', 'Partition', 'LLE')

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
        i = self.index
        return [
            EQ(f.sum[i.phases](inlet.Fcp), outlet.Fc),
            EQ(f.enthalpy(inlet.Fcp, inlet.T, inlet.P), outlet.H),
            EQ(inlet.P, outlet.P),
        ]
        

class Mix(Node):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        ins = self.ins
        product, = self.outs
        invars = ins.variables.dict()
        variables = []
        goodvars = {'Fc', 'H', 'Q', 'P'}
        mixed_variables = []
        for i in invars:
            if i in goodvars:
                variables.append(invars[i])
                mixed_variables.append(i)
            else:
                raise ValueError("'{i}' is not mixable")
        self.mixed_variables = frozenset(mixed_variables)
        product.variables = Variables(*variables)
        
    def equations(self):
        ins = self.inlet_variables(family=True)
        outlet, = self.outlet_variables()
        i = self.index
        mixed_variables = self.mixed_variables
        eqs = []
        if 'Fc' in mixed_variables:
            eqs.append(
                EQ(f.sum[i.inlets](ins.Fci), outlet.Fc)
            )
        if 'H' in mixed_variables:
            if 'Q' in mixed_variables:
                left = f.sum(ins.Hi + ins.Qi)
            else:
                left = f.sum(ins.Hi)
            eqs.append(
                EQ(left, outlet.H)
            )
        elif 'Q' in mixed_variables:
            eqs.append(
                EQ(f.sum(ins.Qi), outlet.Q)
            )
        if 'P' in mixed_variables:
            eqs.append(
                EQ(f.min(ins.Pi), outlet.P)
            )
        return eqs

    
class Mixer(Node, tag='x'):
    n_ins = 2
    n_outs = 1
    
    def load(self):
        self.bulks = []
        ins = []
        for i in self.ins:
            if hasattr(i.variables, 'T'):
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
            equations = [
                EQ(inlet.Fc * split, top.Fc),
                EQ(inlet.Fc * (1 - split), bottom.Fc)
            ]
        elif index.Fcp in vars:
            equations = [
                EQ(inlet.Fcp * split, top.Fcp),
                EQ(inlet.Fcp * (1 - split), bottom.Fcp)
            ]
        if index.H in vars:
            equations = [
                EQ(inlet.H * split, top.H),
                EQ(inlet.H * (1 - split), bottom.H)
            ]
        elif index.T in vars:
            equations = [
                EQ(inlet.T, top.T, bottom.T)
            ]
        if index.P in vars:
            equations = [
                EQ(inlet.P, top.P, bottom.P)
            ]
        return equations


class LLEStage(Node, tag='z'):
    n_ins = 2
    n_outs = 2
    
    def prepare(self, ins, outs, T=None, P=None, Q=None):
        self.init_ins(ins)
        self.init_outs(outs)
        self.T = T
        self.P = P
        self.Q = Q
    
    def load(self):
        index = self.index
        specs = []
        matches = [(0, 0, [index.Fc]), (0, 3, [index.Fc])]
        if self.T:
            specs.append(index.T)
            matches.extend([
                (1, i, [index.T]) for i in range(3)
            ])
        if self.P:
            specs.append(index.P)
            matches.extend([
                (1, i, [index.P]) for i in range(3)
            ])
        if self.Q:
            self.ins.append(
                phn.Edge(variables=Variables(index.Q))
            )
            matches.append(
                (0, 0, [index.H])
            )
        self.mixer = Mixer(self.ins)
        if self.T and self.Q: 
            raise ValueError('cannot specify both temperature and duty')
        elif not (self.T or self.Q):
            raise ValueError('must either temperature or duty')
        specs = Variables(*specs)
        if specs:
            self.ins.append(
                phn.Edge(variables=specs)
            )
        self.lle_enter = Terminal([self.mixer.outs[0], self.ins[-1]], matches=matches)
        self.lle = LLE(self.lle_enter.outs[0])
        self.lle_exit = Terminal(
            [self.lle.outs[0], self.lle_enter.outs[3]], 
            matches=[(0, 0, self.lle.outs[0].variables),
                     (1, 0, self.lle_enter.outs[3].variables)]
        )
        self.partition = Partition(self.lle_exit.outs[0])
        self.top_exit = Terminal(
            [self.partition.outs[0], self.lle_enter.outs[1]], 
            matches=[(0, 0, self.partition.outs[0].variables),
                     (1, 0, self.lle_enter.outs[1].variables)]
        )
        self.bottom_exit = Terminal(
            [self.partition.outs[1], self.lle_enter.outs[2]], 
            matches=[(0, 0, self.partition.outs[1].variables),
                     (1, 0, self.lle_enter.outs[2].variables)]
        )


class LLE(Node, tag='l'):
    n_ins = 1
    n_outs = 1
    
    def load(self):
        inlet, = self.ins
        outlet, = self.outs
        index = self.index
        if index.H in inlet.variables:
            outlet.variables = Variables(index.KLc, index.L, index.T)
        else:
            outlet.variables = Variables(index.KLc, index.L)
    
    def equations(self):
        inlet, = self.inlet_variables()
        outlet,  = self.outlet_variables()
        if hasattr(inlet, 'H'):
            lle = EQ(f.lle(*inlet), outlet.KLc & outlet.L & outlet.T)
        else:
            lle = EQ(f.lle(*inlet), outlet.KLc & outlet.L)
        return [lle]


class Partition(Node, tag='ϕ'):
    n_ins = 1
    n_outs = 2
    
    def load(self):
        inlet, = self.ins
        top, bottom = self.outs
        index = self.index
        if not inlet.variables.difference([index.KVc, index.V, index.T, index.Fc]):
            self.vle = True
            self.lle = False
        elif not inlet.variables.difference([index.KLc, index.L, index.T, index.Fc]):
            self.vle = False
            self.lle = True
        else:
            raise ValueError('inlet variables must be partition coefficients and a phase fraction')
        top.variables = bottom.variables = Variables(index.Fc)
    
    def equations(self):
        inlet, = self.inlet_variables()
        top, bottom = self.outlet_variables()
        if self.vle:
            return [
                EQ(top.Fc, inlet.Fc * (1 - inlet.V) / (inlet.V * (inlet.KVc - 1) + 1)),
                EQ(bottom.Fc, inlet.Fc * inlet.V / (inlet.V * (inlet.KVc - 1) + 1))
            ]
        elif self.lle:
            return [
                EQ(top.Fc, inlet.Fc * (1 - inlet.L) / (inlet.L * (inlet.KLc - 1) + 1)),
                EQ(bottom.Fc, inlet.Fc * inlet.L / (inlet.L * (inlet.KLc - 1) + 1))
            ]
        else:
            raise RuntimeError('unknown error')
            
    