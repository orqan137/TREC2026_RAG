from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DEFAULT_BASE_URL = "http://99.251.12.72:8081"
DEFAULT_INDEX = "climbmix-400b"
DEFAULT_HITS = 100
DEFAULT_RUN_ID = "pyserini-climbmix-baseline"
DEFAULT_TOPIC_FILE = "trec_rag_2026_queries.jsonl"
DEFAULT_RETRIEVAL_OUTPUT = "outputs/r_output_trec_rag_2026.tsv"
DEFAULT_CACHE_DIR = "data/cache/pyserini"
TOKEN_KEYS = ("PYSERINI_API_TOKEN", "PYSERINI_TOKEN")


class PipelineError(RuntimeError):
    pass


class ApiError(PipelineError):
    def __init__(self, status: int | None, message: str):
        self.status = status
        super().__init__(message)


@dataclass(frozen=True)
class Topic:
    id: str
    title: str
    narrative: str


@dataclass(frozen=True)
class EnvConfig:
    base_url: str
    token: str
    loaded_env_files: tuple[Path, ...]


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def candidate_env_files(project_root: Path, explicit: Path | None = None) -> list[Path]:
    paths = [
        project_root / "trec-rag-skills" / ".env",
        project_root / "trec-rag-skills" / ".env.local",
        project_root / "trec_rag_skills" / ".env",
        project_root / "trec_rag_skills" / ".env.local",
        project_root / ".env",
        project_root / ".env.local",
    ]
    if explicit is not None:
        paths.append(explicit if explicit.is_absolute() else project_root / explicit)
    return paths


def load_env_config(
    project_root: Path,
    explicit_env_file: Path | None,
    explicit_base_url: str | None,
) -> EnvConfig:
    merged: dict[str, str] = {}
    loaded: list[Path] = []
    for env_file in candidate_env_files(project_root, explicit_env_file):
        values = parse_env_file(env_file)
        if values:
            merged.update(values)
            loaded.append(env_file)

    for key, value in os.environ.items():
        if key.startswith("PYSERINI_"):
            merged[key] = value

    token = next((merged[key].strip() for key in TOKEN_KEYS if merged.get(key, "").strip()), "")
    if not token:
        checked = ", ".join(str(path) for path in candidate_env_files(project_root, explicit_env_file))
        raise PipelineError(
            "Pyserini token not found. Expected PYSERINI_API_TOKEN or PYSERINI_TOKEN "
            f"in one of: {checked}"
        )

    base_url = (
        explicit_base_url
        or merged.get("PYSERINI_API_BASE_URL")
        or merged.get("PYSERINI_BASE_URL")
        or DEFAULT_BASE_URL
    )
    return EnvConfig(base_url=base_url.rstrip("/"), token=token, loaded_env_files=tuple(loaded))


def auth_header(token: str) -> str:
    normalized = token.strip()
    lowered = normalized.lower()
    if lowered.startswith(("bearer ", "token ", "basic ")):
        return normalized
    return f"Bearer {normalized}"


class PyseriniClient:
    def __init__(self, base_url: str, token: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": auth_header(token),
            "User-Agent": "trec2026-search-pipeline/0.1",
            "Accept": "application/json",
        }

    def health_root(self) -> dict[str, Any]:
        return self._get_json(f"{self.base_url}/", authenticated=False)

    def search(self, index: str, query: str, hits: int) -> dict[str, Any]:
        if hits <= 0:
            raise PipelineError("--hits must be positive")
        params = parse.urlencode({"query": query, "hits": hits})
        return self._get_json(f"{self.base_url}/v1/{parse.quote(index)}/search?{params}")

    def fetch_doc(self, index: str, docid: str) -> dict[str, Any]:
        return self._get_json(f"{self.base_url}/v1/{parse.quote(index)}/doc/{parse.quote(docid, safe='')}")

    def _get_json(self, url: str, authenticated: bool = True) -> dict[str, Any]:
        headers = self.headers if authenticated else {"User-Agent": self.headers["User-Agent"]}
        req = request.Request(url, headers=headers, method="GET")
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                return json.loads(body) if body else {}
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            message = extract_error_message(body) or exc.reason or f"HTTP {exc.code}"
            raise ApiError(exc.code, message) from exc
        except error.URLError as exc:
            raise ApiError(None, str(exc.reason)) from exc
        except TimeoutError as exc:
            raise ApiError(None, "request timed out") from exc
        except json.JSONDecodeError as exc:
            raise ApiError(None, f"response was not valid JSON: {exc}") from exc


