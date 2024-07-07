# -*- coding: utf-8 -*-
"""
"""
__all__ = ('PhenomeNodeGraphics',)

class PhenomeNodeGraphics:
    """Create a PhenomeNodeGraphics object that contains specifications for 
    Graphviz node and edge styles."""
    __slots__ = ('category', 'directed', 'linear', 'options', 'color')
    
    #: [dict] Default node settings
    default_options = {
        'shape': 'point',
        'style': 'filled',
        'gradientangle': '0',
        'width': '0.2',
        'height': '0.2',
        'orientation': '0.0',
        'peripheries': '0',
        'margin': '0',
        'fontname': 'Arial'
    }
    
    #: [dict] Default colors by category
    default_colors = {
        'material': '#a180b8',
        'hidden': '#bdc2bf',
        'material-parameter': '#5fc1cf',
        'energy-parameter': '#f1777f',
        'energy': '#403a48',
        'pressure': '#8ead3e',
        
    }
    
    def __init__(self, category, directed, linear):
        #: [str] Phenomena category(e.g., material, energy, separation, generation, pressure).
        self.category = category
        
        #: [bool] Whether equation should explicitly solve for a variable.
        self.directed = directed
        
        #: [bool] Whether equation is linear.
        self.linear = linear
        
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
        return f'{type(self).__name__}(category={self.category}, directed={self.directed}, linear={self.linear})'

