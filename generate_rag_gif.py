import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx

fig, ax = plt.subplots(figsize=(6, 4))
fig.patch.set_facecolor('#0D1117')
ax.set_facecolor('#0D1117')
ax.axis('off')

# Create a graph
G = nx.barabasi_albert_graph(25, 2, seed=42)
pos = nx.spring_layout(G, seed=42, k=0.5) # k controls node spacing

def update(frame):
    ax.clear()
    ax.set_facecolor('#0D1117')
    ax.axis('off')
    
    # Base network drawing (faded)
    nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.2, edge_color='#8b949e')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#7c3aed', node_size=60, alpha=0.5)
    
    # Simulate a retrieval pulse traversing the graph
    phase = frame % 60
    
    # Select nodes to form a glowing pattern
    active_nodes = []
    central_node = 0
    
    if phase < 20:
        active_nodes = [central_node]
    elif phase < 40:
        active_nodes = [central_node] + list(G.neighbors(central_node))
    else:
        active_nodes = [central_node] + list(G.neighbors(central_node))
        for n in list(G.neighbors(central_node)):
            active_nodes.extend(list(G.neighbors(n)))
        active_nodes = list(set(active_nodes))
        
    # Animate node sizes based on frame for pulsation
    pulse = 1.0 + 0.3 * np.sin(frame * 0.2)
        
    nx.draw_networkx_nodes(G, pos, nodelist=active_nodes, ax=ax, node_color='#58A6FF', node_size=120 * pulse, alpha=0.9)
    
    # Highlight edges between active nodes
    subgraph = G.subgraph(active_nodes)
    nx.draw_networkx_edges(subgraph, pos, ax=ax, alpha=0.8, edge_color='#58A6FF', width=2 * pulse)
    
    # Keep axes fixed
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)

ani = animation.FuncAnimation(fig, update, frames=60, interval=50)
ani.save('assets/rag.gif', writer='pillow', fps=20)
plt.close(fig)
