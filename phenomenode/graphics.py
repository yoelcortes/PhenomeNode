# -*- coding: utf-8 -*-
"""
"""
__all__ = ('PhenomeNodeGraphics',)

class PhenomeNodeGraphics:
    """Create a PhenomeNodeGraphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('category', 'options', 'color')
    
    #: [dict] Default node settings
    default_options = {
        'shape': 'point',
        'style': 'filled',
        'gradientangle': '0',
        'width': '0.1',
        'height': '0.1',
        'orientation': '0.0',
        'peripheries': '1',
        'margin': 'default',
        'fontname': 'Arial'
    }
    
    #: [dict] Default colors by category
    default_colors = {
        'material': '#403a48',
        'transport': '#33cc33',
        'reaction': '#5fc1cf',
        'equilibrium': '#a180b8',
        'energy': '#f1777f',
        'pressure': '#8ead3e',
    }
    
    def __init__(self, category):
        #: [str] Phenomena category(e.g., material, energy, equilibrium, reaction, transport)
        self.category = category
        
        #: [dict] Node settings
        self.options = self.default_options.copy()
        
        # [str] Node and edge color
        self.color = self.default_colors[self.category]
    
    def update(self, **options):
        self.options.update(options)
    
    def get_options(self, node): # pragma: no coverage
        """Return node tailored to node specifications"""
        options = self.options.copy()
        options['name'] = str(hash(node))
        options['label'] = ''
        options['fillcolor'] = options['fontcolor'] = options['color'] = self.color
        return options
        
    def __repr__(self): # pragma: no coverage
        return f'{type(self).__name__}(category={self.category})'

