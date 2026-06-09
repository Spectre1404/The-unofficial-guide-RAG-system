import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from query import ask

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "What platforms do students recommend for finding off-campus housing near UIC?",
        "expected": "Students recommend Domu, Apartments.com, Zillow, University Rentals, and the UIC off-campus housing site. Facebook is mentioned but warned about as scam-prone."
    },
    {
        "id": 2,
        "question": "What rent range do students mention for sharing an apartment in Little Italy near UIC?",
        "expected": "Students mention aiming for about $800–$1,000 per person in Little Italy with one or two roommates."
    },
    {
        "id": 3,
        "question": "What warnings do students give about using Facebook for housing searches?",
        "expected": "Students warn that Facebook housing listings can contain fraudulent or scam listings and recommend using more reputable sites instead."
    },
    {
        "id": 4,
        "question": "What is the official purpose of the UIC off-campus housing website?",
        "expected": "The UIC off-campus housing site is an official listing service for rental units intended for UIC students, faculty, and staff."
    },
    {
        "id": 5,
        "question": "What kinds of off-campus issues does UIC CSRC help students with?",
        "expected": "The CSRC offers resources for apartment searching and for navigating issues with landlords or roommates."
    }
]

def run_evaluation():
    print("=== EVALUATION REPORT ===\n")
    for item in EVAL_QUESTIONS:
        print(f"{'='*65}")
        print(f"Q{item['id']}: {item['question']}")
        print(f"\nEXPECTED: {item['expected']}")
        result = ask(item["question"])
        print(f"\nSYSTEM RESPONSE: {result['answer']}")
        print(f"\nSOURCES RETRIEVED:")
        for s in result["sources"]:
            print(f"  • {s}")
        print(f"\nCHUNKS (top 4 distances):")
        for c in result["chunks"]:
            print(f"  [{c['distance']}] {c['source']} — {c['text'][:80]}...")
        print()

if __name__ == "__main__":
    run_evaluation()