from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trec2026.search_pipeline import main


if __name__ == "__main__":
    raise SystemExit(main(default_project_root=PROJECT_ROOT))
