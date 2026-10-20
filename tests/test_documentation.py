from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MILESTONE_STATUSES = {"Pending", "In progress", "Blocked", "Complete"}
MILESTONE1_ADRS = {
    "0001-cpp20-core-and-cmake.md",
    "0002-domain-logic-adapter-separation.md",
    "0003-canonical-serialization-and-digests.md",
    "0004-test-fixtures-are-not-measurements.md",
    "0005-dry-run-apply-rollback-boundary.md",
    "0006-frontend-selection-deferred-to-d01.md",
}


def _plan_rows() -> dict[int, dict[str, object]]:
    """Parse PLAN.md rows: M | Category | Milestone | Dependencies | Gates | Status | Done."""
    rows: dict[int, dict[str, object]] = {}
    for line in (ROOT / "PLAN.md").read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\| *\d{1,2} \|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            raise AssertionError(f"PLAN.md row does not have 7 columns: {line}")
        dependencies: list[int] = []
        for first, last in re.findall(r"M(\d+)(?:\s*[–-]\s*M?(\d+))?", cells[3]):
            dependencies.extend(range(int(first), int(last or first) + 1))
        rows[int(cells[0])] = {"dependencies": dependencies, "status": cells[5]}
    return rows


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

    def test_plan_and_progress_track_all_17_milestones_consistently(self) -> None:
        plan = _plan_rows()
        self.assertEqual(list(range(1, 18)), sorted(plan))
        progress_text = (ROOT / "PROGRESS.md").read_text(encoding="utf-8")
        progress = {
            int(number): status.strip()
            for number, status in re.findall(r"(?m)^\| (\d{1,2})\. [^|]*\| ([^|]+?) \|", progress_text)
        }
        self.assertEqual(list(range(1, 18)), sorted(progress))
        self.assertEqual("Complete", plan[1]["status"])
        for milestone, row in plan.items():
            self.assertIn(row["status"], MILESTONE_STATUSES, f"PLAN.md M{milestone}")
            self.assertEqual(row["status"], progress[milestone], f"M{milestone} status differs between PLAN.md and PROGRESS.md")
            if row["status"] == "Complete":
                for dependency in row["dependencies"]:
                    self.assertEqual(
                        "Complete", plan[dependency]["status"],
                        f"M{milestone} is Complete but its dependency M{dependency} is not",
                    )

    def test_architecture_decisions_are_well_formed_and_milestone1_adrs_remain(self) -> None:
        adrs = sorted((ROOT / "docs/adr").glob("*.md"))
        names = {path.name for path in adrs}
        self.assertTrue(MILESTONE1_ADRS <= names, sorted(MILESTONE1_ADRS - names))
        numbers = []
        for path in adrs:
            match = re.fullmatch(r"(\d{4})-[a-z0-9-]+\.md", path.name)
            self.assertIsNotNone(match, path.name)
            numbers.append(match.group(1))
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text, r"Status: (Proposed|Accepted|Superseded|Deprecated)\b", path.name)
            self.assertIn("## Decision", text, path.name)
            self.assertIn("## Consequences", text, path.name)
        self.assertEqual(len(numbers), len(set(numbers)), "ADR numbers must be unique")


if __name__ == "__main__":
    unittest.main()
