# -*- coding: utf-8 -*-
"""
"""
from .preferences import preferences

class Graphics:
    """Create a Graphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('node', 'edge_in', 'edge_out')
    
    def __init__(self, edge_in, edge_out, node):
        # [dict] Input stream edge settings
        self.edge_in = edge_in
        
        # [dict] Output stream edge settings
        self.edge_out = edge_out
        
        #: [dict] Node settings
        self.node = node
    
    def get_inlet_options(self, sink, sink_index):
        edge_in = self.edge_in
        try:
            options = edge_in[sink_index]
        except IndexError:
            options = {'headport': 'c'}
        return options
    
    def get_outlet_options(self, source, source_index):
        edge_out = self.edge_out
        try:
            options = edge_out[source_index]
        except IndexError:
            options = {'tailport': 'c'}
        return options
    
    def get_options(self, node): # pragma: no coverage
        """Return node tailored to node specifications"""
        options = self.node.copy()
        options['label'] = str(node)
        options['name'] = str(hash(node))
        if 'fillcolor' not in node:
            options['fillcolor'] = preferences.node_color
        if 'fontcolor' not in node:
            options['fontcolor'] = preferences.node_label_color
        if 'color' not in node:
            options['color'] = preferences.node_periphery_color
        return options
        
    def __repr__(self): # pragma: no coverage
        return f'{type(self).__name__}(node={self.node}, edge_in={self.edge_in}, edge_out={self.edge_out})'


# %% Graphics components

single_edge_in = ({'headport': 'c'},)
single_edge_out = ({'tailport': 'c'},)

box_node = {'shape': 'box',
            'style': 'filled',
            'gradientangle': '0',
            'width': '0.6',
            'height': '0.6',
            'orientation': '0.0',
            'peripheries': '1',
            'margin': 'default',
            'fontname': 'Arial'}

box_graphics = Graphics(single_edge_in, single_edge_out, box_node)


