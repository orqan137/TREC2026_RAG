# Data

대회 입력, 외부 reference, official judgment, retrieval cache를 분리한다. 대용량 또는
license가 명확하지 않은 official data는 Git 추적 대상에서 제외한다.

| 하위 디렉터리 | 용도 | Git 정책 |
| --- | --- | --- |
| `topics` | official/sample topic JSONL | sample만 추적 |
| `corpus` | local corpus 또는 shard metadata | `.gitkeep`만 추적 |
| `baselines` | organizer baseline runs | `.gitkeep`만 추적 |
| `qrels` | doc relevance qrels | `.gitkeep`만 추적 |
| `nuggets` | nugget qrels/evaluation artifacts | `.gitkeep`만 추적 |
| `cache` | API responses, retrieved document packets | 제외 |
