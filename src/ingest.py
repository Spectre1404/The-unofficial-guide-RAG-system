import os
import re

RAW_DIR = "data/raw"
CLEAN_DIR = "data/clean"

def clean_text(text: str) -> str:
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode common HTML entities
    text = text.replace('&amp;', '&').replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Remove markdown-style links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove repeated nav/boilerplate phrases
    boilerplate = [
        "read more", "share", "reply", "upvote", "downvote",
        "save", "hide", "report", "permalink", "embed",
        "cookies", "privacy policy", "terms of service",
        "cookie banner", "accept all cookies",
        "subscribe", "sign in", "log in", "sign up",
        "advertisement", "sponsored"
    ]
    for phrase in boilerplate:
        text = re.sub(rf'\b{re.escape(phrase)}\b', '', text, flags=re.IGNORECASE)
    # Collapse excess whitespace and blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    return text

def load_and_clean_all():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    documents = []

    for filename in sorted(os.listdir(RAW_DIR)):
        if not filename.endswith(".txt"):
            continue
        raw_path = os.path.join(RAW_DIR, filename)
        clean_path = os.path.join(CLEAN_DIR, filename)

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        cleaned = clean_text(raw_text)

        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(cleaned)

        documents.append({
            "source": filename,
            "text": cleaned
        })
        print(f"✓ Cleaned: {filename} ({len(cleaned)} chars)")

    return documents

if __name__ == "__main__":
    docs = load_and_clean_all()
    print(f"\nTotal documents loaded: {len(docs)}")
    # Print one document to inspect
    print("\n--- SAMPLE CLEANED DOCUMENT (first one) ---")
    print(docs[0]["text"][:1000])