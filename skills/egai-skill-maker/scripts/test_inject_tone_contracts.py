#!/usr/bin/env python3
"""Regression tests for public, self-contained tone injection."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent
SCRIPT = SCRIPTS / "inject-tone-contracts.py"
SPEC = importlib.util.spec_from_file_location("inject_tone_contracts", SCRIPT)
assert SPEC and SPEC.loader
injector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(injector)


class ToneInjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="tone-injection-"))
        self.addCleanup(shutil.rmtree, self.root)
        self.skill = self.root / "target"
        self.skill.mkdir()
        (self.skill / "SKILL.md").write_text("# Target\n", encoding="utf-8")

    def test_injects_pinned_kernel_and_selected_profile(self) -> None:
        target = injector.inject(self.skill, "compact", "## Context tone", False)
        text = target.read_text(encoding="utf-8")
        self.assertTrue(target.is_file())
        self.assertIn("# Tone Guidance\n\n## Kernel\n**Canonical Kernel — v1**", text)
        self.assertIn("## Context tone\n**Compact — v1**", text)
        self.assertNotIn("VERSIONED_" + "CAPABILITY_PLACEHOLDER", text)
        self.assertNotIn("repository tone manifest", text)

    def test_refuses_an_existing_reference_without_replace(self) -> None:
        existing = self.skill / "references" / "tone.md"
        existing.parent.mkdir()
        existing.write_text("keep\n", encoding="utf-8")
        with self.assertRaisesRegex(injector.ToneInjectionError, "refusing to replace"):
            injector.inject(self.skill, "terse", "## Output tone", False)
        self.assertEqual(existing.read_text(encoding="utf-8"), "keep\n")

    def test_rejects_a_non_level_two_heading(self) -> None:
        with self.assertRaisesRegex(injector.ToneInjectionError, "must begin"):
            injector.inject(self.skill, "prose", "# Output tone", False)

    def test_copied_public_package_needs_no_repository_compiler(self) -> None:
        published = self.root / "published-egai-skill-maker"
        shutil.copytree(SCRIPTS.parent, published)
        target = self.root / "portable-target"
        target.mkdir()
        (target / "SKILL.md").write_text("# Portable target\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(published / "scripts" / "inject-tone-contracts.py"),
                str(target),
                "--profile",
                "terse-report",
                "--heading",
                "## Delivery report tone",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (target / "references" / "tone.md").read_text(encoding="utf-8")
        self.assertIn("**Canonical Kernel — v1**", text)
        self.assertIn("## Delivery report tone\n**Terse Report — v1**", text)


if __name__ == "__main__":
    unittest.main()
