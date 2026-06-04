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
[I will format each retrieved chunk with a clear label showing the game name, the distance score, and the chunk text. I will separate chunks with delimiters so the LLM can tell where one chunk ends and the next begins. Example:

[Game: Catan | Distance: 0.23]
<chunk text>

---
[Game: Monopoly | Distance: 0.31]
<chunk text>]
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
[You are RulesBot, a board game rules assistant. Answer the user's question using only the retrieved rule text provided in the context. Do not use outside knowledge or make assumptions. If the answer is not clearly supported by the retrieved text, say that the loaded rules do not contain enough information to answer.]
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
[In your answer, clearly identify the game name that supports the answer, using wording like "According to the Catan rules..." or "Based on the Uno rules...".]
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
[I could not find enough information in the loaded rule books to answer that question.]
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
[I will filter out chunks with distance scores above 0.5 before building the context. This helps prevent the model from answering using weak or unrelated passages. The tradeoff is that some useful chunks might be removed if their distance score is slightly high, but it is safer for a grounded rules assistant to say it does not know than to answer from irrelevant text.]
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
[The system message will contain the grounding instructions, citation instructions, and fallback behavior. The user message will contain the user's question plus the formatted retrieved chunks as context. This keeps the model focused on answering the question from the provided rule text only.]
```

---

## Implementation Notes

*Fill this in after implementing and testing.*

**Test query and response:**

```
Query: [what happens when you roll a 7 in Catan?]
Response: [According to...]
Correctly grounded? [yes ]
Cited the right game? [yes ]
```

**One thing you changed from your original spec after seeing the actual output:**

```
[I did not change anything but this was impressive]
```
