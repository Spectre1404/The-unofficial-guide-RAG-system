import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_PATH = os.path.join(BASE_DIR, "data", "chunks", "all_chunks.json")
CHROMA_DIR  = os.path.join(BASE_DIR, "data", "chroma_db")

def load_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_index():
    print("Loading chunks...")
    chunks = load_chunks()
    print(f"  {len(chunks)} chunks loaded")

    print("\nLoading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("\nEmbedding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    print(f"  Embeddings shape: {embeddings.shape}")

    print("\nSetting up ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("uic_housing")
        print("  Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name="uic_housing",
        metadata={"hnsw:space": "cosine"}
    )

    print("\nInserting chunks into ChromaDB...")
    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[
            {
                "source": c["source"],
                "chunk_index": c["chunk_index"],
                "word_count": c["word_count"]
            }
            for c in chunks
        ]
    )

    print(f"\n✓ Index built: {collection.count()} chunks stored in ChromaDB")
    return collection

if __name__ == "__main__":
    build_index()