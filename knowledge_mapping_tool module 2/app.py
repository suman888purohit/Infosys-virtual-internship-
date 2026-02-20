from nlp.nlp_pipeline import run_nlp_pipeline
import networkx as nx
import matplotlib.pyplot as plt

def generate_knowledge_graph(relations):
    G = nx.DiGraph()

    for rel in relations:
        subject = rel["subject"]
        relation = rel["relation"]
        obj = rel["object"]

        # Add nodes and edge
        G.add_node(subject)
        G.add_node(obj)
        G.add_edge(subject, obj, label=relation)

    # Draw graph
    pos = nx.spring_layout(G)
    edge_labels = nx.get_edge_attributes(G, 'label')

    plt.figure(figsize=(8, 5))
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Knowledge Graph from NLP Pipeline")
    plt.show()


if __name__ == "__main__":
    print("=== NLP Pipeline for Cross-Domain Knowledge Mapping ===")
    
    text = input("Enter your text: ")

    result = run_nlp_pipeline(text)

    print("\n--- Cleaned Sentences (Preprocessing) ---")
    print(result["cleaned_sentences"])

    print("\n--- Named Entities (NER) ---")
    for entity in result["entities"]:
        print(entity)

    print("\n--- Extracted Relations (Triples) ---")
    for relation in result["relations"]:
        print(relation)

    # Generate Graph Visualization
    if result["relations"]:
        generate_knowledge_graph(result["relations"])
    else:
        print("\nNo relations found to generate graph.")
