# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences

class PhenomeNodeGraphics:
    """Create a PhenomeNodeGraphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('node', 'edge_in', 'edge_out')
    
    def __init__(self, node, edge_in=None, edge_out=None):
        #: [dict] Node settings
        self.node = node
        
        # [dict] Input stream edge settings
        self.edge_in = edge_in or {}
        
        # [dict] Output stream edge settings
        self.edge_out = edge_out or {}
    
    def get_inlet_options(self, sink, sink_index):
        edge_in = self.edge_in
        if sink_index in edge_in:
            options = edge_in[sink_index]
        else:
            options = {'headport': 'c'}
        return options
    
    def get_outlet_options(self, source, source_index):
        edge_out = self.edge_out
        if source_index in edge_out:
            options = edge_out[source_index]
        else:
            options = {'tailport': 'c'}
        return options
    
    def get_options(self, node): # pragma: no coverage
        """Return node tailored to node specifications"""
        options = self.node.copy()
        options['name'] = str(hash(node))
        if 'label' not in options:
            options['label'] = str(node)
        if 'fillcolor' not in options:
            options['fillcolor'] = preferences.node_color
        if 'fontcolor' not in options:
            options['fontcolor'] = preferences.node_label_color
        if 'color' not in options:
            options['color'] = preferences.node_periphery_color
        return options
        
    def __repr__(self): # pragma: no coverage
        return f'{type(self).__name__}(node={self.node}, edge_in={self.edge_in}, edge_out={self.edge_out})'


# %% Graphics components

box_node = {
    'shape': 'box',
    'style': 'filled',
    'gradientangle': '0',
    'width': '0.6',
    'height': '0.6',
    'orientation': '0.0',
    'peripheries': '1',
    'margin': 'default',
    'fontname': 'Arial'
}

box_graphics = PhenomeNodeGraphics(box_node)

class TerminalGraphics(PhenomeNodeGraphics):

    def get_options(self, node): 
        options = super().get_options(node)
        options['fillcolor'] = preferences.edge_color
        return options

terminal_node = box_node.copy()
terminal_node['label'] = ''
terminal_node['color'] = 'none'
terminal_node['shape'] = 'point'
terminal_node['width'] = '0.1'
terminal_graphics = TerminalGraphics(terminal_node)
