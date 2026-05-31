# Retrieval Task (`R`)

Use this reference when building, explaining, or validating the TREC RAG 2026 Retrieval task.

## Task Summary

- **Given**: a list of topics and access to the ClimbMix collection through the Pyserini REST API or a custom retrieval system.
- **Task**: return a ranked list of relevant ClimbMix document IDs for each topic. Participants may choose how many documents to return per topic.
- **Notes**: this task is the 2026 counterpart of the 2025 Retrieval task, but uses ClimbMix as the primary retrieval collection instead of the MS MARCO V2.1 segmented collection.

## Input Format: Topics

Topics are provided as JSONL in `trec_rag_2026_queries.jsonl`. Each line contains a topic ID, a short keyword-style title, and a longer narrative-style topic description.

```jsonl
{"id":"1","title":"Industrial Revolution causes and effects","narrative":"I'm trying to understand how the Industrial Revolution began, what caused it, and how it changed societies, economies, and populations in different countries. I'm also interested in the roles of key figures like Henry Ford, the impact of technological advancements, and how industrialization connects to topics like urbanization, migration, and modern innovations such as robotics and extended reality."}
{"id":"2","title":"Prisons inmate rights rehabilitation incarceration","narrative":"I'm trying to understand how prisons operate, including issues like inmate rights, rehabilitation, voting, and the impact of race and profit motives on incarceration. Can you explain how correctional facilities address mental health, discipline, and recidivism, and also discuss the ethical and legal challenges inmates face?"}
```

Required fields:

- `id`: topic identifier. Preserve this exactly in all outputs.
- `title`: short topic title, usually a few keywords. Preserve this exactly in outputs that include topic metadata. Use it as the default initial retrieval query unless the system intentionally performs query rewriting or decomposition internally.
- `narrative`: long-form topic description. Preserve this exactly in outputs that include topic metadata. Use it to understand the full information need and to guide query rewriting, decomposition, evidence selection, and generation.

## Input Format: ClimbMix Documents

For baseline systems, retrieve ClimbMix documents from the Pyserini REST API. The configured index name is:

```text
climbmix-400b
```

Search returns candidate objects with at least:

- `docid`: ClimbMix document ID to use in submissions.
- `rank`: returned rank.
- `score`: retrieval score.
- `doc`: parsed or stored document contents when available.

ClimbMix documents commonly expose document text through the returned `doc` payload. When a system needs full document contents for generation, fetch by `docid` through the document endpoint.

## Output Format: Ranked Results

For official submissions, provide a standard TREC runfile in `r_output_trec_rag_2026.tsv`. Each line contains six whitespace-separated fields:

```text
topic_id Q0 docid rank score run_id
```

Example:

```text
1 Q0 shard_00459_61697 1 12.4838 my-run
1 Q0 shard_01012_88420 2 11.9721 my-run
1 Q0 shard_00210_44018 3 10.5542 my-run
2 Q0 shard_00044_91812 1 10.8114 my-run
```

Field rules:

- `topic_id`: topic identifier from `trec_rag_2026_queries.jsonl`.
- `Q0`: fixed string.
- `docid`: ClimbMix document ID.
- `rank`: rank of the retrieved document for that topic, starting at 1.
- `score`: numeric score used to rank documents.
- `run_id`: stable identifier for the submitted run.

## Validation Rules

- There is no fixed maximum number of rows per topic; participants may return as many ranked documents as they choose.
- Rows per topic may vary across topics.
- Sort each topic's rows by rank ascending.
- Keep scores non-increasing within each topic.
- `r_output_trec_rag_2026.tsv` must have exactly six whitespace-separated columns per line.
- Retrieval ranks must restart at 1 for each topic.
- Every Retrieval `docid` must be a ClimbMix document ID returned by the retriever or custom index.
- Do not emit MS MARCO segment IDs unless official 2026 instructions explicitly require a mapping step.
