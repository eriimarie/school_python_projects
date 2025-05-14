#!/usr/bin/env python
# coding: utf-8

# In[4]:


import numpy as np
import plotly.graph_objects as go
import networkx as nx # New dependency


def obj_data_to_mesh3d(odata):
    # odata is the string read from an obj file
    vertices = []
    faces = []
    lines = odata.splitlines()   
   
    for line in lines:
        slist = line.split()
        if slist:
            if slist[0] == 'v':
                vertex = np.array(slist[1:], dtype=float)
                vertices.append(vertex)
            elif slist[0] == 'f':
                face = []
                for k in range(1, len(slist)):
                    face.append([int(s) for s in slist[k].replace('//','/').split('/')])
                if len(face) > 3: # triangulate the n-polyonal face, n>3
                    faces.extend([[face[0][0]-1, face[k][0]-1, face[k+1][0]-1] for k in range(1, len(face)-1)])
                else:    
                    faces.append([face[j][0]-1 for j in range(len(face))])
            else: pass
    
    
    return np.array(vertices), np.array(faces)


with open("lh.pial.obj", "r") as f:
    obj_data = f.read()
[vertices, faces] = obj_data_to_mesh3d(obj_data)

vert_x, vert_y, vert_z = vertices[:,:3].T
face_i, face_j, face_k = faces.T

cmat = np.loadtxt('icbm_fiber_mat.txt')
nodes = np.loadtxt('fs_region_centers_68_sort.txt')

labels=[]
with open("freesurfer_regions_68_sort_full.txt", "r") as f:
    for line in f:
        labels.append(line.strip('\n'))

# Instantiate Graph and add nodes (with their coordinates)
G = nx.Graph()

for idx, node in enumerate(nodes):
    G.add_node(idx, coord=node)

# Add made-up colors for the nodes as node attribute
colors_data = {node: ('gray' if node > 10 else 'red') for node in G.nodes}
nx.set_node_attributes(G, colors_data, name="color")

# Add edges
[source, target] = np.nonzero(np.triu(cmat)>0.01)
edges = list(zip(source, target))

G.add_edges_from(edges)

# Get node coordinates from node attribute
nodes_x = [data['coord'][0] for node, data in G.nodes(data=True)]
nodes_y = [data['coord'][1] for node, data in G.nodes(data=True)]
nodes_z = [data['coord'][2] for node, data in G.nodes(data=True)]

edge_x = []
edge_y = []
edge_z = []
for s, t in edges:
    edge_x += [nodes_x[s], nodes_x[t]]
    edge_y += [nodes_y[s], nodes_y[t]]
    edge_z += [nodes_z[s], nodes_z[t]]

# Get node colors from node attribute
node_colors = [data['color'] for node, data in G.nodes(data=True)]

fig = go.Figure()

# Changed color and opacity kwargs
fig.add_trace(go.Mesh3d(x=vert_x, y=vert_y, z=vert_z, i=face_i, j=face_j, k=face_k,
                        color='gray', opacity=0.1, name='', showscale=False, hoverinfo='none'))

fig.add_trace(go.Scatter3d(x=nodes_x, y=nodes_y, z=nodes_z, text=labels,
                           mode='markers', hoverinfo='text', name='Nodes',
                           marker=dict(
                                       size=5, # Changed node size...
                                       color=node_colors # ...and color
                                      )
                           ))
fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z,
                           mode='lines', hoverinfo='none', name='Edges',
                           opacity=0.3, # Added opacity kwarg
                           line=dict(color='pink') # Added line color
                           ))

fig.update_layout(
    scene=dict(
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=False, visible=False),
        zaxis=dict(showticklabels=False, visible=False),
    ),
    width=800, height=600
)

fig.show()

