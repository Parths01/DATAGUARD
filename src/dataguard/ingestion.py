from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from dataguard.db import DataGuardDB


def _hash_content(source_path: str) -> str:
    digest = hashlib.sha256()
    with Path(source_path).open("rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ingest_dataset_batch(db: DataGuardDB, dataset: dict[str, Any], source_path: str) -> dict[str, Any]:
    path = Path(source_path)
    dataframe = pd.read_csv(path)
    batch_id = _hash_content(str(path))
    db.register_dataset(dataset)
    return {
        "batch_id": batch_id,
        "dataset_id": dataset.get("dataset_id"),
        "dataset_name": dataset.get("dataset_name"),
        "source_path": str(path),
        "row_count": len(dataframe),
        "dataframe": dataframe,
    }
