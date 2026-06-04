from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


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
      2. Make clear which game the answer comes from (citing the game name)
      3. Clearly indicate when the answer isn't in the loaded rules

    Return the response as a plain string or a fallback string when retrieved_chunks is empty..
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    # Parameters
    MAX_CHUNKS = 5                 # include at most this many chunks in context
    DISTANCE_THRESHOLD = 0.7       # drop weak matches (higher distance = less similar)

    # Filter low-relevance chunks and take top-N (chunks are already sorted by distance)
    filtered = [c for c in retrieved_chunks if c.get("distance", 1.0) <= DISTANCE_THRESHOLD]
    if not filtered:
      # If none pass threshold, fall back to empty-answer behavior
      return "I don't know - the answer is not found in the provided rule text."

    top_chunks = filtered[:MAX_CHUNKS]

    # Build the context blocks separated by delimiters. Include ChunkID if present.
    context_blocks = []
    for c in top_chunks:
      chunk_id = c.get("chunk_id") or c.get("id") or "unknown"
      context_blocks.append(
        "---\n"
        f"Game: {c.get('game', 'unknown')} | ChunkID: {chunk_id} | Distance: {c.get('distance', 0):.4f}\n"
        "Text: " + c.get("text", "") + "\n"
      )

    context_text = "\n".join(context_blocks)

    # System prompt — grounding instruction (strict)
    system_prompt = (
      "Answer using only the retrieved rule text below; do not use outside knowledge or guess. "
      "Do not fabricate, infer, or add information not present in the context. "
      "If the text does not contain the answer, reply exactly: I don't know - the answer is not found in the provided rule text. "
      "If multiple chunks conflict or are ambiguous, state that the rules are ambiguous and list the relevant citations. "
      "Cite sources using the format: [Citation: <game>]. Keep answers concise and quote verbatim only when explicitly quoting."
    )

    # User prompt: include the context and the user's question
    user_prompt = (
      "CONTEXT:\n" + context_text + "\n"
      "QUESTION: " + query + "\n\n"
      "Using only the context above, answer the question concisely and include citation(s) in the format [Citation: <game>]. "
      "If the answer is not present, reply exactly: I don't know - the answer is not found in the provided rule text."
    )

    # Call the Groq client.
    try:
      response = _client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model=LLM_MODEL, max_tokens=512)
      return response.choices[0].message.content.strip()
    except Exception:
      return "Exception occurred while generating response. "
        
