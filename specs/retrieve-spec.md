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
[I will call _collection.query() with query_texts=[query], n_results=n_results, and include=["documents", "metadatas", "distances"]. The query_texts argument contains the user's question so ChromaDB can embed it and compare it to the stored rule chunks. n_results controls how many top matches are returned.]
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
[One returned item will look like this:

{
  "text": "If you roll a 7, no player receives resources...",
  "game": "Catan",
  "distance": 0.23
}

The "text" field comes from results["documents"][0][i]. The "game" field comes from results["metadatas"][0][i]["game"]. The "distance" field comes from results["distances"][0][i].]
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
[Because _collection.query() can process multiple queries at once, it returns nested lists. Since this app sends only one query at a time, I need to access index [0] first. For example, results["documents"][0] gives the list of retrieved documents for the single user query.]
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
[I will return the top n_results from retrieve() and let generate_response() decide whether chunks are too weak to use. The tradeoff is that retrieve() stays simple and always returns the best available matches, but generate_response() must be careful not to answer from irrelevant chunks with high distance scores.]
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
[(a) If the collection is empty, the function returns [].
(b) If the query matches no chunks well, it still returns the closest chunks, but they may have high distance scores. The generator can then use a fallback response.
(c) If the query matches chunks from multiple games, the function returns them ranked by distance. This allows the generator to mention the correct game or clarify when the retrieved context comes from more than one game.]
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: [return the relevant answer]
Top result game: [game Catan]
Distance score: [score]
Does it make sense? [yes it does makes sense cause it was put first on the top result]
```

**One thing about the query results that surprised you:**

```
[The Answer was just right as described in generate]
```
