# 🎲 RulesBot

> A board game rules assistant — because "just read the rulebook" isn't always helpful at 11pm on game night.

RulesBot answers natural language questions about board game rules using a RAG (Retrieval-Augmented Generation) pipeline. Ask it anything: it retrieves relevant rule passages and generates an answer grounded in the actual text.

**This is a starter repo.** The UI and infrastructure are built. The retrieval and generation pipeline is yours to implement.

---

## Getting Started

### 1. Fork and clone

Fork this repo, then clone your fork locally.

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # Mac/Linux
# or: .venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `sentence-transformers` will download the embedding model (~80MB) on first run. This only happens once — it's cached locally afterward.

### 4. Add your Groq API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_key_here` with your key from [console.groq.com](https://console.groq.com). No credit card required.

### 5. Run the app

```bash
python app.py
```

RulesBot will start and open in your browser. Before you implement the retrieval pipeline, it will load and display the UI but won't be able to answer questions.

---

## Project Structure

```
ai201-lab1-rulesbot-starter/
├── app.py              # Gradio UI and startup logic — fully built
├── config.py           # Settings (models, paths, retrieval params) — fully built
├── ingest.py           # Document loading + chunking (complete)
├── retriever.py        # Vector store + semantic search — TODO: retrieve()
├── generator.py        # LLM response generation — TODO: generate_response()
├── docs/               # Board game rule documents (pre-loaded)
│   ├── catan.txt
│   ├── clue.txt
│   ├── codenames.txt
│   ├── monopoly.txt
│   ├── pandemic.txt
│   ├── risk.txt
│   ├── ticket_to_ride.txt
│   └── uno.txt
├── specs/              # Design documents — start here before writing any code
│   ├── system-design.md         # Complete — read this first
│   ├── chunk-document-spec.md   # Partial — you complete before Milestone 1
│   ├── retrieve-spec.md         # Partial — you complete before Milestone 2
│   └── generate-response-spec.md # Partial — you complete before Milestone 3
└── planning.md         # Your observations and reflections — fill in as you go
```

## Where to Start

Before opening any `.py` file, read `specs/system-design.md`. It explains what's built, what's left for you, and why the technical decisions were made. Each milestone then begins by completing the corresponding spec file before writing code — that spec becomes the brief you hand to your AI tool when you're ready to implement.

---

## Re-ingesting After Changes

ChromaDB persists to disk in `./chroma_db`. If you change your chunking strategy and want to re-ingest, delete that folder and restart the app:

```bash
rm -rf chroma_db/   # Mac/Linux
# or: rmdir /s /q chroma_db   # Windows
python app.py
```

---

## Rule Books Included

| Game | File |
|------|------|
| Catan | `docs/catan.txt` |
| Clue | `docs/clue.txt` |
| Codenames | `docs/codenames.txt` |
| Monopoly | `docs/monopoly.txt` |
| Pandemic | `docs/pandemic.txt` |
| Risk | `docs/risk.txt` |
| Ticket to Ride | `docs/ticket_to_ride.txt` |
| Uno | `docs/uno.txt` |
