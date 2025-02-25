import os
import hashlib
from dotenv import load_dotenv
import gradio as gr
from engine import ingest_and_answer

load_dotenv()

def web_ui():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Web Content Q&A Tool")
        
        with gr.Row():
            url_input = gr.Textbox(
                label="Enter URLs (comma-separated)",
                placeholder="https://example.com, https://anotherexample.org"
            )
            question_input = gr.Textbox(
                label="Ask a question",
                placeholder="What's the main topic of these pages?"
            )
        
        submit_btn = gr.Button("Get Answer", variant="primary")
        answer_output = gr.Textbox(label="Answer", interactive=False)
        
        gr.Examples(
            examples=[
                [
                    "https://en.wikipedia.org/wiki/Large_language_model, https://www.ibm.com/topics/large-language-models",
                    "What are the key applications of LLMs?"
                ]
            ],
            inputs=[url_input, question_input]
        )

        submit_btn.click(
            fn=lambda urls, q: ingest_and_answer([u.strip() for u in urls.split(",")], q),
            inputs=[url_input, question_input],
            outputs=answer_output
        )

    demo.launch(server_name="0.0.0.0", server_port=7870)

if __name__ == "__main__":
    web_ui()