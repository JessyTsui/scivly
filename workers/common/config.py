from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_CONFIG_DIR = REPO_ROOT / "config" / "reference"


def _read_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in YAML file: {path}")
    return loaded


@lru_cache(maxsize=None)
def load_reference_config(filename: str) -> dict[str, Any]:
    path = REFERENCE_CONFIG_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Reference config not found: {path}")
    return _read_yaml_file(path)


@lru_cache(maxsize=1)
def load_default_triage_profile() -> dict[str, Any]:
    config = load_reference_config("paper_triage_defaults.yaml")
    profile = config.get("default_profile")
    if not isinstance(profile, dict):
        raise ValueError("paper_triage_defaults.yaml is missing default_profile")
    return profile


@lru_cache(maxsize=1)
def load_institution_priors() -> dict[str, Any]:
    return load_reference_config("institution_priors.yaml")


@lru_cache(maxsize=1)
def load_lab_priors() -> dict[str, Any]:
    return load_reference_config("lab_priors.yaml")
