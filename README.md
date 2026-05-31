# TREC2026 RAG Retrieval Pipeline

## 1. 문서 개요

본 저장소는 TREC RAG 2026 트랙 대응을 위한 Retrieval 및 RAG 시스템 구축
작업공간이다. 현 단계의 구현 범위는 ClimbMix 기반 Pyserini REST Retrieval
baseline이며, RAG 생성 단계 확장을 고려한 입력, 출력, 캐시, 검증 구조를 포함한다.

기준 문서는 `trec_rag_skills/skills` 하위의 skill 및 reference 문서이다. 해당
자료는 2026-05-31 현재 로컬 작업공간에 반영된 지침을 기준으로 한다. 대회 최종 제출
전 공식 TREC RAG 사이트의 제출 일정, 업로드 절차, 포털 요구사항 확인이 별도로
필요하다.

## 2. 기준 자료 구성

| 구분 | 경로 | 역할 |
| --- | --- | --- |
| Intro skill | `trec_rag_skills/skills/trec-rag-intro` | 트랙 개요, 공개 상태, 참가 안내, 조직 정보 |
| Track guidelines | `trec_rag_skills/skills/trec-rag-2026-track-guidelines` | 2026 task 정의, 제출 형식, baseline, validation 기준 |
| Pyserini REST API | `trec_rag_skills/skills/pyserini-rest-api` | API endpoint, 인증, 검색, 문서 조회, 오류 처리 |
| 2025 experiment analysis | `docs/trec2025_experiment_analysis.md` | TREC 2025 RAG 실험 패턴 및 2026 구조 반영 기준 |
| Project structure | `docs/project_structure.md` | 폴더 책임, 산출물 위치, Git 추적 기준 |
| 구현 코드 | `src/trec2026/search_pipeline.py` | Retrieval 실행, 캐시 저장, runfile 생성, runfile 검증 |
| 실행 wrapper | `scripts/trec_search.py` | CLI 진입점 |
| 기본 설정 | `configs/search_pipeline.json` | index, hits, output path, cache path, run id |

## 3. TREC RAG 2026 트랙 요약

TREC RAG 2026은 retrieval-augmented generation 시스템 평가를 위한 Text REtrieval
Conference 트랙이다. 평가 대상은 대규모 corpus 검색과 LLM 기반 응답 생성을 결합한
end-to-end RAG 시스템이며, retrieval component와 generation component의 분리 분석도
고려한다.

공개 기준 정보는 다음과 같다.

| 항목 | 내용 |
| --- | --- |
| 트랙 상태 | 2026년 트랙 재개 공지 |
| Corpus | release 예정 |
| Test topics | TBD |
| Baselines | TBD |
| Submission deadline | TBD |
| Results and judgments | TBD |
| Conference | TREC 2026, 2026년 11월 |

참가 안내 기준은 NIST/Evalbase 등록, Google Groups 및 Discord 참여, Google Groups
신청 시 `TREC RAG` 명시, Google Groups 문제 발생 시 `njedidi@uwaterloo.ca` 연락이다.

## 4. Skill 지시사항 종합

### 4.1 `trec-rag-intro`

적용 범위는 트랙의 고수준 설명이다. 포함 항목은 목표, 현황, 일정 placeholder,
주최자, 참가 안내이다. task 규칙, 제출 파일 형식, baseline 구현, Pyserini/ClimbMix
세부 설정은 이 skill의 적용 범위가 아니며 `trec-rag-2026-track-guidelines`의 적용
대상이다.

2024년 및 2025년 세부 내용은 본 기준 자료에 포함되지 않는다. 필요 시 공식 과년도
페이지 참조가 기준이다.

### 4.2 `trec-rag-2026-track-guidelines`

2026년 task는 Retrieval (`R`)과 Retrieval-Augmented Generation (`RAG`)이다.
2025년의 Augmented Generation-only (`AG`) task는 2026년 출력 대상에서 제외된다.

기본 운영값은 다음과 같다.

| 항목 | 값 |
| --- | --- |
| Primary corpus | ClimbMix |
| Pyserini REST index | `climbmix-400b` |
| Topic input | `trec_rag_2026_queries.jsonl` |
| Retrieval output | `r_output_trec_rag_2026.tsv` |
| RAG output | `rag_output_trec_rag_2026.jsonl` |
| Baseline retrieval depth | topic당 top 100 |
| Baseline retrieval query | topic `title` |
| Full information need | topic `narrative` |

topic record의 필수 필드는 `id`, `title`, `narrative`이다. 모든 출력에서 topic id는
원문 그대로 유지한다.

### 4.3 `pyserini-rest-api`

Pyserini REST API는 TREC RAG tracks용 공식 API로 정의되어 있다. 현재 기준 endpoint는
다음과 같다.

```text
http://99.251.12.72:8081
```

