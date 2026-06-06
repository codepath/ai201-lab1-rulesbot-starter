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
[
    I will format each retrieved chunk as:

    Game: <game name>
    Text: <retrieved chunk text>

    Chunks will be separated by a delimiter line to make the context easier for the model to read. I will include the game name because the response must identify which game the answer comes from. I will not include distance scores because they are useful for retrieval but may confuse the language model and are not directly relevant to answering the question. 

    Include Distance
    Advantages: The model may know which chunks are important.
    Disadvantages: Increases prompt complexity; the model may not understand distance.

    Exclude Distance
    Advantages: Concise prompt, reduces interference.
    Disadvantages: The model cannot see similarity information.

    eg. 
    Game: Uno
    Text: A reverse card changes play direction.

    ---

    Game: Chess
    Text: A player wins by checkmate.
]
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
[
    Answer using only the retrieved rule text provided in the context.
    If the answer is not contained in the retrieved text, explicitly state that the information is not available in the loaded rule books.
    Do not use outside knowledge, make assumptions, or fill in missing information.
]
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
[
    Always identify the game that supports the answer. If multiple games are relevant, clearly indicate which information comes from each game.
]
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
[
    "I couldn't find anything relevant in the loaded rule books. "
    "Try rephrasing your question — or check that your ingestion pipeline is working."
    (if retrieved_chunks == [], then throw the fallback ans.)
]
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
[
    I would pass all retrieved chunks to the model rather than filtering by a distance threshold.

    Advantages:
    - Avoids accidentally removing useful information.
    - Keeps the retrieval process simple.

    Disadvantages:
    - Some weakly related chunks may introduce noise.
    - The model may receive less relevant context.

    An alternative approach is to filter results above a distance threshold. This can improve precision and reduce noise, but it risks excluding relevant chunks if the threshold is too strict.

    =======================

    There are several possible approaches for handling low-relevance chunks.

    A simple approach is to pass all retrieved chunks to the language model. This works well when n_results is small because the amount of context is limited, and the risk of introducing irrelevant information is relatively low.

    Another approach is to apply a distance threshold and filter out chunks whose distance scores exceed a predefined value. This can improve precision and reduce noise, but it may accidentally remove useful information if the threshold is too strict.

    In production RAG systems, a common strategy is to combine both approaches. The retriever first returns a larger set of candidate chunks (for example, the top 5–10 results), and then filtering or re-ranking is applied before sending the final context to the language model. This helps balance recall (not missing relevant information) and precision (reducing irrelevant context).

    For this project, I would pass all retrieved chunks when n_results is small. If n_results becomes larger, I would consider applying a relevance threshold or a re-ranking step to reduce noise while preserving useful information.
]
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
[
    The system message will contain the grounding rules and citation instructions. It will tell the model to answer only from the retrieved text, avoid outside knowledge, and identify the relevant game.

    The user message will contain the original query along with the formatted retrieved chunks. This provides the question and supporting context needed to generate the answer.
]
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
