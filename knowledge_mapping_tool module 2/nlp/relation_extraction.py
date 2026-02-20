import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Improved relation extraction (more flexible for demo)
def extract_relations(text):
    doc = nlp(text)
    relations = []

    for sent in doc.sents:
        subject = None
        relation = None
        obj = None

        for token in sent:
            # Find subject
            if token.dep_ in ("nsubj", "nsubjpass"):
                subject = token.text

            # Find main verb (relation)
            if token.pos_ == "VERB":
                relation = token.text

            # Find object
            if token.dep_ in ("dobj", "pobj", "attr", "dative", "oprd"):
                obj = token.text

        if subject and relation and obj:
            relations.append({
                "subject": subject,
                "relation": relation,
                "object": obj
            })

    return relations