dataset-index mapping은 다음과 같다.

| Dataset | Index |
| --- | --- |
| ClimbMix | `climbmix-400b` |
| FineWeb-Edu | `fineweb-edu-100b-karpathy` |
| MS MARCO V2.1 Segmented Doc | `msmarco-v2.1-doc-segmented` |

주요 endpoint는 다음과 같다.

```text
GET /v1/{index}/search?query=...&hits=...
GET /v1/{index}/doc/{docid}
```

검색 query는 Lucene query syntax가 아닌 analyzed text로 취급한다. fielded syntax,
Boolean operator, required/prohibited term syntax 의존은 기준에서 제외된다. 기본
요청에서는 `parse` parameter를 생략한다.

## 5. Retrieval Task 기준

Retrieval task의 입력은 `trec_rag_2026_queries.jsonl`이다. 각 topic의 `title`을
기본 검색 query로 사용하고, `narrative`는 query rewriting, decomposition, evidence
selection, generation 판단에 활용되는 full information need로 취급한다.

Retrieval 제출 파일은 standard TREC runfile 형식이다.

```text
topic_id Q0 docid rank score run_id
```

검증 기준은 다음과 같다.

| 항목 | 기준 |
| --- | --- |
| 열 개수 | line당 whitespace-separated 6 columns |
| topic coverage | 명시된 subset이 없는 경우 모든 input topic 포함 |
| rank | topic별 1부터 시작, ascending order |
| score | topic 내부 non-increasing order |
| docid | ClimbMix retriever 또는 custom index에서 반환된 document id |
| Q0 | 고정 문자열 `Q0` |

제출 row 수는 topic별로 동일할 필요가 없으며, 고정 maximum은 정의되어 있지 않다.
baseline은 topic당 top 100 검색 결과를 사용한다.

## 6. RAG Task 기준

RAG task는 검색된 ClimbMix 문서를 evidence source로 사용하여 grounded answer를
생성하는 task이다. 2026년 RAG task는 fixed evidence set을 전제로 하지 않으며,
system이 retrieval을 수행한다.

RAG 제출 파일은 JSONL 형식이며 topic당 하나의 JSON object를 기록한다. 핵심 schema는
다음과 같다.

```json
{
  "metadata": {
    "team_id": "team-id",
    "run_id": "run-id",
    "type": "automatic",
    "narrative_id": "topic-id",
    "title": "original title",
    "narrative": "original narrative",
    "prompt": "optional prompt"
  },
  "references": ["climbmix-docid"],
  "answer": [
    {
      "text": "Evidence-grounded sentence.",
      "citations": [0]
    }
  ]
}
```

RAG validation 기준은 다음과 같다.

| 항목 | 기준 |
| --- | --- |
| JSONL | line당 complete JSON object |
| topic coverage | input topic당 1 object |
| required fields | `metadata`, `references`, `answer` |
| citation index | `references`에 대한 zero-indexed integer |
| reference usage | 모든 reference는 최소 하나의 sentence에서 citation 필요 |
| grounding | answer claim은 cited reference로 지원 필요 |

`metadata.type`은 answer text 작성 방식에 따른다. agent 또는 사람이 topic별 evidence를
검토하고 문장을 작성한 경우 `manual`이다. 선언된 generator가 per-topic manual
composition 없이 answer text를 생성한 경우 `automatic`이다.

## 7. 구현된 Retrieval Pipeline

현재 구현은 Python 표준 라이브러리만 사용한다. 외부 runtime dependency는 없다.

처리 흐름은 다음과 같다.

1. dotenv 후보 파일에서 Pyserini token과 base URL 로드
2. topic JSONL 파싱 및 필수 필드 검증
3. topic `title` 기반 ClimbMix 검색 실행
4. topic별 raw search response를 `data/cache/pyserini`에 저장
5. TREC runfile row 생성
6. output TSV 저장
7. runfile validation 수행

기본 설정값은 `configs/search_pipeline.json`에 정의되어 있다.

```json
{
  "base_url": "http://99.251.12.72:8081",
  "index": "climbmix-400b",
  "default_hits": 100,
  "run_id": "pyserini-climbmix-baseline",
  "topic_file": "data/topics/trec_rag_2026_queries.jsonl",
  "retrieval_output": "outputs/runs/r_output_trec_rag_2026.tsv",
  "cache_dir": "data/cache/pyserini"
}
```

## 8. TREC 2025 실험 분석 기반 구조

TREC RAG 2025 proceedings 및 baseline 공지에서 반복적으로 확인되는 실험 흐름은
retrieval, fusion/reranking, evidence selection, generation, validation이다. 2026
작업공간은 이 흐름을 기준으로 다음 구조를 적용한다.

