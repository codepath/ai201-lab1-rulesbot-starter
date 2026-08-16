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
[your answer here]
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
One returned item is a flat dict that joins three parallel lists from
_collection.query(), aligned by the same index i:

  {
      "text":     "On your turn, roll both dice...",   # documents[0][i]
      "game":     "Catan",                              # metadatas[0][i]["game"]
      "distance": 0.41,                                 # distances[0][i]
  }

Field provenance (all under index [0], the first/only query):
  - "text"     <- results["documents"][0][i]
                  the raw chunk string, same value stored as c["text"]
                  in embed_and_store().
  - "game"     <- results["metadatas"][0][i]["game"]
                  unwrapped from the metadata dict; "game" is the only key
                  embed_and_store() saved per chunk.
  - "distance" <- results["distances"][0][i]
                  cosine distance (lower = more similar), because the
                  collection is created with metadata={"hnsw:space": "cosine"}.

I build the list by zipping documents[0], metadatas[0], and distances[0]
together so text/game/distance always stay aligned to the same chunk.
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
I need index [0] on each returned list (documents, metadatas, distances).

query() is designed to accept a *batch* of queries via query_texts=[...].
So the result lists have one outer slot per query: the outer list is
indexed by query number, and the inner list holds that query's actual
results. The shape is:

    results["documents"] = [ [chunks for query 0], [chunks for query 1], ... ]

I only ever pass a single query (query_texts=[query]), so there is exactly
one outer slot. results["documents"][0] is the list of chunk texts for my
query, results["metadatas"][0] the matching metadata dicts, and
results["distances"][0] the matching distances. Forgetting the [0] would
leave me iterating over the per-query wrapper instead of the actual chunks.
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
I'll return all n_results (N_RESULTS = 3) regardless of distance — no
threshold filter for now.

Reasoning / tradeoffs:

Option A — return all n_results (chosen):
  + Simple and predictable: generate_response() always gets up to 3 chunks
    of context to work with.
  + With N_RESULTS = 3 the result set is already small, so a few weak matches
    add little noise, and the LLM can ignore irrelevant context.
  - Risk: on an off-topic query, all 3 chunks may be only loosely related,
    and passing them as "context" could nudge the model toward a confident
    but wrong answer (hallucination from weak grounding).

Option B — filter out results above a distance cutoff (e.g. distance > 0.8):
  + Cleaner context: clearly irrelevant chunks never reach the prompt, and
    an empty result can signal "I don't have rules on that."
  - cosine distance values are not intuitively calibrated; a good threshold
    depends on the embedding model (all-MiniLM-L6-v2) and the corpus, so a
    hard-coded number is easy to get wrong and may silently drop good matches.
  - Adds a tuning knob and a "no results" branch to handle downstream.

Choice for this milestone: Option A for simplicity. If hallucination on
off-topic questions becomes a problem, revisit by adding a distance cutoff
(or letting generate_response() decline when the best distance is too high)
rather than baking a fragile threshold into retrieve() now.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
[your answer here]
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: [your test query]
Top result game: [game name]
Distance score: [score]
Does it make sense? [yes / no / explain]
```

**One thing about the query results that surprised you:**

```
[your answer here]
```
