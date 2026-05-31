# TREC 2025 RAG Track Experiment Analysis

## 1. 분석 목적

본 문서는 TREC RAG 2025 공개 지침, baseline 공지, TREC Browser proceedings를
기반으로 TREC2026 작업공간의 실험 폴더 구조를 정렬하기 위한 기준 문서이다. 2025
task는 MS MARCO V2.1 segment collection을 기준으로 운영되었고, 2026 작업공간은
ClimbMix 기반으로 전환되었으나 실험 단계의 분리는 동일하게 적용 가능하다.

## 2. 2025 공식 task 구조

TREC RAG 2025는 세 개의 주요 task를 운영했다.

| Task | 목적 | 산출물 |
| --- | --- | --- |
| Retrieval (`R`) | topic별 관련 MS MARCO V2.1 segment ranking | TREC runfile |
| Augmented Generation (`AG`) | organizer baseline top-k segments 기반 answer generation | cited answer JSONL |
| Retrieval-Augmented Generation (`RAG`) | participant retrieval + generation + attribution | cited answer JSONL |

2025 Retrieval 제출은 topic당 top 100 segment를 포함하는 TREC runfile을 요구했다.
AG/RAG 제출은 최대 400 words 수준의 answer를 sentence 단위로 분리하고, MS MARCO
V2.1 segment citation을 포함하는 구조를 요구했다.

2026 적용점:

- `AG` 단독 task는 2026 기준에서 제거되었으나, evidence selection 및 generation
  실험 구조는 RAG pipeline 내부 단계로 유지한다.
- 2025의 MS MARCO segment id mapping 요구는 2026에서 ClimbMix document id citation
  관리로 대체한다.
- task별 산출물을 한 디렉터리에 혼합하지 않고 `retrieval`, `generation`,
  `rag_end_to_end` 단위로 분리한다.

## 3. 2025 baseline 및 validator에서 도출한 구조

2025 baseline 공지는 retrieval -> rerank 및 retrieval -> rerank -> generate baseline
흐름과 AG/RAG validator 사용을 강조했다. 이 구조는 다음 파일 계층을 요구한다.

| 단계 | 필요한 저장 영역 |
| --- | --- |
| Retrieval input | `data/topics`, `data/corpus` |
| Baseline run input | `data/baselines` |
| Candidate cache | `data/cache` |
| Reranking config | `configs/reranking` |
| Generation config | `configs/generation` |
| Validation output | `outputs/logs`, `outputs/metrics` |
| Submission package | `outputs/submissions` |

## 4. 2025 참가 시스템의 반복 패턴

공개 proceedings에서 반복적으로 관찰되는 실험 패턴은 다음과 같다.

| 패턴 | 2025 사례 | 2026 구조 반영 |
| --- | --- | --- |
| Sparse + dense hybrid retrieval | UTokyo-HitU, CFDA | `experiments/retrieval`, `configs/retrieval` |
| Reciprocal Rank Fusion | CFDA, Keystone-Docs RAG | `experiments/retrieval`, `outputs/runs` |
| Query decomposition | MITLL, LAS, Keystone-Docs RAG | `experiments/retrieval`, `experiments/rag_end_to_end` |
| Learned sparse retrieval | MITLL, LAS | `configs/retrieval` |
| LLM/listwise/pointwise reranking | MITLL, IIUoT, UTokyo-HitU | `experiments/reranking` |
| HyDE/query augmentation | UTokyo-HitU | `experiments/retrieval` |
| Nugget extraction/clustering | GenAIus, LAS, HLTCOE | `experiments/evidence_selection` |
| Few-document evidence packaging | Keystone-Docs RAG | `experiments/evidence_selection` |
| Claim-citation alignment | IIUoT | `experiments/generation` |
| Agentic iterative retrieval | GRILL Lab, LAS | `experiments/rag_end_to_end` |
| Relevance judgment experiments | GenAIus, DUTH | `experiments/relevance_judgment` |

## 5. 2026 적용 구조

2026 작업공간은 다음 원칙을 적용한다.

1. `data`는 외부 입력과 캐시를 보관한다.
2. `configs`는 재현 가능한 실험 parameter를 보관한다.
3. `experiments`는 실험 family별 protocol, ablation, notes를 보관한다.
4. `src`는 공통 실행 코드만 보관한다.
5. `outputs`는 생성 산출물을 보관하되 Git 추적에서 제외한다.
6. `docs`는 대회 기준, 실험 분석, 구조 결정 근거를 보관한다.

## 6. 주요 출처

- TREC RAG 2025 overview: https://trec-rag.github.io/trec25/
- TREC RAG 2025 track guidelines: https://trec-rag.github.io/annoucements/2025-track-guidelines/
- TREC RAG 2025 baselines and validator: https://trec-rag.github.io/annoucements/2025-baselines/
- TREC Browser 2025 RAG data: https://pages.nist.gov/trec-browser/trec34/rag/data/
- TREC Browser 2025 RAG proceedings: https://pages.nist.gov/trec-browser/trec34/rag/proceedings/
- Overview paper: https://arxiv.org/abs/2603.09891