| 단계 | 디렉터리 | 적용 목적 |
| --- | --- | --- |
| Topic/corpus/qrels 관리 | `data/topics`, `data/corpus`, `data/qrels`, `data/nuggets` | official input과 평가 자료 분리 |
| Organizer baseline 및 candidate cache | `data/baselines`, `data/cache` | baseline run, API response, evidence packet 관리 |
| Retrieval 실험 | `experiments/retrieval`, `configs/retrieval` | BM25, sparse/dense hybrid, HyDE, RRF, query decomposition |
| Reranking 실험 | `experiments/reranking`, `configs/reranking` | LLM/listwise/pointwise reranking, sliding-window reranking |
| Evidence selection | `experiments/evidence_selection` | nugget extraction, clustering, few-document packaging |
| Generation 실험 | `experiments/generation`, `configs/generation` | sentence-level citation, claim-citation alignment |
| End-to-end RAG | `experiments/rag_end_to_end`, `configs/experiments` | retrieval-to-answer ablation 및 통합 실험 |
| 산출물 | `outputs/runs`, `outputs/submissions`, `outputs/metrics`, `outputs/reports`, `outputs/logs` | runfile, JSONL, metric, report, validator log 분리 |

세부 분석 근거는 `docs/trec2025_experiment_analysis.md`에 기록한다.

## 9. 보안 정책

저장소 공개 기준에서 제외되는 항목은 다음과 같다.

| 항목 | 사유 |
| --- | --- |
| `.env`, `.env.*` | API token 및 local secret 포함 가능성 |
| `.curlrc.pyserini-rest` | Authorization header 포함 |
| `.venv/` | local runtime environment |
| `tmp/` | API response 임시 파일 |
| `data/cache/` | retrieved document cache |
| `outputs/*.tsv`, `outputs/*.jsonl`, `outputs/*.json` | run output 및 평가 산출물 |
| `trec-rag-skills/` | local 작업용 clone, token 및 nested git metadata 포함 가능 |
| `trec_rag_skills/.env*` | 공개용 skill snapshot 내부 secret 방지 |
| `trec_rag_skills/.git/` | nested repository metadata 방지 |
| `__pycache__/`, `*.pyc` | Python bytecode |

공개 저장소에는 `.env.example`만 포함한다. 실제 token은 코드, README, command line
example, log, output 파일에 기록하지 않는다.

token 탐색 순서는 다음과 같다.

1. `.env.local`
2. `.env`
3. `trec-rag-skills/.env.local`
4. `trec-rag-skills/.env`
5. `trec_rag_skills/.env.local`
6. `trec_rag_skills/.env`

지원 변수명은 `PYSERINI_API_TOKEN` 및 `PYSERINI_TOKEN`이다.

## 10. 저장소 구조

```text
.
|-- configs/
|   |-- retrieval/
|   |-- reranking/
|   |-- generation/
|   |-- experiments/
|   `-- search_pipeline.json
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
|   `-- trec_search.py
|-- src/
|   `-- trec2026/
|       |-- __init__.py
|       `-- search_pipeline.py
|-- trec_rag_skills/
|   `-- skills/
|-- .env.example
|-- .gitignore
`-- README.md
```

## 11. 실행 절차

가상환경 생성:

```powershell
python -m venv .venv
```

CLI 확인:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py --help
```

API health check:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py health
```

단일 query 검색:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py search "Albert Einstein" --hits 5
```

official topic file 기준 Retrieval runfile 생성:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py run
```

Retrieval runfile 검증:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py validate-run
```

sample topic 기준 smoke test:

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py run --topics data\topics\sample_trec_rag_2026_queries.jsonl --out outputs\runs\sample_r_output_trec_rag_2026.tsv --hits 3 --run-id smoke-test
.\.venv\Scripts\python.exe scripts\trec_search.py validate-run --topics data\topics\sample_trec_rag_2026_queries.jsonl --runfile outputs\runs\sample_r_output_trec_rag_2026.tsv
```

## 12. 초기 검증 결과

| 검증 항목 | 결과 |
| --- | --- |
| Python compile check | 통과 |
| Pyserini REST root endpoint | 접근 성공 |
| `climbmix-400b` authenticated search | 성공 |
| health query | `Albert Einstein` 기준 candidate 반환 |
| document payload | 첫 candidate에 document body 포함 |
| sample runfile generation | 2 topics, 6 rows |
| sample runfile validation | `valid: true` |

## 13. 후속 개발 항목

| 우선순위 | 항목 |
| --- | --- |
| 1 | official `trec_rag_2026_queries.jsonl` 수령 후 full Retrieval run 생성 |
| 2 | topic별 top 100 evidence packet 정규화 |
| 3 | document text normalization 및 passage selection |
| 4 | RAG answer schema validator 구현 |
| 5 | `rag_output_trec_rag_2026.jsonl` 생성 CLI 구현 |
| 6 | submission logistics 공식 업데이트 반영 |