def extract_error_message(body: str) -> str:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body.strip()
    if isinstance(payload, dict) and isinstance(payload.get("error"), str):
        return payload["error"]
    return json.dumps(payload, ensure_ascii=False)


def resolve_path(project_root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def load_json_config(project_root: Path, config_path: Path | None) -> dict[str, Any]:
    path = resolve_path(project_root, config_path) if config_path else project_root / "configs" / "search_pipeline.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid config JSON at {path}: {exc}") from exc


def read_topics(path: Path) -> list[Topic]:
    if not path.exists():
        raise PipelineError(f"Topic file not found: {path}")
    topics: list[Topic] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise PipelineError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
        missing = [field for field in ("id", "title", "narrative") if field not in payload]
        if missing:
            raise PipelineError(f"Topic at {path}:{line_no} is missing fields: {', '.join(missing)}")
        topics.append(Topic(id=str(payload["id"]), title=str(payload["title"]), narrative=str(payload["narrative"])))
    if not topics:
        raise PipelineError(f"No topics found in {path}")
    return topics


def safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_", ".") else "_" for ch in value)[:120] or "topic"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def format_score(value: Any) -> str:
    try:
        return f"{float(value):.10g}"
    except (TypeError, ValueError):
        return str(value)


def run_retrieval(
    client: PyseriniClient,
    topics_path: Path,
    output_path: Path,
    cache_dir: Path,
    index: str,
    hits: int,
    run_id: str,
) -> dict[str, Any]:
    topics = read_topics(topics_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)

    rows: list[str] = []
    topic_counts: dict[str, int] = {}
    for topic in topics:
        response = client.search(index=index, query=topic.title, hits=hits)
        candidates = response.get("candidates")
        if not isinstance(candidates, list):
            raise PipelineError(f"Search response for topic {topic.id} did not include a candidates list")
        write_json(cache_dir / f"{safe_name(topic.id)}.search.json", response)

        topic_counts[topic.id] = len(candidates)
        for rank, candidate in enumerate(candidates, start=1):
            if not isinstance(candidate, dict):
                raise PipelineError(f"Candidate {rank} for topic {topic.id} was not an object")
            docid = candidate.get("docid")
            if not docid:
                raise PipelineError(f"Candidate {rank} for topic {topic.id} is missing docid")
            rows.append(f"{topic.id} Q0 {docid} {rank} {format_score(candidate.get('score', 0.0))} {run_id}")

    output_path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return {
        "topics": len(topics),
        "rows": len(rows),
        "output": str(output_path),
        "cache_dir": str(cache_dir),
        "hits": hits,
        "index": index,
        "run_id": run_id,
        "topic_counts": topic_counts,
    }


