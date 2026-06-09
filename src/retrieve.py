import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from sentence_transformers import SentenceTransformer
import chromadb

CHROMA_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

# Load model and collection once at module level
_model      = None
_collection = None

def _load():
    global _model, _collection
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DIR)
        _collection = client.get_collection("uic_housing")

def retrieve(query: str, top_k: int = 4) -> list:
    _load()
    query_embedding = _model.encode([query]).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text":        results["documents"][0][i],
            "source":      results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance":    round(results["distances"][0][i], 4)
        })
    return retrieved

if __name__ == "__main__":
    # Test retrieval on 3 evaluation plan queries
    test_queries = [
        "What platforms do students recommend for finding off-campus housing near UIC?",
        "What warnings do students give about using Facebook for housing searches?",
        "What kinds of off-campus support does UIC CSRC provide to students?"
    ]

    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print('='*70)
        results = retrieve(query, top_k=4)
        for rank, r in enumerate(results, 1):
            print(f"\n  Rank {rank} | Source: {r['source']} | Distance: {r['distance']}")
            print(f"  {r['text'][:300]}...")
            print()
