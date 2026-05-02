#!/usr/bin/env python3
"""
Docker Compose Formatter (Recursive)
Version: 1.1.0
"""

import os
import sys
import yaml
from collections import OrderedDict

VERSION = "1.1.0"


# ---------- File Discovery ----------

def find_yaml_files(root: str):
    """
    Recursively find docker compose files.
    Safe + deterministic ordering.
    """
    targets = []

    for dirpath, _, filenames in os.walk(root):
        filenames.sort()

        for name in filenames:
            lower = name.lower()

            if lower in ("docker-compose.yml", "docker-compose.yaml"):
                targets.append(os.path.join(dirpath, name))

            # Optional broader support (comment out if too wide)
            elif lower.endswith(".yml") or lower.endswith(".yaml"):
                targets.append(os.path.join(dirpath, name))

    return sorted(set(targets))


# ---------- YAML Handling ----------

def safe_load(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] Read failed: {file_path} -> {e}")
        return None


def safe_write(file_path: str, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True
            )
    except Exception as e:
        print(f"[ERROR] Write failed: {file_path} -> {e}")


# ---------- Normalization ----------

def sort_dict(obj):
    if isinstance(obj, dict):
        return OrderedDict(
            sorted(
                ((k, sort_dict(v)) for k, v in obj.items()),
                key=lambda x: x[0]
            )
        )

    if isinstance(obj, list):
        return [sort_dict(i) for i in obj]

    return obj


def normalize_compose(data):
    if not isinstance(data, dict):
        return None

    ordered = OrderedDict()

    preferred = ["version", "services", "networks", "volumes"]

    for key in preferred:
        if key in data:
            ordered[key] = sort_dict(data[key])

    for key in sorted(data.keys()):
        if key not in ordered:
            ordered[key] = sort_dict(data[key])

    return ordered


# ---------- Processing ----------

def format_file(path: str):
    print(f"[FORMAT] {path}")

    data = safe_load(path)
    if data is None:
        return

    normalized = normalize_compose(data)
    if normalized is None:
        print(f"[SKIP] Invalid structure: {path}")
        return

    safe_write(path, normalized)


def run(root: str):
    print(f"Docker Compose Formatter v{VERSION}")
    print(f"[SCAN] Root: {root}")

    files = find_yaml_files(root)

    if not files:
        print("[INFO] No YAML files found")
        return

    print(f"[FOUND] {len(files)} files")

    for f in files:
        format_file(f)

    print("[DONE]")


# ---------- Entry ----------

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    run(root)
