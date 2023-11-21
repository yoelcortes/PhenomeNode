# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .variable import Variables, Variable, variable_index as index
from .function import function_index as f
from .equality import Equality as EQ
from . unit import Unit

__all__ = (
    'Mixer', 
    # 'Splitter', 
    'MultiStageVLE',
    'VLEStage'
    # 'LLEStage', 
)

class Mixer(Unit, tag='x'):
    n_ins = 2
    n_outs = 1
    def load(self):
        feeds = self.ins
        product, = self.outs
        self.min_pressure = phn.MinPressure(ins=[i.P for i in feeds], outs=[product.P])
        self.bulk_material = bulk_material = phn.BulkMaterial(ins=[i.Fcp for i in feeds])
        self.enthalpies = enthalpies = [phn.Enthalpy(ins=[*i.varnodes]) for i in feeds]
        self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnthalpy(
            ins=[i.outs[0] for i in enthalpies]
        )
        self.equilibrium = phn.Equilibrium(
            ins=(bulk_material.outs[0], product.T, product.P, bulk_enthalpy.outs[0]),
            outs=[product.Fcp]
        )

class VLEStage(Unit, tag='f'):
    n_ins = 2
    n_outs = 2
    def load(self):
        Lfeed, Vfeed = feeds = self.ins
        self.enthalpies = enthalpies = [phn.Enthalpy(ins=[*i.varnodes]) for i in feeds]
        self.bulk_enthalpy = bulk_enthalpy = phn.BulkEnthalpy(
            ins=[i.outs[0] for i in enthalpies]
        )
        Hbulk, = bulk_enthalpy.outs
        vapor, liquid = self.outs
        vapor.P = Lfeed.P
        liquid.P = Vfeed.P
        vapor.T = liquid.T
        
        self.bulk_material = bulk_material = phn.BulkMaterial(ins=[Lfeed.Fcp, Vfeed.Fcp])
        self.vle = vle = phn.VLE(
            ins=(bulk_material.outs[0], vapor.T, vapor.P, index.V),
        )
        Fc, T, P, V = vle.ins
        KVc, = vle.outs
        self.vle_material_balance = vle_material_balance = phn.VLEMaterialBalance(
            ins=(Fc, KVc, V),
        )
        FVc, FLc = vle_material_balance.outs
        vapor.Fcp = FVc
        liquid.Fcp = FLc
        self.bulk_vapor = bulk_vapor = phn.BulkComponents(ins=[FVc])
        FV = bulk_vapor.outs
        self.bulk_liquid = bulk_liquid = phn.BulkComponents(ins=[FLc])
        FL = bulk_liquid.outs
        self.vapor_composition = vapor_composition = phn.Composition(ins=[FVc, FV], outs=[index.zV])
        zV, = vapor_composition.outs
        self.liquid_composition = liquid_composition = phn.Composition(ins=[FLc, FL], outs=[index.zV])
        zL, = liquid_composition.outs
        self.liquid_enthalpy = liquid_enthalpy = phn.Enthalpy(
            ins=[zL, T, P], outs=['hL'],
        )
        hL, = liquid_enthalpy.outs
        self.vapor_enthalpy = vapor_enthalpy = phn.Enthalpy(
            ins=[zV, T, P], outs=['hV'],
        )
        hV, = vapor_enthalpy.outs
        self.vle_energy_balance = vle_energy_balance = phn.VLEEnergyBalance(
            ins=[Hbulk, hL, hV, FL], outs=[V]
        )
        self.bubble_point = bubble_point = phn.BubblePoint(
            ins=[FLc, T, P, KVc],
        )
        self.dew_point = dew_point = phn.DewPoint(
            ins=[FVc, T, P, KVc],
        )
        
class MultiStageVLE(Unit, tag='v'):
    n_ins = 2
    n_outs = 2
    def load(self):
        n_stages = self.n_stages
        streams = [
            [phn.Stream(), phn.Stream()] # Vapor, Liquid
            for i in range(n_stages + 2)
        ]
        self.vle_stages = [
            VLEStage(
                ins=[streams[i+1][0], streams[i-1][1]],
                outs=streams[i]
            ) for i in range(1, n_stages + 1)
        ]
            
# class Split(Node):
#     n_ins = 1
#     n_outs = 2
    
#     def load(self):
#         inlet, = self.ins
#         outs = self.outs
#         for i in outs: i.variables = inlet.variables
    
#     def equations(self, fmt=None, context=None, inbound=None):
#         inlet, = self.inlet_variables()
#         top, bottom = self.outlet_variables()
#         split = index.split
#         vars = self.ins[0].variables
#         if index.Fc in vars:
#             equations = [
#                 EQ(inlet.Fc * split, top.Fc),
#                 EQ(inlet.Fc * (1 - split), bottom.Fc)
#             ]
#         elif index.Fcp in vars:
#             equations = [
#                 EQ(inlet.Fcp * split, top.Fcp),
#                 EQ(inlet.Fcp * (1 - split), bottom.Fcp)
#             ]
#         if index.H in vars:
#             equations = [
#                 EQ(inlet.H * split, top.H),
#                 EQ(inlet.H * (1 - split), bottom.H)
#             ]
#         elif index.T in vars:
#             equations = [
#                 EQ(inlet.T, top.T, bottom.T)
#             ]
#         if index.P in vars:
#             equations = [
#                 EQ(inlet.P, top.P, bottom.P)
#             ]
#         return equations


