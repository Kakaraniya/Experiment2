from __future__ import annotations

from _bootstrap import add_project_root_to_path

add_project_root_to_path()

from src.config import DEFAULT_DATA_PATH
from src.data import build_sample_dataset


def main() -> None:
    data_path = DEFAULT_DATA_PATH
    data_path.parent.mkdir(parents=True, exist_ok=True)
    build_sample_dataset().to_csv(data_path, index=False)
    print(f"Wrote sample dataset to {data_path}")


if __name__ == "__main__":
    main()
