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
I'll join the retrieved chunks into a single "context block" string, where
each chunk is labeled with its source game and separated by a clear delimiter.
Conceptual shape:

    [Catan]
    On your turn, roll both dice. Every settlement adjacent to a hex...
    ---
    [Catan]
    When a 7 is rolled, no resources are produced. Every player with...
    ---
    [Risk]
    The attacker rolls up to 3 dice...

Decisions and why:
  - Label each chunk by GAME ([game] header): the model needs the game name
    to satisfy the citation requirement, and labeling per-chunk lets it tell
    apart chunks from different games when a query pulls from several. The
    game comes from chunk["game"].
  - Separate chunks with a visible delimiter (e.g. a line of "---"): keeps the
    model from blending two unrelated rules into one continuous passage and
    makes chunk boundaries explicit.
  - Do NOT include distance scores in the context: they're an internal
    retrieval signal, not rule content. Showing them would add noise and might
    tempt the model to editorialize about confidence. (Distance is still used
    in code — see "Handling low-relevance chunks" — just not shown to the LLM.)
  - Preserve the chunk text verbatim (no summarizing) so grounding stays exact.
  - Keep the retrieve() ordering (lowest distance first) so the most relevant
    rule appears at the top of the context block.

This block is inserted into the prompt as the model's sole source of truth,
paired with the grounding instruction from the system-prompt field.
```

---

### System prompt — grounding instruction

*Write the exact system prompt instruction you will use to prevent the model from answering beyond the retrieved text. This is the most important design decision in this function.*

```
Exact instruction placed in the system message:

"You are a board game rules assistant. Answer the user's question using ONLY
the rule text provided in the context below. Do not use any outside or prior
knowledge about board games, even if you are confident you know the answer.
If the context does not contain enough information to answer the question,
reply exactly: 'I couldn't find that in the loaded rule books.' Do not guess,
infer beyond what the text states, or fill gaps with general knowledge. Quote
or paraphrase only what the context supports."

Why this wording:
  - "ONLY ... context below" + "Do not use outside or prior knowledge" draws a
    hard boundary so the model treats the retrieved chunks as its sole source.
  - "even if you are confident" specifically counters the model's tendency to
    override weak context with its (often correct, but ungrounded) training
    knowledge — a confident wrong/ungrounded answer is the failure mode we
    most want to avoid.
  - Giving an exact fallback sentence makes "I don't know" a first-class,
    predictable output instead of a hallucinated answer, and lets the UI
    detect the not-found case reliably.
  - "Do not guess / infer beyond / fill gaps" closes the common loopholes the
    model uses to rationalize answering anyway.
```

---

### System prompt — citation instruction

*Write the exact instruction you will use to tell the model to identify which game its answer comes from.*

```
Exact instruction (appended to the system message):

"Always state which game your answer comes from. Begin your reply with the
game name in brackets, e.g. '[Catan] ...'. The game name is given in the
bracketed label above each passage in the context. If your answer draws on
more than one game, name each game you used."

Why:
  - The bracketed game label matches how the context block is formatted
    (see "Context formatting"), so the model has the game name right next to
    each passage and doesn't have to infer it.
  - Forcing the [Game] prefix gives a consistent, predictable format the UI
    (and the student grading) can rely on, and makes the source obvious to
    the user.
```

---

### Fallback behavior

*What should the response say when the answer isn't found in the loaded rule books? Write the exact fallback message.*

```
Exact fallback message (used for both the empty retrieved_chunks case and
when the model determines the context doesn't answer the question):

"I couldn't find that in the loaded rule books. Try rephrasing your question,
or make sure the relevant rulebook has been ingested."

Notes:
  - The grounding instruction tells the model to reply with the first sentence
    ("I couldn't find that in the loaded rule books.") when the context is
    insufficient, so the model's not-found answer and the code's empty-list
    fallback share the same wording — one consistent failure message.
  - It's phrased as a normal answer, never an error/exception, per the
    Input/Output contract.
```

---

### Handling low-relevance chunks

*`retrieved_chunks` may include chunks with high distance scores (weak relevance). Will you filter these out before building context, pass them all in, or handle them another way? What are the tradeoffs?*

```
Decision: pass all retrieved chunks into the context (labeled by game), and
rely on the grounding instruction to ignore any that don't actually answer
the question. No hard distance cutoff in generate_response().

Reasoning / tradeoffs:
  - Why not a hard threshold: cosine-distance cutoffs are model- and
    corpus-specific and fragile (see the Relevance threshold field in
    retrieve-spec.md). The observed gap for one query (good 0.466 vs weak
    0.597) would NOT generalize into a safe global cutoff, and a too-tight
    threshold can silently drop genuinely relevant chunks.
  - Why passing all is safe enough: every chunk carries a [Game] label and the
    grounding instruction forbids using unsupported context, so for a Catan
    question the model answers from the Catan chunk and ignores the off-topic
    Risk chunks. The labels make wrong-game text easy for the model to skip.
  - Cost of this choice: a few extra tokens, and a small residual risk the
    model anchors on a wrong-game chunk. Mitigated by per-chunk game labels +
    the strong grounding prompt, and acceptable because N_RESULTS is only 3.
  - If anchoring on wrong-game chunks shows up in testing, the cheap next step
    is a soft filter (drop chunks whose distance is far above the best match,
    e.g. > best_distance + margin) rather than a fixed absolute cutoff.
```

---

### Message structure

*Describe how you will structure the messages list for the API call — what goes in the system message vs. the user message?*

```
Two messages:

  system: the model's role + the rules of engagement that never change per
          query — the grounding instruction and the citation instruction.
          This is fixed behavior, so it belongs in the system role.

  user:   the per-query content — the formatted context block (game-labeled
          chunks separated by delimiters) followed by the user's actual
          question. Putting the retrieved context here keeps the "data" in the
          user turn and the "instructions" in the system turn.

Shape:
  messages = [
      {"role": "system", "content": <grounding + citation instructions>},
      {"role": "user",   "content": "Context:\n<context block>\n\n"
                                     "Question: <query>"},
  ]

Also: call with temperature=0 (deterministic, factual — we don't want
creative variation in a rules answer).
```

---

## Implementation Notes

*After Implementing and testing, Everything looks as expected*

**Test query and response:**

```
Query: [How many games do we have?]
Response: [[Catan, Monopoly, Risk] We have 3 games.]
Correctly grounded? [yes]
Cited the right game? [yes]

Query: [Is the Abdoul Game the easiest ?]
Response: [I couldn't find that in the loaded rule books.]
Correctly grounded? [Yes]
```

**One thing you changed from your original spec after seeing the actual output:**

```
[I didn't have to make any change]
```
