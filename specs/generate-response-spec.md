# Spec: `generate_response()`

**File:** `generator.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user query and a list of retrieved rule chunks, generate a response that directly answers the question using only the retrieved text as context. The response must be grounded — it should not draw on the model's general knowledge of board games, only on what was retrieved.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's original question |
| `retrieved_chunks` | `list[dict]` | Ranked list of chunks from `retrieve()`, each with `"text"`, `"game"`, and `"distance"` |

**Output:** `str`

A plain string containing the response to show the user. The response should:
- Answer the question using only the retrieved rule text
- Identify which game the answer comes from
- Acknowledge clearly when the answer is not found in the loaded rules

Returns a fallback string (not an error) when `retrieved_chunks` is empty.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Context formatting

*How will you format the retrieved chunks before passing them to the LLM? Describe the structure — not the code. Consider: will you label chunks by game? Include distance scores? Separate chunks with delimiters?*

```
[Chunk 1]
Game: Catan
Distance: 0.12
text: [chunk text here]
--------------
[Chunk 2]
Game: Catan
Distance: 0.18
text: [chunk text here]
--------------
[Chunk 3]
Game: Pandemic
Distance: 0.25
text: [chunk text here]
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
You are a board game rules assistant. Answer questions using only the information provided in the retrieved rule book chunks. Do not use outside knowledge, prior training data, assumptions, or general knowledge about any game. If the retrieved chunks do not contain enough information to answer the question, do not guess or infer. Instead, return the fallback response exactly as specified.

```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
For every answer, identify the game that the supporting information came from. Include a citation in the format:

Source:

If information from multiple games is used, list all relevant game names.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
I could not find enough information in the loaded rule books to answer that question.

```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Approach:

Pass only the top-k retrieved chunks to the model.
Optionally filter chunks above a distance threshold (for example, distance > 0.5).

Tradeoffs:

Filtering reduces noise and hallucinations.
Aggressive filtering may remove useful chunks and increase "I don't know" responses.
Passing all chunks increases recall but may confuse the model with irrelevant information.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
System message: include the grounding instruction and the citation instruction together.
User message: include the original user query plus the formatted retrieved chunks as the context for the answer.

Example:

Context:
[Chunk 1]
Game: Catan
Distance: 0.12
text: ...

[Chunk 2]
Game: Catan
Distance: 0.18
text: ...

Question:
What happens when a player rolls a 7?
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: what is aa23?

Response: I could not find enough information in the loaded rule books to answer that question.

Correctly grounded? yes
Cited the right game? yes
```

**One thing you changed from your original spec after seeing the actual output:**

```
[your answer here]
```
