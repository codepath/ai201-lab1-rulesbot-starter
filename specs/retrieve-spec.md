# Spec: `retrieve()`

**File:** `retriever.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Given a user's natural language query, find the most relevant chunks from the vector store using semantic similarity search. Return them ranked by relevance so that `generate_response()` can use them as context.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The user's natural language question |
| `n_results` | `int` | Maximum number of chunks to return (default: `N_RESULTS` from `config.py`) |

**Output:** `list[dict]`

Each dict in the returned list must contain exactly these keys:

| Key | Type | Description |
|-----|------|-------------|
| `"text"` | `str` | The chunk text |
| `"game"` | `str` | The game name this chunk came from |
| `"distance"` | `float` | Cosine distance score — lower means more similar to the query |

Results should be ordered from most to least relevant (lowest to highest distance). Returns an empty list `[]` if the collection contains no documents.

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Query approach

*Describe how you will use `_collection.query()` to find relevant chunks. What arguments will you pass, and why?*

```
I'd use `_collection.query()` to run a semantic similarity vector search to find top n chunks that have cosine similarity score closed to the user query. Some arguments I need to pass are:
    - query_texts : a list containing your query string
    - n_results   : how many results to return
    - include     : what to return — use ["documents", "metadatas", "distances"]
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
Each item in the return list will have these fields:
    - "text"     : the chunk text
    - "game"     : the game name (pull this from metadatas)
    - "distance" : the similarity score (lower = more similar for cosine)
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
we'd need to use index 0 to get the actual results, as we only have a single query.
Nesting exists because `_collection.query()` takes a list of query_texts as an input
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
Results that have similarity score higher than a certain threshold can be identified as irrelevant and thus we may discard them instead of trying to return all `n_results`. The tradeoff are between precision + complexity of the RAG system vs. recall

Lower = more similar. A score around 0.1–0.2 means highly relevant; around 0.7–0.9 means loosely related at best.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) If the collection is empty, `retrieve()` returns `[]` immediately.

(b) If the query matches no chunks well, the function should return only the highest-ranked chunks that still pass the relevance threshold; if none are relevant, it should return `[]` so `generate_response()` can fall back cleanly instead of using weak context.

(c) If the query matches chunks from multiple games, `retrieve()` should return the top-ranked chunks across all games, sorted by distance, without forcing them to come from just one game. The final answer can then cite the relevant game(s) from the returned metadata.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: "What happens when you roll a 7?"
Top result: [Catan] (dist: 0.567)
            [Risk] (dist: 0.617)
            [Codenames] (dist: 0.629)
Does it make sense? not really, multiple games are returned while only catan is relevant

Query: "How do you win?"
Top result: [Clue] (dist: 0.632)
            [Risk] (dist: 0.664)
            [Risk] (dist: 0.695)
Does it make sense? no, scores are high

Query: "What happens when you run out of disease cubes in Pandemic?"
Top result: [Pandemic] (dist: 0.459)
            [Pandemic] (dist: 0.485)
            [Pandemic] (dist: 0.575)
Does it make sense? yes, all belong to Pandemic
```

**One thing about the query results that surprised you:**

```
the similarity score remains similar, fluctuating around 0.5, even for different value of chunk_size, overlap, and min_length 
```