# class LLEStage(Node, tag='z'):
#     n_ins = 2
#     n_outs = 2
    
#     def prepare(self, ins, outs, T=None, P=None, Q=None):
#         self.init_ins(ins)
#         self.init_outs(outs)
#         self.T = T
#         self.P = P
#         self.Q = Q
    
#     def load(self):
#         specs = []
#         filtered = []
#         if self.Q:
#             self.ins.append(
#                 phn.Edge(variables=Variables(index.Q))
#             )
#         self.mixer = Mixer(self.ins)
#         if self.T:
#             specs.append(index.T)
#             filtered.append(index.H)
#         if self.P:
#             specs.append(index.P)
#             filtered.append(index.P)
#         if self.T and self.Q: 
#             raise ValueError('cannot specify both temperature and duty')
#         elif not (self.T or self.Q):
#             raise ValueError('must either temperature or duty')
#         self.filter = Pylon.filter(self.mixer.outs[0], filtered)
#         self.distribute = Pylon.distribute(self.filter.outs[0], [index.Fc], 2)
#         specs = Variables(*specs)
#         if specs:
#             self.ins.append(
#                 phn.Edge(variables=specs)
#             )
#             self.outlet_specs = Pylon.repeat(self.ins[-1], 3)
#             self.merge_specs = Pylon.merge([self.distribute.outs[0], self.outlet_specs.outs[0]])
#             lle_inlet = self.merge_specs.outs[0]
#         else:
#             self.outlet_specs = Pylon.distribute(self.distribute.outs[0], [index.P], 3)
#             lle_inlet = self.distribute.outs[0]
#         self.lle = LLE(lle_inlet)
#         lle_outlet = self.lle.outs[0]
#         merge_T = index.T in lle_outlet.variables
#         if merge_T:
#             self.pop = Pylon.pop(lle_outlet, [index.T], 3)
#             lle_outlet = self.pop.outs[0]
#         self.partition_merge = Pylon.merge([lle_outlet, self.distribute.outs[1]])
#         self.partition = Partition(self.partition_merge.outs[0])
#         if merge_T:
#             self.exit_merges = [Pylon.merge([i, j, k]) for i, j, k 
#                                 in zip(self.partition.outs, self.outlet_specs.outs[1:], self.pop.outs[1:])]
#         else:
#             self.exit_merges = [Pylon.merge([i, j]) for i, j in zip(self.partition.outs, self.outlet_specs.outs[1:])]


# class LLE(Node, tag='l'):
#     n_ins = 1
#     n_outs = 1
    
#     def load(self):
#         inlet, = self.ins
#         outlet, = self.outs
#         if index.H in inlet.variables:
#             outlet.variables = Variables(index.KLc, index.L, index.T)
#         else:
#             outlet.variables = Variables(index.KLc, index.L)
    
#     def equations(self):
#         inlet, = self.inlet_variables()
#         outlet,  = self.outlet_variables()
#         if hasattr(inlet, 'H'):
#             lle = EQ(f.lle(*inlet), outlet.KLc & outlet.L & outlet.T)
#         else:
#             lle = EQ(f.lle(*inlet), outlet.KLc & outlet.L)
#         return [lle]


# class Partition(Node, tag='ϕ'):
#     n_ins = 1
#     n_outs = 2
    
#     def load(self):
#         inlet, = self.ins
#         top, bottom = self.outs
#         if not inlet.variables.difference([index.KVc, index.V, index.T, index.Fc]):
#             self.vle = True
#             self.lle = False
#         elif not inlet.variables.difference([index.KLc, index.L, index.T, index.Fc]):
#             self.vle = False
#             self.lle = True
#         else:
#             raise ValueError('inlet variables must be partition coefficients and a phase fraction')
#         top.variables = bottom.variables = Variables(index.Fcp)
    
#     def equations(self):
#         inlet, = self.inlet_variables()
#         top, bottom = self.outlet_variables()
#         if self.vle:
#             return [
#                 EQ(top.Fcp[index.liquid], inlet.Fc * (1 - inlet.V) / (inlet.V * (inlet.KVc - 1) + 1)),
#                 EQ(bottom.Fcp[index.liquid], inlet.Fc * inlet.V / (inlet.V * (inlet.KVc - 1) + 1))
#             ]
#         elif self.lle:
#             return [
#                 EQ(top.Fcp[index.liquid], inlet.Fc * (1 - inlet.L) / (inlet.L * (inlet.KLc - 1) + 1)),
#                 EQ(bottom.Fcp[index.liquid], inlet.Fc * inlet.L / (inlet.L * (inlet.KLc - 1) + 1))
#             ]
#         else:
#             raise RuntimeError('unknown error')
            
    