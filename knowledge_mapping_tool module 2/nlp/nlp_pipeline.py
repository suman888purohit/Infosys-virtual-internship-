from nlp.preprocessing import preprocess_text
from nlp.ner_spacy import extract_entities
from nlp.relation_extraction import extract_relations

# Main pipeline function
def run_nlp_pipeline(text):
    # Step 1: Preprocessing
    cleaned_sentences = preprocess_text(text)

    # Step 2: Named Entity Recognition
    entities = extract_entities(text)

    # Step 3: Relation Extraction (Triples)
    relations = extract_relations(text)

    return {
        "cleaned_sentences": cleaned_sentences,
        "entities": entities,
        "relations": relations
    }
