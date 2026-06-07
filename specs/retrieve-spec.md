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
I will use this '_collections.query()' to find the relevant chunks that will answer the user query. I pass query_texts(which has user query text in natural language and it has lists of user queries since chromaDB accepts like that), n_results(It returns the top matching results from the embedding collection stored), include(Here we include which parameters to output such as text, metadata and distance(which is cosine similarity score here))
```

---

### Return structure

*Sketch out what one item in your return list looks like as a concrete example. Where does each field come from in the query results?*

```
results = _collection.query(
    query_texts=["how do you win at catan?"],
    n_results=3,
    include=["documents", "metadatas", "distances"],
)

results contain
{
    "documents": [
        [
            "The first matched chunk text",
            "The second matched chunk text",
            "The third matched chunk text"
        ]
    ],
    "metadatas": [
        [
            {"game": "catan"},
            {"game": "catan"},
            {"game": "catan"}
        ]
    ],
    "distances": [
        [0.12, 0.18, 0.23]
    ]
}

the each field comes from the ones we put in the 'include' field in the input. 
```

---

### Handling the nested result structure

*`_collection.query()` returns nested lists. Describe what index you need to access to get the actual list of results for a single query, and why the nesting exists.*

```
In the results, for every dict, we use the index - 0, since we have only sent in one user query. It will look like
results = _collection.query(
    query_texts=["how do you win at catan?"],
    n_results=3,
    include=["documents", "metadatas", "distances"],
)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]
```

---

### Relevance threshold

*Will you filter out results above a certain distance score, or return all `n_results` regardless of how relevant they are? What are the tradeoffs of each approach?*

```
I will return all `n_results` without a distance threshold initially, because:
- It guarantees results whenever the collection is not empty
- Ensures the LLM has context to work with, even if similarity is lower
- Filtering by distance threshold might return 0 results if the threshold is too strict

If I filter by a distance threshold after getting n_results:
- Results could be fewer than requested (or empty)
- Quality improves by removing weak matches
- But I lose the guarantee of getting any results

I'll use n_results for now and optionally add threshold filtering later based on testing.
```

---

### Edge cases

*How does your implementation behave when: (a) the collection is empty, (b) the query matches no chunks well, (c) the query matches chunks from multiple games?*

```
(a) when collection is empty, we don't get any response. 
(b) when query matches no chunks well, it's giving me the more distance with other chunks
(c) when query matches chunks from multiple games, it's giving me the one with more less score
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**Test query and top result returned:**

```
Query: how to come out of jail?
Top result game: Monopoly
Distance score: 0.336
Does it make sense? yes, that chunk contains the answer. The LLM model can answer that. 
```

**One thing about the query results that surprised you:**

```
[your answer here]
```
