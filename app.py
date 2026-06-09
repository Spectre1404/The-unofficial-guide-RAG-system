import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

import gradio as gr
from query import ask

def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


# ── UI ──────────────────────────────────────────────────────────────────────
with gr.Blocks(title="UIC Unofficial Housing Guide", theme=gr.themes.Soft()) as demo:

    gr.Markdown("""
    # 🏠 UIC Unofficial Housing Guide
    Ask anything about off-campus housing near UIC — rent, neighborhoods,
    platforms, lease tips, and more. Answers are grounded in real student
    posts and official UIC resources.
    """)

    with gr.Row():
        with gr.Column(scale=3):
            inp = gr.Textbox(
                label="Your question",
                placeholder='e.g. "What rent range is realistic in Little Italy with a roommate?"',
                lines=2
            )
        with gr.Column(scale=1):
            btn = gr.Button("Ask", variant="primary", size="lg")

    with gr.Row():
        answer_box = gr.Textbox(
            label="Answer",
            lines=8,
            interactive=False
        )

    with gr.Row():
        sources_box = gr.Textbox(
            label="Retrieved from (sources)",
            lines=4,
            interactive=False
        )

    # Example questions so the demo video is easy to follow
    gr.Examples(
        examples=[
            ["What platforms do students recommend for finding off-campus housing near UIC?"],
            ["What warnings do students give about Facebook housing listings?"],
            ["What rent should I expect sharing a place in Little Italy?"],
            ["What does the UIC CSRC help students with for off-campus housing?"],
            ["What is the best coffee shop near UIC?"]   # out-of-scope test
        ],
        inputs=inp
    )

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

if __name__ == "__main__":
    demo.launch()