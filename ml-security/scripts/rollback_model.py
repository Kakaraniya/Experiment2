from __future__ import annotations

import json

from _bootstrap import add_project_root_to_path

add_project_root_to_path()

from src.config import MODEL_DIR


def main() -> None:
    history_path = MODEL_DIR / "model_history.json"
    latest_path = MODEL_DIR / "latest.json"

    if not history_path.exists() or not latest_path.exists():
        raise SystemExit("Rollback failed: model history is incomplete")

    history = json.loads(history_path.read_text(encoding="utf-8"))
    if len(history) < 2:
        raise SystemExit("Rollback failed: no previous model version is available")

    previous_entry = history[-2]
    latest_path.write_text(json.dumps(previous_entry, indent=2), encoding="utf-8")
    print(json.dumps({"status": "rolled_back", "restored_model": previous_entry["model_path"]}, indent=2))


if __name__ == "__main__":
    main()
