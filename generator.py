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


    # Your implementation here.

    # step1: Format the retrieved chunks into a context block for the prompt, then call the LLM to generate a grounded answer.
    context = "\n\n".join(
        f"From [{chunk['game']}]:\n{chunk['text']}" 
        for chunk in retrieved_chunks
    )

    # step2: Grounding System Prompt
    # Craft instructions to ensure the model answers only based on the provided context, and clearly indicates when information is missing.
    system_prompt = (
        "You are a board game rules assistant that answers questions about board game rules based solely on the provided context. "

        "Use ONLY the the retrieved rule text provided. "

        "If the answer is not in the provided rules, say 'I don't know based on the provided rules.' "

        "Do not use outside knowledge. Do not make assumptions. Do not fill in missing information."

        "Clearly indicate which game each piece of information comes from."
    )

    # step3: Call the LLM with the system prompt and the context to generate a response.
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system", 
                "content": system_prompt
             },
            {
                "role": "user", 
                "content": f"""
                Question:{query}\n
                Context:{context}\n"""
             }
        ]
    )

    # step4: Return the generated response as a plain string.
    return response.choices[0].message.content.strip()

