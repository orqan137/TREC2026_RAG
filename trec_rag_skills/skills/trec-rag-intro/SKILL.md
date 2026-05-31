---
name: trec-rag-intro
description: Introductory and practical 2026-only reference for discussing the TREC Retrieval-Augmented Generation (RAG) track. Use when a user wants to understand TREC RAG 2026 goals, current public status, timeline placeholders, organizers, participation guidance, or high-level differences from prior years. For task rules, system-building guidance, baselines, output formats, ClimbMix/Pyserini details, or validation, use trec-rag-2026-track-guidelines instead.
metadata:
  version: v0.2.0
---

# TREC RAG Intro

## Use This Skill

Use this skill to answer conversational questions about the TREC RAG 2026 track and orient new participants using only the current 2026 information in `references/trec-rag.md`.

Start with the concise answer the user asked for. Load `references/trec-rag.md` when the user asks for 2026 facts, current status, dates, organizers, participation guidance, or source links.

If the user asks for 2026 guidelines, task rules, output formats, baselines, validation, ClimbMix retrieval, Pyserini REST details, or how to build a TREC RAG 2026 system, use `trec-rag-2026-track-guidelines` instead of answering from this intro skill. Make clear that the 2026 task guidelines are available in that skill; only public logistics such as final deadlines, upload procedures, and portal-specific submission details remain subject to official-site updates.

## Conversation Guidance

- Answer only with 2026 information from the current TREC RAG home page unless the user explicitly provides newer source material.
- Do not say the 2026 task guidelines are pending; route guideline questions to `trec-rag-2026-track-guidelines`.
- Treat public submission logistics, deadlines, upload procedures, and portal-specific requirements as pending unless verified from the official site.
- If the user asks about TREC RAG 2025 or TREC RAG 2024, do not summarize those years from this skill. Refer them to:
  - 2025: https://trec-rag.github.io/trec25/
  - 2024: https://trec-rag.github.io/trec24/
- Exception: if the user asks about task-level differences between 2025 and 2026, route to `trec-rag-2026-track-guidelines`; for prior-year details, point them to the 2025 page.
- If the user needs operationally current participation instructions, browse `https://trec-rag.github.io/` before answering because registration, timelines, and guidelines can change.

## Reference

Read `references/trec-rag.md` for the summarized 2026 track facts and links.
