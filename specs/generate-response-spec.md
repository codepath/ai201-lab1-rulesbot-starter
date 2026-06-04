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
I will pass the top-N retrieved_chunks as distinct, labeled context blocks separated by a clear delimiter (e.g., ---); each block will show Game: <name>, ChunkID: <id>, (optionally Distance: <score> only for diagnostics/thresholding), and then the chunk Text. I’ll order blocks by ascending distance (most relevant first), apply a distance threshold to drop weak matches (e.g., >0.5) and limit total tokens by truncating or omitting lower-ranked blocks, and avoid including distance values in the user-facing answer—distance is used only to filter and sort. This keeps provenance (which game) explicit, prevents the LLM from merging unrelated passages, and ensures generate_response() receives concise, high-quality context it can quote and cite.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
"Answer using only the retrieved rule text below; do not use outside knowledge or guess. Do not fabricate, infer, or add information not present in the context. Keep answers brief and grounded."
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
"If the answer is clearly present in the provided text, respond concisely and cite sources using this format: [Game: <game>]"
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
"If the text does not contain the answer, reply exactly: "I don't know - the answer is not found in the provided rule text."
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
I'll filter them out before building the context
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
I'd use a two-message sequence:

- System message: an authoritative grounding/instruction prompt that sets rules for the model (do not use outside knowledge, only use the provided context, exact fallback text, citation format, brevity requirement, how to handle ambiguity/conflicts). 

- User message: contains the user’s original question plus the formatted context blocks to use as evidence. The context should be the top‑N retrieved chunks (already filtered/thresholded), each separated by a clear delimiter and labeled with Game, ChunkID, (optional Distance for diagnostics) and Text. End the user message with a final instruction like: “Using only the context above, answer the question: <user query>. Provide a concise answer and include citation(s) in the required format.”
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: [your test query]
Response: [abbreviated response]
Correctly grounded? [yes / no]
Cited the right game? [yes / no]
```

**One thing you changed from your original spec after seeing the actual output:**

```
[your answer here]
```
