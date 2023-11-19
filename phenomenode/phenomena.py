# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .phenomenode import PhenomeNode
from .variable import Variables, Variable
from .function import function_index as f
from .equality import Equality as EQ

__all__ = (
    'BulkEnthalpy', 
    'BulkMaterial',
    'Mixer', 
    'Splitter', 
    'VLEStage'
    'LLEStage', 
    'LLE', 'VLE'
)

class BulkEnthalpy(PhenomeNode):
    default_ins = 'H'
    default_outs = 'H'
    
    def load(self):
        feeds = self.ins
        product, = self.outs
        index = self.index
        for i in [*feeds, product]: assert i.variable == index.H
    
    def equations(self):
        Hi, = self.inlet_variables(family=True)
        H, = self.outlet_variables()
        return [EQ(f.sum[self.index.inlets](Hi), H)]


class Enthalpy(PhenomeNode):
    default_ins = ['Fcp', 'T', 'P']
    default_outs = 'H'
    
    def equations(self):
        Fcp, T, P = self.inlet_variables()
        H = self.outlet_variables()
        return [EQ(f.enthalpy(Fcp, T, P), H)]
    
    
class BulkMaterial(PhenomeNode):
    default_ins = 'Fcp'
    default_outs = 'Fc'
    
    def equations(self):
        Fcpi, = self.inlet_variables(family=True)
        Fc, = self.outlet_variables()
        i = self.index
        return [EQ(f.sum[i.inlets, i.phases](Fcpi), Fc)]


class VLE(PhenomeNode):
    default_ins = ['Fc', 'H', 'P', 'V', 'KV', 'T']
    
    def equations(self):
        return [EQ(f.vle(*self.inlet_variables()), 0)]
    

class LLE(PhenomeNode):
    default_ins = ['Fc', 'T', 'P', 'L', 'KL', 'H']
    
    def equations(self):
        return [EQ(f.lle(*self.inlet_variables()), 0)]
    
    
class BubblePoint(PhenomeNode):
    default_ins = ['FLc', 'KV', 'T', 'P']
    
    def equations(self):
        return [EQ(f.bubble_point(*self.inlet_variables()), 0)]
    
    
class DewPoint(PhenomeNode):
    default_ins = ['FVc', 'KV', 'T', 'P']
    
    def equations(self):
        return [EQ(f.dew_point(*self.inlet_variables()), 0)]
    
    
class Mixer(PhenomeNode, tag='x'):
    def load(self):
        
        self.bulk_material = 
        self.bulk_enthalpy = 
        self.enthalpies = enthalpies = []
        index = self.index
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
        filtered = []
        if self.Q:
            self.ins.append(
                phn.Edge(variables=Variables(index.Q))
            )
        self.mixer = Mixer(self.ins)
        if self.T:
            specs.append(index.T)
            filtered.append(index.H)
        if self.P:
            specs.append(index.P)
            filtered.append(index.P)
        if self.T and self.Q: 
            raise ValueError('cannot specify both temperature and duty')
        elif not (self.T or self.Q):
            raise ValueError('must either temperature or duty')
        self.filter = Pylon.filter(self.mixer.outs[0], filtered)
        self.distribute = Pylon.distribute(self.filter.outs[0], [index.Fc], 2)
        specs = Variables(*specs)
        if specs:
            self.ins.append(
                phn.Edge(variables=specs)
            )
            self.outlet_specs = Pylon.repeat(self.ins[-1], 3)
            self.merge_specs = Pylon.merge([self.distribute.outs[0], self.outlet_specs.outs[0]])
            lle_inlet = self.merge_specs.outs[0]
        else:
            self.outlet_specs = Pylon.distribute(self.distribute.outs[0], [index.P], 3)
            lle_inlet = self.distribute.outs[0]
        self.lle = LLE(lle_inlet)
        lle_outlet = self.lle.outs[0]
        merge_T = index.T in lle_outlet.variables
        if merge_T:
            self.pop = Pylon.pop(lle_outlet, [index.T], 3)
            lle_outlet = self.pop.outs[0]
        self.partition_merge = Pylon.merge([lle_outlet, self.distribute.outs[1]])
        self.partition = Partition(self.partition_merge.outs[0])
        if merge_T:
            self.exit_merges = [Pylon.merge([i, j, k]) for i, j, k 
                                in zip(self.partition.outs, self.outlet_specs.outs[1:], self.pop.outs[1:])]
        else:
            self.exit_merges = [Pylon.merge([i, j]) for i, j in zip(self.partition.outs, self.outlet_specs.outs[1:])]


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
        top.variables = bottom.variables = Variables(index.Fcp)
    
    def equations(self):
        inlet, = self.inlet_variables()
        top, bottom = self.outlet_variables()
        index = self.index
        if self.vle:
            return [
                EQ(top.Fcp[index.liquid], inlet.Fc * (1 - inlet.V) / (inlet.V * (inlet.KVc - 1) + 1)),
                EQ(bottom.Fcp[index.liquid], inlet.Fc * inlet.V / (inlet.V * (inlet.KVc - 1) + 1))
            ]
        elif self.lle:
            return [
                EQ(top.Fcp[index.liquid], inlet.Fc * (1 - inlet.L) / (inlet.L * (inlet.KLc - 1) + 1)),
                EQ(bottom.Fcp[index.liquid], inlet.Fc * inlet.L / (inlet.L * (inlet.KLc - 1) + 1))
            ]
        else:
            raise RuntimeError('unknown error')
            
    