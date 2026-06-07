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
      2. Make clear which game the answer comes from
      3. Say so clearly when the answer isn't in the loaded rules

    Return the response as a plain string.
    """
    if not retrieved_chunks:
        return (
            "I couldn't find anything relevant in the loaded rule books. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, start=1): 
       context_parts.append( f"[Chunk {i}]\n" f"Game: {chunk['game']}\n" f"Distance: {chunk['distance']}\n" f"text: {chunk['text']}\n" f"--------------" )
    
    context = "\n".join(context_parts)

    system_prompt = """

    You are a board game rules assistant. Answer questions using only the information provided in the retrieved rule book chunks. Do not use outside knowledge, prior training data, assumptions, or general knowledge about any game. If the retrieved chunks do not contain enough information to answer the question, do not guess or infer. Instead, return the fallback response exactly as specified.

    For every answer, identify the game that the supporting information came from. Include a citation in the format:

    Source:

    If information from multiple games is used, list all relevant game names.

    Fallback response:
    I could not find enough information in the loaded rule books to answer that question.
    """

    user_prompt = f"""

    Context:
    {context}

    Question:
    {query}
    """

    response = _client.chat.completions.create(
       model=LLM_MODEL,
       messages=[
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": user_prompt},
      ],
  )

    
    # Your implementation here.
    return response.choices[0].message.content.strip()