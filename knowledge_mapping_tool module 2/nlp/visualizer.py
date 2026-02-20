import networkx as nx
import matplotlib.pyplot as plt

def visualize_knowledge_graph(triples):
    G = nx.DiGraph()
    
    # Add nodes and edges from triples
    for subj, rel, obj in triples:
        G.add_edge(subj, obj, relation=rel)
    
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G, k=0.5) # k controls distance between nodes
    
    # Draw nodes and labels
    nx.draw(G, pos, with_labels=True, node_color='skyblue', 
            node_size=3000, edge_color='gray', linewidths=2, font_size=12, font_weight='bold')
    
    # Draw edge labels (the relations)
    edge_labels = nx.get_edge_attributes(G, 'relation')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title("Cross-Domain Knowledge Map", fontsize=15)
    plt.show() # Yeh presentation ke beech mein pop-up window kholegas