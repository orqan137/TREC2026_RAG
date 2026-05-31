# Project Structure

## 1. 구조 원칙

TREC2026 작업공간은 TREC 2025 RAG track의 실험 흐름을 기준으로 단계별 분리를
적용한다. 기준 흐름은 retrieval, reranking, evidence selection, generation,
validation, submission이다.

## 2. 디렉터리 정의

```text
.
|-- configs/
|   |-- retrieval/
|   |-- reranking/
|   |-- generation/
|   `-- experiments/
|-- data/
|   |-- topics/
|   |-- corpus/
|   |-- baselines/
|   |-- qrels/
|   |-- nuggets/
|   `-- cache/
|-- docs/
|-- experiments/
|   |-- retrieval/
|   |-- reranking/
|   |-- evidence_selection/
|   |-- generation/
|   |-- rag_end_to_end/
|   `-- relevance_judgment/
|-- outputs/
|   |-- runs/
|   |-- submissions/
|   |-- metrics/
|   |-- reports/
|   `-- logs/
|-- scripts/
|-- src/
|-- tests/
`-- trec_rag_skills/
```

## 3. 단계별 책임

| 단계 | 입력 | 출력 | 저장 위치 |
| --- | --- | --- | --- |
| Topic preparation | official/sample topic JSONL | normalized topic files | `data/topics` |
| Retrieval | topics, corpus/API | TREC runfile, raw search cache | `outputs/runs`, `data/cache` |
| Reranking | candidate runs/cache | reranked runfile | `outputs/runs` |
| Evidence selection | retrieved documents | evidence packets | `data/cache`, `outputs/reports` |
| Generation | evidence packets | RAG JSONL | `outputs/submissions` |
| Validation | runfile/RAG JSONL | logs, metrics | `outputs/logs`, `outputs/metrics` |
| Reporting | metrics, run notes | analysis reports | `outputs/reports`, `docs` |

## 4. Git 추적 기준

설정, 문서, 샘플 입력, 코드, skill snapshot은 추적 대상이다. official corpus, qrels,
retrieval cache, run outputs, submission files, API response dump, local secrets는
추적 대상에서 제외한다.
