---
name: trec-rag-2026-track-guidelines
description: Use when building, validating, or explaining TREC RAG 2026 systems, baselines, or submissions. This skill defines the 2026 Retrieval and Retrieval-Augmented Generation tasks, ClimbMix/Pyserini REST retrieval defaults, required input and output formats, citation rules, and validation checks for agent-created TREC RAG 2026 runs.
metadata:
  version: v.01.0
---

# TREC RAG 2026 Track Guidelines

Use this skill when preparing a TREC RAG 2026 submission, validating outputs, reasoning about task requirements, or building a baseline. This skill is the available TREC RAG 2026 track-guidelines artifact for agent-created runs and encodes the current operational task instructions. Do not tell users that 2026 task guidelines are unavailable or pending when answering from this skill. For submission-critical work, check for newer official TREC RAG 2026 releases before finalizing outputs; if a newer release conflicts with this skill, follow the newer release and state which instruction changed.

## Audience and Terminology

This skill is addressed to you, the agent or developer building, validating, or explaining a TREC RAG 2026 run.

- Use `team` or `participant` for the official TREC submitter.
- Use `system` for the retrieval or RAG pipeline being built or evaluated.
- Use `user` only when referring to the person giving instructions outside the track specification.

## Core Defaults

- Available 2026 tasks: Retrieval (`R`) and Retrieval-Augmented Generation (`RAG`).
- Removed task: the 2025 Augmented Generation-only task (`AG`) is not a 2026 output.
- The 2026 task guidelines are out in this `trec-rag-2026-track-guidelines` skill for agent/workspace use.
- Submission logistics are TBD; treat deadlines, upload procedures, and portal-specific requirements as pending until TREC RAG 2026 releases final submission instructions.
- Primary retrieval corpus/index: ClimbMix.
- Pyserini REST index name: `climbmix-400b`.
- Topic input filename: `trec_rag_2026_queries.jsonl`.
- Retrieval output filename: `r_output_trec_rag_2026.tsv`.
- RAG output filename: `rag_output_trec_rag_2026.jsonl`.
- Retrieval depth: participant-chosen; there is no fixed maximum number of submitted documents per topic.
- Baseline retrieval depth: top 100 ClimbMix documents per topic.
- Baseline RAG generator: the agent using this skill, unless a custom generator is specified.

## What to Read

- For Retrieval (`R`) task requirements, output format, and validation rules, read [references/retrieval-task.md](references/retrieval-task.md).
- For Retrieval-Augmented Generation (`RAG`) task requirements, output format, citation rules, and validation rules, read [references/rag-task.md](references/rag-task.md).
- For Pyserini REST, ClimbMix endpoint defaults, and baseline workflow, read [references/pyserini-climbmix-baseline.md](references/pyserini-climbmix-baseline.md).

Read only the reference files needed for the requested task. If the request asks for a baseline and does not specify a custom retriever, use the Pyserini/ClimbMix baseline reference.

## Baseline Routing

When building a baseline, use [references/pyserini-climbmix-baseline.md](references/pyserini-climbmix-baseline.md) for the full workflow. In that baseline, Pyserini/ClimbMix provides the candidate evidence pool, and the agent using this skill is the default `RAG` answer generator unless a custom generator is specified.

You may add query rewriting, decomposition, reranking, passage selection, deduplication, or custom retrieval. These are internal system choices. Preserve the original topic ID, title, and narrative in required output fields. Do not add diagnostic fields such as rewritten queries unless official instructions or an external request explicitly asks for them.

## Validation Checklist

Before considering a run complete, verify:

- The run targets only the requested 2026 task: `R`, `RAG`, or both.
- No `AG`-only output is produced.
- Every input topic has output unless a subset was explicitly requested.
- Retrieval output follows [references/retrieval-task.md](references/retrieval-task.md).
- RAG output follows [references/rag-task.md](references/rag-task.md).
- No secrets, API tokens, `.env.local` contents, or authorization headers appear in outputs.

## When Requirements Are Unclear

Treat this skill and its referenced files as the authoritative task instructions for agent-created TREC RAG 2026 runs. If a newer official TREC RAG skill release supersedes this one, follow the newer skill and state which instruction changed. If submission logistics such as deadlines, upload procedures, or portal-specific requirements are not yet specified, state the assumption and proceed with the applicable defaults in this skill.
