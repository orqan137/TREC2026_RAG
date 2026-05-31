# Retrieval-Augmented Generation Task (`RAG`)

Use this reference when building, explaining, or validating the TREC RAG 2026 Retrieval-Augmented Generation task.

## Task Summary

- **Given**: a list of topics and access to ClimbMix retrieval results and document contents.
- **Task**: retrieve relevant evidence and return a summarized answer grounded in that evidence.
- **Notes**: this task best matches an industrial RAG setup that combines retrieval, evidence selection, and generation. The answer should be evaluated as both an answer and a grounded, cited use of retrieved material.

Unlike the removed `AG` task, the 2026 `RAG` task does not assume a fixed provided evidence set. The system is responsible for retrieval. Use the Pyserini REST baseline retriever when focusing on answer generation.

For the Pyserini/ClimbMix baseline, retrieved BM25 results are the candidate evidence pool. Unless a custom generator is specified, the agent using this skill selects the cited evidence subset from those candidates and generates the final sentence-level answer.

## Input Format: Topics

Use the same `trec_rag_2026_queries.jsonl` topic file as the Retrieval task. Preserve `id`, `title`, and `narrative` exactly in RAG metadata.

## Input Format: Documents

Use ClimbMix documents returned by retrieval as the evidence source. A RAG system may:

- Use the `doc` contents returned directly in search results.
- Fetch full document contents with `GET /v1/climbmix-400b/doc/{docid}`.
- Apply its own chunking or passage selection internally.

If a system chunks documents internally, still keep final `references` tied to ClimbMix document IDs unless official 2026 instructions require a different mapping.

## Input Format: Ranked Results

If using a retrieval run as input to generation, use the same six-column format as `r_output_trec_rag_2026.tsv`:

```text
topic_id Q0 docid rank score run_id
```

The ranked `docid` values are the candidate evidence pool for `RAG` output. The final RAG `references` list should include only the ClimbMix documents cited by at least one answer sentence.

Do not copy all top-ranked results into `references` by default. Include only documents that directly support at least one generated answer sentence.

## Output Format: RAG Output

For official submissions, provide JSONL in `rag_output_trec_rag_2026.jsonl`, with one JSON object per topic.

```json
{
  "metadata": {
    "team_id": "my-team",
    "run_id": "my-rag-run",
    "type": "automatic",
    "narrative_id": "1",
    "title": "Industrial Revolution causes and effects",
    "narrative": "I'm trying to understand how the Industrial Revolution began, what caused it, and how it changed societies, economies, and populations in different countries. I'm also interested in the roles of key figures like Henry Ford, the impact of technological advancements, and how industrialization connects to topics like urbanization, migration, and modern innovations such as robotics and extended reality.",
    "prompt": "Optional prompt used to generate the answer."
  },
  "references": [
    "shard_00459_61697",
    "shard_01012_88420",
    "shard_00210_44018"
  ],
  "answer": [
    {
      "text": "Industrialization began through a combination of technological innovation, changing labor patterns, and expanding markets.",
      "citations": [0, 1]
    },
    {
      "text": "Its effects included urbanization, factory labor systems, and major changes in economic organization.",
      "citations": [1, 2]
    }
  ]
}
```

Required fields:

- `metadata.team_id`: team identifier.
- `metadata.run_id`: run identifier.
- `metadata.type`: `automatic` or `manual`.
- `metadata.narrative_id`: topic ID from `trec_rag_2026_queries.jsonl`.
- `metadata.title`: original short topic title from `trec_rag_2026_queries.jsonl`.
- `metadata.narrative`: original long-form topic narrative from `trec_rag_2026_queries.jsonl`.
- `metadata.prompt`: optional prompt used for response generation.
- `references`: ordered list of retrieved ClimbMix document IDs cited by the answer. Do not include uncited documents.
- `answer`: array of sentence-level answer objects.
- `answer[].text`: answer sentence.
- `answer[].citations`: zero-indexed positions into `references`.

Run type guidance:

- Use `metadata.type: "manual"` when a person or agent reads retrieved evidence and composes the answer topic by topic.
- Use `metadata.type: "automatic"` when a declared system or generator produces the answer text without per-topic human or agent composition.
- The distinction describes how the answer text was produced, not whether scripts were used for retrieval, packaging, validation, or JSONL formatting.

## Answer Rules

- Break the final answer into individual sentences.
- Ground each sentence in retrieved evidence.
- Every citation must be an integer index into `references`.
- Do not cite documents that are missing from `references`.
- Every document in `references` should be cited by at least one answer sentence.
- Sort citation indices by support strength when the system can estimate support.
- Avoid unsupported claims, even if the model knows them from prior knowledge.

## Validation Rules

- `rag_output_trec_rag_2026.jsonl` must be valid JSONL, with one complete object per line.
- Every input topic must have exactly one RAG object unless a subset was explicitly requested.
- Every RAG object must have `metadata`, `references`, and `answer`.
- Every RAG citation must be a valid zero-indexed reference position.
- Every RAG reference must be cited by at least one answer sentence.
- Answer claims must be supported by cited references.
