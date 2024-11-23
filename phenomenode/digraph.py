# -*- coding: utf-8 -*-
"""
"""
import phenomenode as phn
from .connection import Connection
from warnings import warn
from graphviz import Digraph
from IPython import display

__all__ = ('digraph_from_phenomenode',
           'blank_digraph',
           'finalize_digraph',
           'display_digraph',
           'save_digraph')

preferences = phn.preferences

def blank_digraph(format='svg', maxiter='10000', 
                  Damping='0.2', K='0.2', **graph_attrs):
    # Create a digraph and set direction left to right
    f = Digraph(format=format)
    f.attr(rankdir='LR', 
           maxiter=maxiter, 
           Damping=Damping, 
           K=K,
           penwidth='0', 
           color='none', 
           bgcolor=preferences.background_color,
           # fontcolor=preferences.label_color, 
           # fontname="Arial",
           # labeljust='l', 
           # labelloc='t', 
           # fontsize='8', 
           # constraint='false',
           nodesep='0.01', 
           ranksep='0.01', 
           layout='fdp', 
           **graph_attrs)
    return f

def stream_varnodes(phenomenode, varnodes=None):
    if varnodes is None: varnodes = []
    for i in phenomenode.ins + phenomenode.outs:
        if hasattr(i, 'varnodes'): varnodes.extend(i.varnodes)
    for i in phenomenode.phenomena:
        stream_varnodes(i, varnodes)
    return varnodes

def digraph_from_phenomenode(phenomenode, filterkey, **graph_attrs):
    f = blank_digraph(**graph_attrs)
    bridge_nodes = set(stream_varnodes(phenomenode))
    nodes = get_all_nodes(phenomenode)
    update_digraph_from_phenomena(
        f, nodes, filterkey, bridge_nodes
    )
    return f

def get_all_nodes(phenomenode, nodes=None):
    if nodes is None: nodes = []
    if phenomenode.phenomena:
        for i in phenomenode.phenomena:
            get_all_nodes(i, nodes)
    else:
        nodes.append(phenomenode)
    return nodes

def update_digraph_from_phenomena(f, nodes, filterkey, bridge_nodes):
    all_connections = set()
    for i in nodes:
        if not (filterkey and filterkey(i)): 
            varnodes = i.outlet_varnodes if preferences.outputs_only else i.varnodes
            for varnode in varnodes:
                connection = Connection(i, varnode)
                all_connections.add(connection)
                for neighbor in varnode.neighbors:
                    if neighbor.phenomena: continue
                    if filterkey and filterkey(neighbor): continue
                    connection = Connection(neighbor, varnode)
                    all_connections.add(connection)
    varnodes = set([i.varnode for i in all_connections])
    nodes = set([i.phenomenode for i in all_connections])
    varnode_names = get_varnode_names(f, varnodes, bridge_nodes)
    phenomenode_names = get_phenomenode_names(f, nodes)
    add_connections(f, all_connections, phenomenode_names, varnode_names)
    

# def update_digraph_from_path(f, path, depth, node_names, all_connections,
#                              connected, filterkey, bridge_nodes, depths):
#     phenomena = set()
#     superphenomena = []
#     varnodes = set()
#     new_connections = []
#     other_connections = []
#     for i in path:
#         if i.phenomena:
#             superphenomena.append(i)
#             # proprietary_varnodes = [
#             #     i for i in i.proprietary_varnodes(filterkey)
#             #     if [j for j in (i.sinks + i.sources) if not j.phenomena]
#             # ]
#             # for varnode in proprietary_varnodes:
#             #     for neighbor in varnode.neighbors:
#             #         if neighbor.phenomena: continue
#             #         if filterkey and filterkey(neighbor): continue
#             #         connection = Connection(neighbor, varnode)
#             #         if connection in all_connections: continue
#             #         varnodes.add(varnode)
#             #         other_connections.append(connection)
#         elif not (filterkey and filterkey(i)): 
#             phenomena.add(i)
#             proprietary_varnodes = i.varnodes
#             varnodes.update(proprietary_varnodes)
#             for varnode in proprietary_varnodes:
#                 connection = Connection(i, varnode)
#                 if connection in all_connections: continue
#                 new_connections.append(connection)
#                 for neighbor in varnode.neighbors:
#                     if neighbor.phenomena: continue
#                     if filterkey and filterkey(neighbor): continue
#                     connection = Connection(neighbor, varnode)
#                     if connection in all_connections: continue
#                     other_connections.append(connection)
#     all_connections.update(new_connections + other_connections)
#     update_varnode_names(f, varnodes, node_names, bridge_nodes)
#     update_phenomenode_names(f, phenomena, node_names)
#     add_connections(f, new_connections, node_names)
#     connected.update(new_connections)
#     if preferences.cluster and depth:
#         N_colors = len(preferences.depth_colors)
#         color = preferences.depth_colors[(depth) % N_colors]
#         if preferences.fill_cluster:
#             if depth == 1:
#                 kwargs = dict(bgcolor=color, penwidth='0')
#             else:
#                 kwargs = dict(bgcolor=color, penwidth='0.2', color=preferences.edge_color)
#         else:
#             kwargs = dict(color=color, bgcolor='none', penwidth='0.75', style='solid')
#         for i in superphenomena:
#             if depths is None or i.depth in depths: 
#                 if preferences.tooltip: kwargs['tooltip'] = i.get_tooltip_string()
#                 with f.subgraph(name='cluster_' + str(hash(i))) as c:
#                     c.attr(label=str(i), fontname="Arial", fontsize='8',
#                            labeljust='l', fontcolor=preferences.label_color,
#                            style='rounded',
#                            clusterrank='local', 
#                            **kwargs)
#                     update_digraph_from_path(c, i.phenomena, depth, node_names,
#                                              all_connections, connected, filterkey,
#                                              bridge_nodes, depths)
#             else:
#                 update_digraph_from_path(f, i.phenomena, depth, node_names, 
#                                          all_connections, connected, filterkey,
#                                          bridge_nodes, depths)
#     else:
#         for i in superphenomena:
#             update_digraph_from_path(f, i.phenomena, depth, node_names, 
#                                      all_connections, connected, filterkey,
#                                      bridge_nodes, depths)


