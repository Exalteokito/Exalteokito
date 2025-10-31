import json
from haystack import Document

# Load processed articles
with open("processed_articles.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

# Convert to Haystack Documents
documents = []
for article in articles:
    doc = Document(
        content=article["content"],
        meta=article["meta"]
    )
    documents.append(doc)

# Ensure models directory exists
import os
os.makedirs("models", exist_ok=True)

# Save as documents.json
doc_dicts = [doc.to_dict() for doc in documents]
with open("models/documents.json", "w", encoding="utf-8") as f:
    json.dump(doc_dicts, f, ensure_ascii=False, indent=2)

print("Documents prepared and saved to models/documents.json")