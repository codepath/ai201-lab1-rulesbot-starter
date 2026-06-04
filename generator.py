from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

_client = Groq(api_key=GROQ_API_KEY)


def generate_response(query, retrieved_chunks):
    """
    Generate a grounded answer from retrieved rule chunks.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk["distance"] <= 0.5
    ]

    if not relevant_chunks:
        return "I could not find enough information in the loaded rule books to answer that question."

    context_parts = []

    for chunk in relevant_chunks:
        context_parts.append(
            f"[Game: {chunk['game']} | Distance: {chunk['distance']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)

    system_message = """
You are RulesBot, a board game rules assistant.

Answer the user's question using only the retrieved rule text provided in the context.
Do not use outside knowledge.
Do not make assumptions.
If the answer is not clearly supported by the retrieved text, say that the loaded rules do not contain enough information to answer.

Clearly identify which game the answer comes from using wording like:
"According to the Catan rules..." or "Based on the Uno rules..."
"""

    user_message = f"""
User question:
{query}

Retrieved rule context:
{context}
"""

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content