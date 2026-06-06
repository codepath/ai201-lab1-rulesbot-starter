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
[I will call _collection.query() with query_texts=[query], n_results=n_results, and include=["documents", "metadatas", "distances"].
query_texts must be a list because ChromaDB supports multiple queries at once. n_results controls how many relevant chunks to return. include tells ChromaDB to return the chunk text, metadata such as the game name, and the distance score.]
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
[
    One item in the returned list looks like:

{
    "text": "A reverse card changes the direction of play.",
    "game": "Uno",
    "distance": 0.08
}

The "text" field comes from results["documents"][0][i], which contains the retrieved chunk text.

The "game" field comes from results["metadatas"][0][i]["game"], which stores the game name in the metadata.

The "distance" field comes from results["distances"][0][i], which represents how similar the chunk is to the query. Smaller distances indicate more relevant results.
]
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
[
    Because _collection.query() accepts multiple query texts, it returns one list of results per query. Since I only pass one query with query_texts=[query], I use index [0] to access the actual results for that single query, like results["documents"][0], results["metadatas"][0], and results["distances"][0].
]
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
[
    There are two possible approaches:

1. Return all n_results (n_results=3)

In this approach, the retriever returns all results provided by ChromaDB, regardless of their distance scores.

Advantages:
- Simple to implement and understand.
- Reduces the risk of filtering out potentially useful chunks.
- Works well when the embedding model's distance scores are not well calibrated.

Disadvantages:
- Some returned chunks may be only weakly related to the query.
- Additional irrelevant context may increase prompt size and token usage.
- Noisy results could negatively affect the LLM's final answer.

2. Apply a relevance threshold (if distance < 0.5:)

In this approach, results with distance scores above a chosen threshold are filtered out before being returned.

Advantages:
- Improves precision by removing less relevant chunks.
- Reduces noise in the retrieved context.
- Can improve answer quality when the threshold is chosen appropriately.

Disadvantages:
- Relevant chunks may be accidentally removed if the threshold is too strict.
- The best threshold often depends on the embedding model and dataset.
- In some cases, very few or even no results may be returned.

For this assignment, I would return all n_results without applying a threshold because it keeps the retriever simple and avoids accidentally discarding useful information. However, a relevance threshold could be added later to improve retrieval quality after evaluating the distance score distribution.
]
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
