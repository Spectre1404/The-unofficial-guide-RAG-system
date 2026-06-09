import os
import sys
from dotenv import load_dotenv
from groq import Groq

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from retrieve import retrieve

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an assistant that helps UIC students find reliable \
information about off-campus housing near the University of Illinois Chicago.

STRICT RULES — follow these exactly:
1. Answer ONLY using information explicitly stated in the provided documents.
2. Do NOT use your general training knowledge under any circumstances.
3. If the question is NOT about off-campus housing, renting, leases, \
neighborhoods, roommates, or UIC housing resources, respond with exactly:
   "I don't have enough information in my documents to answer that question."
4. If the documents mention a topic only incidentally (e.g., a gym listed \
as an apartment amenity), do NOT treat that as an answer to a question \
about that topic directly.
5. Do not speculate, extrapolate, or fill in gaps from general knowledge.
6. Keep your answer concise and practical — 3 to 6 sentences maximum.
7. When you use a fact, mention the source document inline \
(e.g., "According to [source name]...").
"""

def format_context(chunks: list) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    sections = []
    for i, chunk in enumerate(chunks, 1):
        sections.append(
            f"[Document {i} — Source: {chunk['source']}]\n{chunk['text']}"
        )
    return "\n\n---\n\n".join(sections)

def ask(question: str, top_k: int = 4) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve top_k relevant chunks
    2. Build grounded prompt
    3. Generate answer with Groq LLM
    4. Return answer + sources (programmatically guaranteed)
    """
    # Step 1: Retrieve
    chunks = retrieve(question, top_k=top_k)

    # Step 2: Build context
    context = format_context(chunks)

    # Step 3: Build user message
    user_message = f"""Here are the relevant documents:

{context}

---

Question: {question}

Remember: answer ONLY from the documents above. If the documents don't \
cover this question, say you don't have enough information."""

    # Step 4: Call LLM
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message}
        ],
        temperature=0.2,   # low temp = more faithful, less creative
        max_tokens=512
    )

    answer = response.choices[0].message.content.strip()

    # Step 5: Programmatically collect sources (not left to the LLM)
    seen = []
    for chunk in chunks:
        if chunk["source"] not in seen:
            seen.append(chunk["source"])

    return {
        "answer":   answer,
        "sources":  seen,
        "chunks":   chunks   # kept for debugging/evaluation
    }


if __name__ == "__main__":
    # Quick end-to-end test before launching the UI
    test_questions = [
        # In-scope: should give a grounded answer
        "What platforms do students recommend for finding off-campus housing near UIC?",
        # In-scope: scam warning
        "What warnings do students give about using Facebook for housing?",
        # Out-of-scope: system should refuse
        "What is the best gym near UIC campus?"
    ]

    for q in test_questions:
        print(f"\n{'='*65}")
        print(f"Q: {q}")
        print('='*65)
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"\nSources:")
        for s in result["sources"]:
            print(f"  • {s}")
        print()