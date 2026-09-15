import gradio as gr
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load rule documents, chunk them, and store in ChromaDB.

    If the vector store is already populated, ingestion is skipped.
    To re-ingest (e.g. after changing your chunking strategy), delete the
    ./chroma_db folder and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting rule documents...")
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc["text"], doc["game"])
        all_chunks.extend(chunks)

    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")
    else:
        print(
            "\n⚠️  No chunks produced. Make sure chunk_document() is implemented in ingest.py.\n"
            "    RulesBot will start, but won't be able to answer questions yet.\n"
        )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    return generate_response(message, retrieved)


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="indigo"),
    title="RulesBot",
) as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1.25rem 0 0.5rem;">
            <h1 style="font-size:2rem; font-weight:700; color:#312e81; margin:0;">
                🎲 RulesBot
            </h1>
            <p style="color:#6b7280; font-size:1rem; margin:0.4rem 0 0;">
                Ask anything about your board games — answers straight from the rulebook.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                type="messages",
                chatbot=gr.Chatbot(
                    height=440,
                    type="messages",
                    placeholder=(
                        "<div style='text-align:center; color:#6b7280; margin-top:3rem; font-size:1.05rem;'>"
                        "Ask a rules question to get started — no arguing required 🎯"
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "Can I build a road through someone else\'s settlement?"',
                    container=False,
                    scale=7,
                    show_label=False,
                ),
                examples=[
                    "How do you set up the board in Catan?",
                    "What happens if you roll a 7 in Catan?",
                    "How does the Spymaster give clues in Codenames?",
                    "What happens when a city gets a 4th disease cube in Pandemic?",
                    "Can two players claim the same route in Ticket to Ride?",
                    "How do you get out of Jail in Monopoly?",
                    "How does attacking work in Risk?",
                    "What is a Wild Draw Four and when can you play it in Uno?",
                    "How does making a Suggestion work in Clue?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=180):
            gr.HTML("""
                <div style="background:#f5f3ff; border:1px solid #ddd6fe;
                            border-radius:10px; padding:1rem; margin-top:0.5rem;">
                    <p style="font-size:0.8rem; font-weight:700; color:#4c1d95;
                               margin:0 0 0.5rem; letter-spacing:0.05em;">
                        📚 LOADED RULE BOOKS
                    </p>
                    <ul style="font-size:0.85rem; color:#1a1315; list-style:none;
                                padding:0; margin:0; line-height:1.8;">
                        <li>🏔️ Catan</li>
                        <li>🔍 Clue</li>
                        <li>🎯 Codenames</li>
                        <li>🏦 Monopoly</li>
                        <li>🦠 Pandemic</li>
                        <li>🌍 Risk</li>
                        <li>🚂 Ticket to Ride</li>
                        <li>🃏 Uno</li>
                    </ul>
                    <hr style="border:none; border-top:1px solid #ddd6fe; margin:0.75rem 0;">
                    <p style="font-size:0.75rem; color:#7c3aed; margin:0; line-height:1.5;">
                        Answers are grounded in the loaded rules only. If a rule
                        isn't in the books, RulesBot will say so.
                    </p>
                </div>
            """)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  RulesBot — starting up")
    print("="*50 + "\n")
    run_ingestion()
    demo.launch()
