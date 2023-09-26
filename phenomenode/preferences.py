# -*- coding: utf-8 -*-
"""
"""
import yaml
import os

__all__ = ('preferences', 'DisplayPreferences', 'TemporaryPreferences')

class DisplayPreferences:
    """
    All preferences for graph and equations display.

    Examples
    --------
    >>> from phenomenode import preferences
    >>> preferences.show()
    DisplayPreferences:
    autodisplay: True
    raise_exception: False
    background_color: 'transparent'
    edge_color: '#90918e'
    label_color: '#90918e'
    depth_colors: ['#f98f609f']
    variable_width: 'F_mass'
    label_edges: True
    node_color: '#555f69'
    node_label_color: 'white'
    node_periphery_color: '#90918e'
    fill_cluster: False
    graphviz_format: 'svg'
    tooltips_full_results: False
    graphviz_html_height: {'big-network': ('600px', '900px'), 'network': ('400px', '600px'), 'node': ('225px', '400px')}
    
    """
    __slots__ = (
        'autodisplay', 
        'raise_exception', 
        'background_color', 
        'edge_color',
        'label_color', 
        'depth_colors', 
        'variable_width',
        'label_edges',
        'node_color', 'node_label_color', 'node_periphery_color',
        'fill_cluster', 'graphviz_format', 'tooltips_full_results',
        'graphviz_html_height'
    )
    
    def __init__(self):
        #: Whether to label the edges with sources and sinks in process 
        #: flow diagrams.
        self.label_edges: bool = True
        
        #: Whether to automatically generate diagrams when displaying an object in the
        #: IPython console.
        self.autodisplay: bool = True
        
        #: Whether to raise exception regarding problems displaying diagrams.
        self.raise_exception: bool = False
        
        #: Background color.
        self.background_color: str = 'transparent'
        
        #: Color of edges.
        self.edge_color: str = '#90918e'
        
        #: Color of edge labels.
        self.label_color: str = '#90918e'
        
        #: Color of node clusters.
        self.depth_colors: list[str] = ['#f98f609f']
        
        #: Whether to scale edge widths by number of variables.
        self.variable_width: bool = 'F_mass'
        
        #: Node fill color.
        self.node_color: str = '#555f69'
        
        #: Node label color in BioSTEAM graphviz diagrams.
        self.node_label_color: str = 'white'
        
        #: Node periphery color in BioSTEAM graphviz diagrams.
        self.node_periphery_color: str = '#90918e'
        
        #: Whether to fill node boxes in 'cluster' diagrams.
        self.fill_cluster: bool = False
        
        #: Image format of BioSTEAM graphviz diagrams.
        self.graphviz_format: str = 'svg'
        
        #: Whether to add full results in tooltips by inserting java script into graphviz html outputs.
        self.tooltips_full_results: bool = False
        
        #: Displayed height of graphviz html diagrams without and with full results.
        self.graphviz_html_height: dict[str, tuple[str, str]] = {
            'big-network': ('600px', '900px'),
            'network': ('400px', '600px'),
            'node': ('225px', '400px'),
        }
        
    def temporary(self):
        """Return a TemporaryPreferences object that will revert back to original
        preferences after context management."""
        return TemporaryPreferences()
        
    def reset(self, save=False):
        """Reset to BioSTEAM defaults."""
        self.__init__()
        if save: self.save()
        
    def update(self, *, save=False, **kwargs):
        for i, j in kwargs.items(): setattr(self, i, j)
        if save: self.save()
        
    def _set_mode(self, stream, label, bg, cluster, node_color, 
                  node_label_color, node_periphery_color, fill_cluster, save):
        self.background_color = bg
        self.edge_color = stream
        self.label_color = label
        self.depth_colors = cluster
        self.node_color = node_color
        self.node_label_color = node_label_color
        self.node_periphery_color = node_periphery_color
        self.fill_cluster = fill_cluster
        if save: self.save()
    
    def classic_mode(self, 
                     stream='#90918e', 
                     label='#90918e', 
                     bg='transparent',
                     cluster=('#f98f609f',),
                     node_color='#555f69',
                     node_label_color='white',
                     node_periphery_color='none',
                     fill_cluster=False,
                     save=False):
        """Set diagram display colors to classic mode."""
        self._set_mode(stream, label, bg, cluster, node_color, 
                       node_label_color, node_periphery_color,
                       fill_cluster, save)
    
    def dark_mode(self, stream='#98a2ad', label='#e5e5e5', bg='transparent',
                  cluster=['#5172512f'], node_color='#555f69', 
                  node_label_color='white', node_periphery_color='none',
                  fill_cluster=True, save=False):
        """Set diagram display colors to dark mode."""
        self._set_mode(stream, label, bg, cluster, node_color, node_label_color,
                       node_periphery_color, fill_cluster, save)
    
    def light_mode(self, stream='#4e4e4e', label='#4e4e4e', bg='#ffffffff',
                   cluster=['#7ac0832f'], node_color='white:#CDCDCD', 
                   node_label_color='black', node_periphery_color='#4e4e4e',
                   fill_cluster=True, save=False):
        """Set diagram display colors to light mode."""
        self._set_mode(stream, label, bg, cluster, node_color, node_label_color, 
                       node_periphery_color, fill_cluster, save)
    
    night_mode = dark_mode
    day_mode = light_mode
    
    def autoload(self):
        folder = os.path.dirname(__file__)
        file = os.path.join(folder, 'preferences.yaml')
        with open(file, 'r') as stream: 
            data = yaml.full_load(stream)
            assert isinstance(data, dict), 'yaml file must return a dict' 
        self.update(**data)
        
    def to_dict(self):
        """Return dictionary of all preferences."""
        return {i: getattr(self, i) for i in preferences.__slots__}
        
    def save(self):
        """Save preferences."""
        folder = os.path.dirname(__file__)
        file = os.path.join(folder, 'preferences.yaml')
        with open(file, 'w') as file:
            dct = self.to_dict()
            yaml.dump(dct, file)

    def show(self):
        """Print all specifications."""
        dct = self.to_dict()
        print(f'{type(self).__name__}:\n' + '\n'.join([f"{i}: {repr(j)}" for i, j in dct.items()])) 
    _ipython_display_ = show


class TemporaryPreferences:
    
    def __enter__(self):
        dct = self.__dict__
        dct.update({i: getattr(preferences, i) for i in preferences.__slots__})
        return preferences
        
    def __exit__(self, type, exception, traceback):
        preferences.update(**self.__dict__)
        if exception: raise exception

#: 
preferences: DisplayPreferences = DisplayPreferences()

if os.environ.get("FILTER_WARNINGS"):
    from warnings import filterwarnings; filterwarnings('ignore')
if not os.environ.get("DISABLE_PREFERENCES") == "1":
    try: preferences.autoload()
    except: pass 
