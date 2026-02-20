import re
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to clean raw text
def clean_text(text):
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters (keep words & dots)
    text = re.sub(r'[^\w\s.]', '', text)
    return text.strip()

# Function for preprocessing
def preprocess_text(text):
    text = clean_text(text)
    doc = nlp(text)

    processed_sentences = []

    for sent in doc.sents:
        tokens = [
            token.lemma_.lower()
            for token in sent
            if not token.is_stop and not token.is_punct
        ]
        processed_sentences.append(" ".join(tokens))

    return processed_sentences
