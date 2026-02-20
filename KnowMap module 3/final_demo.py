import networkx as nx
from  pyvis.network import Network
import json
from networkx.readwrite import json_graph

# ---------------------------
# STEP 1: NLP Output (Triples)
# ---------------------------
triples = [
    ("Artificial Intelligence", "improves", "Healthcare"),
    ("Machine Learning", "supports", "Medical Diagnosis"),
    ("Neural Networks", "used_in", "Cancer Detection"),
    ("Google", "invests_in", "Artificial Intelligence")
]

# ---------------------------
# STEP 2: Domain Mapping (Cross-Domain Feature)
# ---------------------------
domain_map = {
    "Artificial Intelligence": "Technology",
    "Machine Learning": "Technology",
    "Neural Networks": "Technology",
    "Healthcare": "Medical",
    "Medical Diagnosis": "Medical",
    "Cancer Detection": "Medical",
    "Google": "Organization"
}

# ---------------------------
# STEP 3: Build Knowledge Graph
# ---------------------------
def build_knowledge_graph(triples, domain_map):
    G = nx.DiGraph()
    for subj, rel, obj in triples:
        G.add_node(subj, domain=domain_map.get(subj, "Unknown"))
        G.add_node(obj, domain=domain_map.get(obj, "Unknown"))
        G.add_edge(subj, obj, relation=rel)
    return G

# ---------------------------
# STEP 4: Filter by Domain (Slide 14)
# ---------------------------
def filter_graph_by_domain(G, selected_domain):
    if selected_domain.lower() == "all":
        return G
    nodes_to_keep = [
        n for n, d in G.nodes(data=True)
        if d.get("domain", "").lower() == selected_domain.lower()
    ]
    return G.subgraph(nodes_to_keep).copy()

# ---------------------------
# STEP 5: Interactive Graph (Slide 13)
# ---------------------------
def create_interactive_graph(G):
    from pyvis.network import Network

    net = Network(height="600px", width="100%", directed=True)

    # Advanced interaction features (Slide 13)
    net.barnes_hut()
    net.set_options("""
    var options = {
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      },
      "physics": {
        "enabled": true
      }
    }
    """)

    # Add nodes with domain colors
    for node, data in G.nodes(data=True):
        domain = data.get("domain", "Unknown")

        if domain == "Technology":
            color = "blue"
        elif domain == "Medical":
            color = "red"
        elif domain == "Organization":
            color = "green"
        else:
            color = "gray"

        net.add_node(node, label=node, color=color, title=f"Domain: {domain}")

    # Add edges
    for source, target, data in G.edges(data=True):
        relation = data.get("relation", "")
        net.add_edge(source, target, label=relation)

    # 🔥 FIXED LINE (NO ERROR NOW)
    net.write_html("graph.html", open_browser=True)

    print("✅ Interactive graph opened successfully (graph.html)")


# ---------------------------
# STEP 6: Export JSON (Slide 15)
# ---------------------------
def export_graph_json(G):
    data = json_graph.node_link_data(G)
    with open("graph.json", "w") as f:
        json.dump(data, f, indent=4)
    print("✅ Graph exported as graph.json for D3.js visualization")

# ---------------------------
# MAIN EXECUTION (LIVE DEMO FLOW)
# ---------------------------
print("=== Cross-Domain Knowledge Graph Demo ===")

# Build graph
G = build_knowledge_graph(triples, domain_map)

# Show console output (important for demo)
print("\nNodes in Graph:")
print(G.nodes(data=True))

print("\nEdges in Graph:")
print(G.edges(data=True))

# Domain filter input (Slide 14)
print("\nAvailable Domains: Technology, Medical, Organization, All")
domain_choice = input("Enter domain to filter (type All for full graph): ")

G_filtered = filter_graph_by_domain(G, domain_choice)

# Create interactive graph
create_interactive_graph(G_filtered)

# Export JSON (Slide 15)
export_graph_json(G_filtered)