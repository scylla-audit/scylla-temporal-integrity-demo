from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scylla_temporal_demo.demo import (  # noqa: E402
    canonical_json,
    compare_histories,
    intentionally_leaky_decision,
    load_history,
    observations_available_at_decision,
    safe_decision,
)


class TemporalIntegrityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.a = load_history(ROOT / "examples" / "history_a.json")
        cls.b = load_history(ROOT / "examples" / "history_b.json")

    def test_histories_are_identical_through_decision_time(self) -> None:
        self.assertEqual(
            canonical_json(observations_available_at_decision(self.a)),
            canonical_json(observations_available_at_decision(self.b)),
        )

    def test_only_future_information_differs(self) -> None:
        stripped_a = json.loads(canonical_json(self.a))
        stripped_b = json.loads(canonical_json(self.b))
        future_a = stripped_a["observations"].pop()
        future_b = stripped_b["observations"].pop()
        self.assertEqual(stripped_a, stripped_b)
        self.assertEqual(future_a["open"], future_b["open"])
        self.assertNotEqual(future_a["close"], future_b["close"])

    def test_safe_decision_is_invariant(self) -> None:
        self.assertEqual(safe_decision(self.a), safe_decision(self.b))

    def test_leaky_decision_is_detected(self) -> None:
        self.assertNotEqual(
            intentionally_leaky_decision(self.a),
            intentionally_leaky_decision(self.b),
        )

    def test_canonical_result_passes(self) -> None:
        result = compare_histories(self.a, self.b)
        self.assertEqual("PASS", result["result"])
        self.assertTrue(result["safe_path_invariant"])
        self.assertTrue(result["leaky_path_detected"])


if __name__ == "__main__":
    unittest.main()
