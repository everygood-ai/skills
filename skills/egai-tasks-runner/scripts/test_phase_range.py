from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PHASE_RANGE = Path(__file__).resolve().parent / "phase-range.py"


def make_phase(parent: Path, number: int, task_count: int = 1) -> Path:
    phase_dir = parent / f"phase-{number}"
    phase_dir.mkdir()
    (phase_dir / "index.md").write_text(
        f'---\nkind: "phase"\nname: "Name"\n---\n# Phase {number}: Name\n',
        encoding="utf-8",
    )
    for task_number in range(1, task_count + 1):
        (phase_dir / f"task-{task_number}-do-thing.md").write_text(
            "---\n---\n", encoding="utf-8"
        )
    return phase_dir


class PhaseRangeTests(unittest.TestCase):
    def run_phase_range(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(PHASE_RANGE), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )

    def test_count_lists_consecutive_sibling_phases(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phases = [make_phase(group, number) for number in range(3, 7)]

            result = self.run_phase_range(str(phases[0]), "--count", "4")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "".join(f"{phase}\n" for phase in phases),
            )

    def test_end_phase_lists_the_same_range_as_count(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phases = [make_phase(group, number) for number in range(3, 7)]

            result = self.run_phase_range(str(phases[0]), "--end", str(phases[-1]))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "".join(f"{phase}\n" for phase in phases),
            )

    def test_single_phase_range_with_count_one(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase = make_phase(group, 1)

            result = self.run_phase_range(str(phase), "--count", "1")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{phase}\n")

    def test_index_md_path_is_accepted_for_start_and_end(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phases = [make_phase(group, number) for number in range(1, 3)]

            result = self.run_phase_range(
                str(phases[0] / "index.md"), "--end", str(phases[-1] / "index.md")
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "".join(f"{phase}\n" for phase in phases),
            )

    def test_count_skips_over_a_deleted_phase_in_the_middle(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase_3 = make_phase(group, 3)
            # phase-4 was deleted after task-writing: no directory for it.
            phase_5 = make_phase(group, 5)
            phase_6 = make_phase(group, 6)

            result = self.run_phase_range(str(phase_3), "--count", "3")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{phase_3}\n{phase_5}\n{phase_6}\n")

    def test_end_phase_after_a_gap_still_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase_3 = make_phase(group, 3)
            phase_5 = make_phase(group, 5)

            result = self.run_phase_range(str(phase_3), "--end", str(phase_5))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{phase_3}\n{phase_5}\n")

    def test_count_past_the_group_boundary_caps_instead_of_failing(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase = make_phase(group, 1)
            # No other phase under this group: simulates the group boundary.

            result = self.run_phase_range(str(phase), "--count", "2")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{phase}\n")
            self.assertIn("requested 2 phases", result.stderr)
            self.assertIn("only 1 exist", result.stderr)
            self.assertIn("never crosses into a sibling group", result.stderr)

    def test_count_exactly_matching_what_exists_is_not_capped(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phases = [make_phase(group, number) for number in range(1, 3)]

            result = self.run_phase_range(str(phases[0]), "--count", "2")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "".join(f"{phase}\n" for phase in phases))
            self.assertEqual(result.stderr, "")

    def test_incompatible_phase_directory_name_fails_fast(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase = make_phase(group, 1)
            make_phase(group, 2)
            # A phase directory with a leading zero: not phase-N, but clearly
            # meant to be one. It would otherwise sort invisibly out of range.
            (group / "phase-03").mkdir()
            (group / "phase-03" / "index.md").write_text(
                '---\nkind: "phase"\nname: "Name"\n---\n# Phase 3: Name\n', encoding="utf-8"
            )

            result = self.run_phase_range(str(phase), "--count", "2")

            self.assertEqual(result.returncode, 1)
            self.assertIn("incompatible phase directory name 'phase-03'", result.stderr)

    def test_incompatible_name_fails_even_outside_the_requested_window(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase = make_phase(group, 1)
            make_phase(group, 2)
            # Wrong case, far past the requested range: still caught, since
            # the whole parent is scanned on every resolution, not just the
            # requested window.
            (group / "Phase-9").mkdir()
            (group / "Phase-9" / "index.md").write_text(
                '---\nkind: "phase"\nname: "Name"\n---\n# Phase 9: Name\n', encoding="utf-8"
            )

            result = self.run_phase_range(str(phase), "--count", "1")

            self.assertEqual(result.returncode, 1)
            self.assertIn("incompatible phase directory name 'Phase-9'", result.stderr)

    def test_unrelated_directory_names_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            phase = make_phase(group, 1)
            (group / "assets").mkdir()
            (group / "README.md").write_text("notes\n", encoding="utf-8")

            result = self.run_phase_range(str(phase), "--count", "1")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, f"{phase}\n")

    def test_end_before_start_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            make_phase(group, 3)
            make_phase(group, 5)

            result = self.run_phase_range(str(group / "phase-5"), "--end", str(group / "phase-3"))

            self.assertEqual(result.returncode, 1)
            self.assertIn("comes before start", result.stderr)

    def test_start_path_that_is_not_a_phase_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            (group / "index.md").write_text(
                '---\nkind: "group"\nname: "Group"\n---\n# Group\n', encoding="utf-8"
            )
            child = group / "phase-1"
            child.mkdir()
            (child / "index.md").write_text(
                '---\nkind: "phase"\nname: "Name"\n---\n# Phase 1: Name\n', encoding="utf-8"
            )

            result = self.run_phase_range(str(group), "--count", "1")

            self.assertEqual(result.returncode, 1)
            self.assertIn("not a phase", result.stderr)

    def test_end_phase_not_under_the_same_parent_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            group = Path(root)
            make_phase(group, 1)
            other_group = group / "epic-other"
            other_group.mkdir()
            other_phase = make_phase(other_group, 1)

            result = self.run_phase_range(str(group / "phase-1"), "--end", str(other_phase))

            self.assertEqual(result.returncode, 1)
            self.assertIn("is not a phase-N directory under", result.stderr)

    def test_missing_both_count_and_end_is_a_usage_error(self) -> None:
        result = self.run_phase_range("some-phase")

        self.assertEqual(result.returncode, 2)
        self.assertIn("usage: phase-range.py", result.stderr)


if __name__ == "__main__":
    unittest.main()
