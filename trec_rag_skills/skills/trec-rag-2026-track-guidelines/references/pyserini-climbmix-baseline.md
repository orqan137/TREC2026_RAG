# Pyserini ClimbMix Baseline

Use this reference when building a baseline retrieval system or when no custom retriever is provided. For baseline `RAG` runs, Pyserini/ClimbMix BM25 provides the candidate evidence pool; it is not the final answer generator. Unless an explicit non-agent answer generator is named, the agent prepares the final `RAG` answer by reading evidence and writing the cited answer sentences.

## Companion Skill

For retrieval implementation details beyond the task-level contract in this skill, use the `search-pyserini-rest` skill from:

```text
https://github.com/TREC-RAG/trec-rag-skills/tree/main/skills/search-pyserini-rest
```

Read or invoke `search-pyserini-rest` when you need:

- Token setup or safe local authentication workflow.
- Current service location, OpenAPI docs, health checks, or endpoint discovery.
- ClimbMix search or document-fetch command examples.
- Response parsing, `parse` behavior, query semantics, or error handling.

## Dataset Mapping

```text
ClimbMix -> climbmix-400b
```

## Endpoints

Search endpoint:

```text
GET /v1/climbmix-400b/search?query=...&hits=100
```

Document fetch endpoint:

```text
GET /v1/climbmix-400b/doc/{docid}
```

Expected search response shape:

```json
{
  "api": "v1",
  "index": "climbmix-400b",
  "query": {"text": "Albert Einstein"},
  "candidates": [
    {
      "docid": "shard_00459_61697",
      "score": 12.483799934387207,
      "rank": 1,
      "doc": "..."
    }
  ]
}
```

## Operational Rules

- Use ordinary natural-language or keyword queries.
- Do not rely on Lucene fielded, Boolean, required, or prohibited query syntax.
- Omit the `parse` parameter unless raw stored payloads are explicitly requested.
- Never put Pyserini tokens in generated code, tracked files, command lines, logs, examples, or chat.

## Baseline RAG Generator

For the default `RAG` baseline, the top 100 Pyserini/ClimbMix BM25 results are candidate evidence. Participants and custom systems may choose a different retrieval depth. Unless a custom generator is specified, the agent using this skill is the answer generator. Treat the agent as an evidence-grounded research reporter: it reads the retrieved source packet, identifies the documents that support an answer, and writes a concise cited synthesis from that evidence.

- Review the retrieved candidate documents.
- Reason over the evidence as a source packet, looking for corroboration, disagreement, missing context, and limits in coverage.
- Select only the ClimbMix documents that directly support final answer sentences.
- Put only cited document IDs in `references`.
- Manually write sentence-level answers grounded only in the selected documents.
- Use zero-indexed citation positions into `references`.

Default baseline answer-writing rules:

- Use only retrieved ClimbMix documents as evidence.
- Do not use intrinsic, parametric, or memory-based knowledge to add facts.
- Keep every substantive claim tightly supported by cited documents.
- Prefer careful synthesis over extractive copying, but do not introduce facts that are not supported by the retrieved evidence.
- If support is partial, write only the supported claim rather than filling the gap.
- If the retrieved evidence is insufficient, say so in the answer rather than guessing.
- Do not include diagnostic fields, search traces, rewritten queries, or raw snippets in the submitted `RAG` object unless official instructions require them.
- Write the answer as sentence-level JSON objects; do not embed bracketed citations inside `answer[].text`.

Use `metadata.type: "manual"` when an agent interactively reads evidence and composes the answer. This remains true even if a script later packages the agent-written answer into JSONL, validates citations, or copies fields into the output schema.

Use `metadata.type: "automatic"` only when a specified generator produces the answer text without manual per-topic composition by the agent. A deterministic template, heuristic extractor, or script-authored answer should not be treated as the default baseline RAG generator unless the run explicitly declares that generator as a custom system.

When building the default baseline, keep the division of labor explicit:

- Retrieval automation may write `r_output_trec_rag_2026.tsv`.
- Scripts may retrieve, cache, rank, display, package, and validate evidence.
- The final `answer[].text` values are written by the agent after reviewing the evidence.
- The resulting `rag_output_trec_rag_2026.jsonl` uses `metadata.type: "manual"`.

## Baseline Steps

1. Load `trec_rag_2026_queries.jsonl`.
2. For each topic, use `title` as the default initial ClimbMix query, and use `narrative` as the full information need for query rewriting, decomposition, evidence selection, and answer generation.
3. For the default baseline, retrieve `hits=100` from `climbmix-400b`; custom systems may use a different depth.
4. For `R`, write `r_output_trec_rag_2026.tsv` directly from returned `docid`, `rank`, and `score`.
5. For default baseline `RAG`, have the agent review the retrieved documents, select the cited evidence subset, manually compose cited sentence-level answers, and write or package `rag_output_trec_rag_2026.jsonl` with `metadata.type: "manual"`.
6. If a custom non-agent generator is used instead, document it in the run configuration or prompt, have it generate the cited sentence-level answers, and use `metadata.type: "automatic"`.
7. Validate all outputs before returning or submitting them.
