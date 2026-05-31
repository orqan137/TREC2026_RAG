# Experiments

실험 단위 문서, ablation 기록, run manifest를 보관한다. 실행 결과 파일은 `outputs`에
저장한다.

| 하위 디렉터리 | 실험 family |
| --- | --- |
| `retrieval` | BM25, sparse, dense, HyDE, RRF, query decomposition |
| `reranking` | LLM/listwise/pointwise reranking, sliding-window reranking |
| `evidence_selection` | nugget extraction, clustering, keystone-document selection |
| `generation` | citation-first generation, claim-citation alignment |
| `rag_end_to_end` | retrieval-to-answer 전체 pipeline |
| `relevance_judgment` | automatic/semi-manual relevance judgment experiments |
