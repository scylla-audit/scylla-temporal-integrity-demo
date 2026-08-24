"""Deterministic counterfactual test for future-data leakage."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize a value with stable key order and no insignificant spaces."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def load_history(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def observations_available_at_decision(history: dict[str, Any]) -> list[dict[str, Any]]:
    boundary = history["decision_time"]
    return [row for row in history["observations"] if row["available_at"] <= boundary]


def safe_decision(history: dict[str, Any]) -> str:
    """Use only observations available at or before the decision boundary."""
    known = observations_available_at_decision(history)
    if len(known) < 2:
        return "HOLD"
    return "BUY" if known[-1]["close"] > known[-2]["close"] else "HOLD"


def intentionally_leaky_decision(history: dict[str, Any]) -> str:
    """Teaching example: incorrectly reads the last value in the full history."""
    decision_close = observations_available_at_decision(history)[-1]["close"]
    future_close = history["observations"][-1]["close"]
    return "BUY" if future_close > decision_close else "SELL"


def compare_histories(history_a: dict[str, Any], history_b: dict[str, Any]) -> dict[str, Any]:
    available_a = observations_available_at_decision(history_a)
    available_b = observations_available_at_decision(history_b)
    safe_a = safe_decision(history_a)
    safe_b = safe_decision(history_b)
    leaky_a = intentionally_leaky_decision(history_a)
    leaky_b = intentionally_leaky_decision(history_b)

    result = {
        "decision_time": history_a["decision_time"],
        "histories_identical_through_decision": canonical_json(available_a) == canonical_json(available_b),
        "leaky_decision_a": leaky_a,
        "leaky_decision_b": leaky_b,
        "leaky_path_detected": leaky_a != leaky_b,
        "next_execution_open_identical": history_a["next_execution_open"] == history_b["next_execution_open"],
        "safe_decision_a": safe_a,
        "safe_decision_b": safe_b,
        "safe_path_invariant": safe_a == safe_b,
    }
    result["result"] = "PASS" if all(
        [
            result["histories_identical_through_decision"],
            result["next_execution_open_identical"],
            result["safe_path_invariant"],
            result["leaky_path_detected"],
        ]
    ) else "FAIL"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-a", type=Path, required=True)
    parser.add_argument("--history-b", type=Path, required=True)
    args = parser.parse_args()

    result = compare_histories(load_history(args.history_a), load_history(args.history_b))
    output = canonical_json(result)
    print(output)
    print(canonical_json({
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest().upper(),
        "result": result["result"],
    }))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
