from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)

# Shared so the model's "not found" reply and the empty-results fallback match.
FALLBACK_MESSAGE = (
    "I couldn't find that in the loaded rule books. Try rephrasing your "
    "question, or make sure the relevant rulebook has been ingested."
)

# System prompt = grounding instruction + citation instruction (the rules of
# engagement that never change per query). See generate-response-spec.md.
SYSTEM_PROMPT = (
    "You are a board game rules assistant. Answer the user's question using "
    "ONLY the rule text provided in the context below. Do not use any outside "
    "or prior knowledge about board games, even if you are confident you know "
    "the answer. If the context does not contain enough information to answer "
    "the question, reply exactly: 'I couldn't find that in the loaded rule "
    "books.' Do not guess, infer beyond what the text states, or fill gaps "
    "with general knowledge. Quote or paraphrase only what the context "
    "supports.\n\n"
    "Always state which game your answer comes from. Begin your reply with the "
    "game name in brackets, e.g. '[Catan] ...'. The game name is given in the "
    "bracketed label above each passage in the context. If your answer draws "
    "on more than one game, name each game you used."
)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.

    TODO — Milestone 3:

    `retrieved_chunks` is the list returned by retrieve(). Each item is a dict:
      - "text"     : the chunk text
      - "game"     : the game name
      - "distance" : similarity score (you can use this to filter weak matches)

    Before writing code, talk through these with your group:
      - How will you format the chunks into a context block for the prompt?
      - What instructions will stop the model from answering beyond what the
        rules say? (Grounding is the whole point — a confident wrong answer
        is worse than an honest "I don't know.")
      - How will you surface which game each answer comes from?

    Your response should:
      1. Answer using only the retrieved context — not the model's general knowledge
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return FALLBACK_MESSAGE

    # Build the context block: each chunk labeled by game, separated by a
    # visible delimiter, in retrieve()'s order (most relevant first).
    context_block = "\n---\n".join(
        f"[{chunk['game']}]\n{chunk['text']}" for chunk in retrieved_chunks
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context_block}\n\nQuestion: {query}",
        },
    ]

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content
