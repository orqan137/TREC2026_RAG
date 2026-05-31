# TREC2026 RAG Retrieval Pipeline

이 저장소는 TREC RAG 2026 트랙 준비를 위한 작업 공간이다. 현재 구현 범위는
ClimbMix/Pyserini REST API를 사용하는 Retrieval baseline이며, 이후 RAG 생성
단계를 붙일 수 있도록 입력, 출력, 캐시, 검증 구조를 분리했다.

작성 기준일은 2026-05-31이며, 세부 규칙은 로컬에 보관한
`trec-rag-skills` 스냅샷을 기준으로 정리했다. 최종 제출 전에는 공식 TREC RAG
사이트의 최신 제출 일정, 업로드 절차, 포털 요구사항을 다시 확인해야 한다.

## 1. 프로젝트 목표

본 프로젝트의 목표는 TREC RAG 2026의 Retrieval task와 RAG task에 대응하는
재현 가능한 검색 파이프라인을 구축하는 것이다. 1차 구현은 다음을 수행한다.

- topic JSONL 파일을 읽는다.
- topic title을 기본 검색 query로 사용한다.
- Pyserini REST API를 통해 ClimbMix index에서 top-k 문서를 검색한다.
- TREC Retrieval runfile 형식의 `r_output_trec_rag_2026.tsv`를 생성한다.
- 생성된 runfile의 열 개수, topic coverage, rank, score ordering을 검증한다.

## 2. Skill 정리

로컬 참조 자료는 `trec-rag-skills` 폴더에 있다. 이 폴더는 API token이 들어 있는
로컬 `.env`와 별도 git metadata를 포함하므로 GitHub 업로드 대상에서 제외했다.

### `trec-rag-intro`

TREC RAG 2026의 개요를 설명하는 skill이다. 트랙 목표, 공개 상태, 주최자,
참가 안내 같은 고수준 질문에 사용한다. task 규칙, output format, baseline
구축 방법은 이 skill이 아니라 `trec-rag-2026-track-guidelines`를 따른다.

### `trec-rag-2026-track-guidelines`

2026 task 구현과 제출 형식을 정의하는 핵심 skill이다.

- 사용 가능한 task: Retrieval (`R`), Retrieval-Augmented Generation (`RAG`)
- 2026에서 제거된 task: 2025의 Augmented Generation-only (`AG`)
- 기본 corpus/index: ClimbMix, `climbmix-400b`
- topic input: `trec_rag_2026_queries.jsonl`
- Retrieval output: `r_output_trec_rag_2026.tsv`
- RAG output: `rag_output_trec_rag_2026.jsonl`
- baseline retrieval depth: topic당 top 100

Retrieval 제출 형식은 표준 TREC runfile이다.

```text
topic_id Q0 docid rank score run_id
```

RAG 제출 형식은 JSONL이며, topic마다 하나의 JSON object를 둔다. 핵심 필드는
`metadata`, `references`, `answer`이다. `references`에는 실제 answer sentence가
인용한 ClimbMix document id만 넣고, `answer[].citations`는 `references`에 대한
0-based index를 사용한다.

### `pyserini-rest-api`

Pyserini REST API 접근 방법을 정의하는 skill이다. 현재 service endpoint는 다음과
같다.

```text
http://99.251.12.72:8081
```

index mapping은 다음과 같다.

| Dataset | Index |
| --- | --- |
| ClimbMix | `climbmix-400b` |
| FineWeb-Edu | `fineweb-edu-100b-karpathy` |
| MS MARCO V2.1 Segmented Doc | `msmarco-v2.1-doc-segmented` |

주요 endpoint는 다음 두 개다.

```text
GET /v1/{index}/search?query=...&hits=...
GET /v1/{index}/doc/{docid}
```

query는 Lucene field syntax나 Boolean operator에 의존하지 않고 일반 자연어 또는
keyword text로 보낸다.

## 3. 보안 관리

GitHub에 올라가면 안 되는 항목은 `.gitignore`로 제외했다.

- `.env`, `.env.*`
- `.curlrc.pyserini-rest`
- `.venv/`
- `tmp/`
- `data/cache/`
- `outputs/*.tsv`, `outputs/*.jsonl`, `outputs/*.json`
- `trec-rag-skills/`
- Python bytecode/cache

토큰은 코드, README, command line 예시, log, output 파일에 기록하지 않는다.
현재 파이프라인은 다음 순서로 local env file을 읽고, token 값은 출력하지 않는다.

1. `.env.local`
2. `.env`
3. `trec-rag-skills/.env.local`
4. `trec-rag-skills/.env`

지원하는 token 변수명은 `PYSERINI_API_TOKEN`과 `PYSERINI_TOKEN`이다. GitHub에
공개할 값은 `.env.example`에 빈 placeholder로만 둔다.

## 4. 저장소 구조

```text
.
|-- configs/
|   `-- search_pipeline.json
|-- data/
|   `-- sample_trec_rag_2026_queries.jsonl
|-- outputs/
|-- scripts/
|   `-- trec_search.py
|-- src/
|   `-- trec2026/
|       |-- __init__.py
|       `-- search_pipeline.py
|-- .env.example
|-- .gitignore
`-- README.md
```

## 5. 실행 방법

Python 가상환경을 만든다.

```powershell
python -m venv .venv
```

현재 검색 파이프라인은 Python 표준 라이브러리만 사용하므로 별도 runtime package
설치가 필요 없다.

CLI 연결을 확인한다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py --help
```

API health check를 실행한다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py health
```

단일 query 검색을 실행한다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py search "Albert Einstein" --hits 5
```

공식 topic 파일을 프로젝트 루트에 `trec_rag_2026_queries.jsonl`로 둔 뒤 Retrieval
runfile을 생성한다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py run
```

생성된 runfile을 검증한다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py validate-run
```

공식 topic 파일이 없을 때는 sample topic으로 smoke test를 수행할 수 있다.

```powershell
.\.venv\Scripts\python.exe scripts\trec_search.py run --topics data\sample_trec_rag_2026_queries.jsonl --out outputs\sample_r_output_trec_rag_2026.tsv --hits 3 --run-id smoke-test
.\.venv\Scripts\python.exe scripts\trec_search.py validate-run --topics data\sample_trec_rag_2026_queries.jsonl --runfile outputs\sample_r_output_trec_rag_2026.tsv
```

## 6. 현재 검증 결과

초기 구축 시 다음 검증을 완료했다.

- Python compile check 통과
- Pyserini REST root endpoint 접근 성공
- `climbmix-400b` authenticated search 성공
- `Albert Einstein` health query에서 document body 포함 candidate 반환 확인
- sample topic 2개 기준 Retrieval runfile 6 rows 생성
- sample runfile validator 결과: `valid: true`

## 7. 향후 작업

다음 단계는 RAG output 생성을 위한 evidence selection과 sentence-level citation
packaging이다.

- top 100 retrieval cache를 topic별 evidence packet으로 정리
- document text normalization 및 passage selection 추가
- RAG answer schema validator 구현
- `rag_output_trec_rag_2026.jsonl` 생성 CLI 추가
- official topic file 수령 후 full run 생성 및 검증