def get_phenomenode_names(f: Digraph, path):
    node_names = {}
    for n in path:
        kwargs = n.vizoptions()
        node_names[n] = kwargs['name']
        f.node(**kwargs)
    return node_names

def get_varnode_names(f: Digraph, varnodes, bridge_nodes):
    node_names = {}
    for n in varnodes:
        kwargs = n.vizoptions()
        node_names[n] = kwargs['name']
        # if n in bridge_nodes and n.variable.highlight and n.sources and preferences.highlight: kwargs['color'] = '#f3c354'
        f.node(**kwargs)
    return node_names

def add_connection(f: Digraph, connection, phenomenode_names, varnode_names, **edge_options):
    phenomenode = connection.phenomenode
    varnode = connection.varnode
    f.attr('edge', label='', taillabel='', headlabel='', labeldistance='1',
           **edge_options)
    options = {}
    if preferences.tooltip:
        options['labeltooltip'] = options['edgetooltip'] = phenomenode.get_tooltip_string()
    graphics = phenomenode.graphics
    color = (graphics.subcolor or graphics.color) if preferences.subcategory else graphics.color
    penwidth = '3'
    directed = (preferences.directed and graphics.directed and varnode in phenomenode.outs)
    f.edge(phenomenode_names[phenomenode], varnode_names[varnode], label='', 
           arrowtail='none', 
           arrowhead='normal' if directed else 'none', headport='c', 
           tailport='c', 
           color=color,
           len='0.5',
           dir='forward' if directed else 'none',
           penwidth=penwidth,
           style='dashed' if graphics.category == 'hidden' else 'solid',
           **options)

def add_connections(f: Digraph, connections, phenomenode_names, varnode_names, **edge_options):
    # Set attributes for graph and edges
    f.attr('graph', 
           splines='curved', 
           outputorder='edgesfirst', 
           nodesep='0.2', 
           ranksep='0.2',
           maxiter='100000',
           overlap=preferences.overlap, 
           dir='none')
    f.attr('edge', 
           concentrate='true',
           dir='none')
    for connection in connections:
        add_connection(f, connection, phenomenode_names, varnode_names,
                       **edge_options)

def display_digraph(digraph, format): # pragma: no coverage
    if format is None: format = preferences.graphviz_format
    if format == 'svg':
        img = digraph.pipe(format=format)
        x = display.SVG(img)
        display.display(x)
    else:
        x = display.Image(digraph.pipe(format='png'))
        display.display(x)

def save_digraph(digraph, file, format): # pragma: no coverage
    if '.' not in file:
        if format is None: format = preferences.graphviz_format
        file += '.' + format
    elif format is None:
        format = file.split()[-1]
    else:
        raise ValueError(
            "cannot specify format extension; file already has format "
           f"extension '{file.split()[-1]}'"
        )
    if format == 'tex':
        import dot2tex
        texcode = dot2tex.dot2tex(digraph.source, math=True)
        f = open(file, 'w', encoding="utf-8")
        f.write(texcode)
        f.close()
    else:
        img = digraph.pipe(format=format)
        f = open(file, 'wb')
        f.write(img)
        f.close()
    
def finalize_digraph(digraph, file, format): # pragma: no coverage
    if preferences.raise_exception: 
        if file: save_digraph(digraph, file, format)
        if format in ('png', 'svg'): display_digraph(digraph, format)
    else:
        try:
            if file: save_digraph(digraph, file, format)
            display_digraph(digraph, format)
        except (OSError, TypeError) as exp:
            raise exp from None
        except Exception as exp: 
            warn(
                f"a '{type(exp).__name__}' was raised when generating "
                "graphviz diagram, possibly due to graphviz installation issues, "
                "make sure Graphviz executables are on your systems' PATH",
                RuntimeWarning
            )
