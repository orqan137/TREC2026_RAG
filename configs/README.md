# Configs

실험 재현을 위한 정적 설정 파일을 보관한다. 실행 중 생성되는 결과는 이 디렉터리에
저장하지 않는다.

| 하위 디렉터리 | 용도 |
| --- | --- |
| `retrieval` | first-stage retrieval, fusion, query expansion 설정 |
| `reranking` | cross-encoder, LLM reranking, sliding-window reranking 설정 |
| `generation` | answer generation, citation alignment, prompt 설정 |
| `experiments` | ablation 단위의 end-to-end run manifest |