def validate_runfile(topics_path: Path, runfile_path: Path) -> dict[str, Any]:
    topics = read_topics(topics_path)
    expected_ids = {topic.id for topic in topics}
    seen: dict[str, list[tuple[int, float, str]]] = {}
    errors: list[str] = []

    if not runfile_path.exists():
        raise PipelineError(f"Runfile not found: {runfile_path}")

    for line_no, raw_line in enumerate(runfile_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip():
            continue
        parts = raw_line.split()
        if len(parts) != 6:
            errors.append(f"{runfile_path}:{line_no}: expected 6 columns, got {len(parts)}")
            continue
        topic_id, q0, docid, rank_text, score_text, _run_id = parts
        if q0 != "Q0":
            errors.append(f"{runfile_path}:{line_no}: column 2 must be Q0")
        if topic_id not in expected_ids:
            errors.append(f"{runfile_path}:{line_no}: unknown topic id {topic_id}")
        try:
            rank = int(rank_text)
        except ValueError:
            errors.append(f"{runfile_path}:{line_no}: rank is not an integer")
            continue
        if rank <= 0:
            errors.append(f"{runfile_path}:{line_no}: rank must be positive")
        try:
            score = float(score_text)
        except ValueError:
            errors.append(f"{runfile_path}:{line_no}: score is not numeric")
            continue
        seen.setdefault(topic_id, []).append((rank, score, docid))

    missing = sorted(expected_ids - set(seen))
    for topic_id in missing:
        errors.append(f"missing output for topic {topic_id}")

    for topic_id, rows in seen.items():
        ranks = [rank for rank, _score, _docid in rows]
        expected_ranks = list(range(1, len(rows) + 1))
        if ranks != expected_ranks:
            errors.append(f"topic {topic_id}: ranks must be contiguous from 1")
        scores = [score for _rank, score, _docid in rows]
        for left, right in zip(scores, scores[1:]):
            if right > left + 1e-9:
                errors.append(f"topic {topic_id}: scores must be non-increasing")
                break

    return {
        "valid": not errors,
        "topics_expected": len(expected_ids),
        "topics_seen": len(seen),
        "rows": sum(len(rows) for rows in seen.values()),
        "errors": errors,
    }


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_client(args: argparse.Namespace, project_root: Path) -> tuple[PyseriniClient, EnvConfig]:
    env_config = load_env_config(
        project_root=project_root,
        explicit_env_file=args.env_file,
        explicit_base_url=args.base_url,
    )
    client = PyseriniClient(base_url=env_config.base_url, token=env_config.token, timeout=args.timeout)
    return client, env_config


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--env-file", type=Path, default=None, help="Optional dotenv file to load last.")
    parser.add_argument("--base-url", default=None, help=f"Pyserini REST base URL. Default: {DEFAULT_BASE_URL}")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds.")


def main(default_project_root: Path | None = None, argv: list[str] | None = None) -> int:
    project_root = default_project_root or Path.cwd()
    parser = argparse.ArgumentParser(description="TREC RAG 2026 Pyserini/ClimbMix search pipeline")
    parser.add_argument("--root", type=Path, default=project_root, help="Project root directory.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health", help="Check root endpoint and authenticated search.")
    add_common_args(health_parser)
    health_parser.add_argument("--index", default=DEFAULT_INDEX)

    search_parser = subparsers.add_parser("search", help="Run a single ClimbMix search.")
    add_common_args(search_parser)
    search_parser.add_argument("query")
    search_parser.add_argument("--index", default=DEFAULT_INDEX)
    search_parser.add_argument("--hits", type=int, default=5)
    search_parser.add_argument("--out", type=Path, default=Path("tmp/pyserini-rest-search.json"))

    fetch_parser = subparsers.add_parser("fetch-doc", help="Fetch one document by docid.")
    add_common_args(fetch_parser)
    fetch_parser.add_argument("docid")
    fetch_parser.add_argument("--index", default=DEFAULT_INDEX)
    fetch_parser.add_argument("--out", type=Path, default=Path("tmp/pyserini-rest-doc.json"))

    run_parser = subparsers.add_parser("run", help="Build r_output_trec_rag_2026.tsv from topics.")
    add_common_args(run_parser)
    run_parser.add_argument("--config", type=Path, default=None)
    run_parser.add_argument("--topics", type=Path, default=None)
    run_parser.add_argument("--out", type=Path, default=None)
    run_parser.add_argument("--cache-dir", type=Path, default=None)
    run_parser.add_argument("--index", default=None)
    run_parser.add_argument("--hits", type=int, default=None)
    run_parser.add_argument("--run-id", default=None)

    validate_parser = subparsers.add_parser("validate-run", help="Validate a TREC Retrieval runfile.")
    validate_parser.add_argument("--config", type=Path, default=None)
    validate_parser.add_argument("--topics", type=Path, default=None)
    validate_parser.add_argument("--runfile", type=Path, default=None)

    args = parser.parse_args(argv)
    root = args.root.resolve()

    try:
        if args.command == "health":
            client, env_config = build_client(args, root)
            root_payload = client.health_root()
            search_payload = client.search(index=args.index, query="Albert Einstein", hits=1)
            candidates = search_payload.get("candidates") if isinstance(search_payload, dict) else []
            first = candidates[0] if isinstance(candidates, list) and candidates else None
            print_json(
                {
                    "base_url": env_config.base_url,
                    "loaded_env_files": [str(path) for path in env_config.loaded_env_files],
                    "root": root_payload,
                    "search": {
                        "index": search_payload.get("index"),
                        "candidate_count": len(candidates) if isinstance(candidates, list) else 0,
                        "first": {
                            "rank": first.get("rank"),
                            "docid": first.get("docid"),
                            "score": first.get("score"),
                            "has_doc": first.get("doc") is not None,
                        }
                        if isinstance(first, dict)
                        else None,
                    },
                }
            )
            return 0

        if args.command == "search":
            client, env_config = build_client(args, root)
            payload = client.search(index=args.index, query=args.query, hits=args.hits)
            out_path = resolve_path(root, args.out)
            write_json(out_path, payload)
            candidates = payload.get("candidates")
            compact = [
                {"rank": item.get("rank"), "score": item.get("score"), "docid": item.get("docid")}
                for item in candidates
                if isinstance(item, dict)
            ] if isinstance(candidates, list) else []
            print_json(
                {
                    "base_url": env_config.base_url,
                    "out": str(out_path),
                    "index": payload.get("index"),
                    "query": payload.get("query"),
                    "candidates": compact,
                }
            )
            return 0

        if args.command == "fetch-doc":
            client, env_config = build_client(args, root)
            payload = client.fetch_doc(index=args.index, docid=args.docid)
            out_path = resolve_path(root, args.out)
            write_json(out_path, payload)
            print_json(
                {
                    "base_url": env_config.base_url,
                    "out": str(out_path),
                    "index": payload.get("index"),
                    "docid": payload.get("docid"),
                    "has_doc": payload.get("doc") is not None,
                }
            )
            return 0

        if args.command == "run":
            config = load_json_config(root, args.config)
            client, _env_config = build_client(args, root)
            topics = resolve_path(root, args.topics or config.get("topic_file", DEFAULT_TOPIC_FILE))
            out = resolve_path(root, args.out or config.get("retrieval_output", DEFAULT_RETRIEVAL_OUTPUT))
            cache_dir = resolve_path(root, args.cache_dir or config.get("cache_dir", DEFAULT_CACHE_DIR))
            summary = run_retrieval(
                client=client,
                topics_path=topics,
                output_path=out,
                cache_dir=cache_dir,
                index=args.index or config.get("index", DEFAULT_INDEX),
                hits=args.hits if args.hits is not None else int(config.get("default_hits", DEFAULT_HITS)),
                run_id=args.run_id or config.get("run_id", DEFAULT_RUN_ID),
            )
            print_json(summary)
            return 0

        if args.command == "validate-run":
            config = load_json_config(root, args.config)
            topics = resolve_path(root, args.topics or config.get("topic_file", DEFAULT_TOPIC_FILE))
            runfile = resolve_path(root, args.runfile or config.get("retrieval_output", DEFAULT_RETRIEVAL_OUTPUT))
            summary = validate_runfile(topics_path=topics, runfile_path=runfile)
            print_json(summary)
            return 0 if summary["valid"] else 2

    except ApiError as exc:
        status = exc.status if exc.status is not None else "network"
        print_json({"error": str(exc), "status": status})
        return 1
    except PipelineError as exc:
        print_json({"error": str(exc)})
        return 1

    parser.error(f"Unhandled command: {args.command}")
    return 2
