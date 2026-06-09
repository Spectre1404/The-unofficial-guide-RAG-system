import os
import json
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_DIR = os.path.join(BASE_DIR, "data", "chunks")

sys.path.insert(0, os.path.join(BASE_DIR, "src"))
from ingest import load_and_clean_all


def split_into_paragraphs(text: str) -> list:
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if len(p.strip()) > 30]


def count_words(text: str) -> int:
    return len(text.split())


def chunk_document(text, source, target_words=200, overlap_words=50):
    paragraphs = split_into_paragraphs(text)
    chunks = []
    current_paragraphs = []
    current_word_count = 0
    overlap_text = ""

    for para in paragraphs:
        para_words = count_words(para)

        if para_words >= target_words:
            if current_paragraphs:
                chunk_text = (overlap_text + " " + " ".join(current_paragraphs)).strip()
                if len(chunk_text) > 30:
                    chunks.append({
                        "source": source,
                        "chunk_index": len(chunks),
                        "text": chunk_text,
                        "word_count": count_words(chunk_text)
                    })
                words = chunk_text.split()
                overlap_text = " ".join(words[-overlap_words:]) if len(words) > overlap_words else chunk_text
                current_paragraphs = []
                current_word_count = 0

            chunk_text = (overlap_text + " " + para).strip()
            chunks.append({
                "source": source,
                "chunk_index": len(chunks),
                "text": chunk_text,
                "word_count": count_words(chunk_text)
            })
            words = chunk_text.split()
            overlap_text = " ".join(words[-overlap_words:]) if len(words) > overlap_words else chunk_text
            continue

        current_paragraphs.append(para)
        current_word_count += para_words

        if current_word_count >= target_words:
            chunk_text = (overlap_text + " " + " ".join(current_paragraphs)).strip()
            if len(chunk_text) > 30:
                chunks.append({
                    "source": source,
                    "chunk_index": len(chunks),
                    "text": chunk_text,
                    "word_count": count_words(chunk_text)
                })
            words = chunk_text.split()
            overlap_text = " ".join(words[-overlap_words:]) if len(words) > overlap_words else chunk_text
            current_paragraphs = []
            current_word_count = 0

    if current_paragraphs:
        chunk_text = (overlap_text + " " + " ".join(current_paragraphs)).strip()
        if len(chunk_text) > 30:
            chunks.append({
                "source": source,
                "chunk_index": len(chunks),
                "text": chunk_text,
                "word_count": count_words(chunk_text)
            })

    return chunks


def chunk_all_documents():
    os.makedirs(CHUNKS_DIR, exist_ok=True)
    documents = load_and_clean_all()
    all_chunks = []

    for doc in documents:
        doc_chunks = chunk_document(
            text=doc["text"],
            source=doc["source"],
            target_words=200,
            overlap_words=50
        )
        all_chunks.extend(doc_chunks)
        print(f"  {doc['source']}: {len(doc_chunks)} chunks")

    output_path = os.path.join(CHUNKS_DIR, "all_chunks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    return all_chunks


if __name__ == "__main__":
    print("=== CHUNKING DOCUMENTS ===\n")
    chunks = chunk_all_documents()

    print(f"\n✓ Total chunks produced: {len(chunks)}")
    print(f"  Target range: 50–500 chunks")

    if len(chunks) < 50:
        print("  ⚠️  WARNING: Fewer than 50 chunks — consider smaller chunk size")
    elif len(chunks) > 500:
        print("  ⚠️  WARNING: More than 500 chunks — consider larger chunk size")
    else:
        print("  ✓ Chunk count looks healthy")

    import random
    print("\n=== 5 SAMPLE CHUNKS FOR INSPECTION ===")
    sample = random.sample(chunks, min(5, len(chunks)))
    for i, chunk in enumerate(sample, 1):
        print(f"\n--- Chunk {i} | Source: {chunk['source']} | Words: {chunk['word_count']} ---")
        print(chunk["text"])
        print()