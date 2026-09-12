import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Groq retired every Llama chat model in 2026. gpt-oss-20b is a Production-tier
# replacement. It reasons before it answers, and the reasoning tokens count
# against max_tokens. Leave max_tokens unset, or set it to 1000+, or pass
# reasoning_effort="low" (groq>=1.1.2). A tight cap returns an empty string.
LLM_MODEL = "openai/gpt-oss-20b"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "rulesbot"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 3

# --- Documents ---
DOCS_PATH = "./docs"
