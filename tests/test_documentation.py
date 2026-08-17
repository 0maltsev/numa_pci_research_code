from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationCoverageTests(unittest.TestCase):
    def test_contract_map_covers_c01_through_c24_once(self) -> None:
        text = (ROOT / "docs/contracts/CONTRACT_MAP.md").read_text(encoding="utf-8")
        found = re.findall(r"^\| (C\d{2})\b", text, flags=re.MULTILINE)
        self.assertEqual([f"C{index:02d}" for index in range(1, 25)], found)
        for column in ("Producer", "Consumers", "v1 schema(s)", "Implementation component", "Required tests", "Delivery milestone", "Unresolved decision dependencies"):
            self.assertIn(column, text)

    def test_rq_and_baseline_documents_are_complete(self) -> None:
        rq = (ROOT / "docs/contracts/RQ_FIELD_MATRIX.md").read_text(encoding="utf-8")
        for index in range(1, 7):
            self.assertIn(f"RQ{index}", rq)
        for output in ("Sole-primary", "key-secondary", "Operational feasibility", "Scientific exclusion"):
            self.assertIn(output, rq)

        baseline = (ROOT / "docs/contracts/BASELINE_MATRIX.md").read_text(encoding="utf-8")
        for policy in ("B0", "B1", "B2", "B3"):
            self.assertIn(policy, baseline)
        for distinction in ("Desired", "requested", "applied", "observed"):
            self.assertIn(distinction, baseline)

    def test_plan_has_all_17_milestones_and_later_work_is_pending(self) -> None:
        plan = (ROOT / "PLAN.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| (\d{1,2}) \|", plan, flags=re.MULTILINE)
        self.assertEqual([str(index) for index in range(1, 18)], rows)
        progress = (ROOT / "PROGRESS.md").read_text(encoding="utf-8")
        for index in range(2, 18):
            self.assertRegex(progress, rf"(?m)^\| {index}\..*\| Pending \|")

    def test_all_six_architecture_decisions_exist(self) -> None:
        adrs = sorted((ROOT / "docs/adr").glob("*.md"))
        self.assertEqual(6, len(adrs))
        for path in adrs:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Status: Accepted", text, path.name)
            self.assertIn("## Decision", text, path.name)
            self.assertIn("## Consequences", text, path.name)


if __name__ == "__main__":
    unittest.main()
