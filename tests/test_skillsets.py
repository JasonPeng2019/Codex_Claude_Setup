from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELECTOR = ROOT / ".agent" / "select-skillset.py"
SELECTOR_SH = ROOT / ".agent" / "select-skillset.sh"
MANIFEST = ROOT / ".agent" / "skillsets.json"
RESEARCH_SOURCE = ROOT / ".agent" / "skillsets" / "research"
CATALOGS = (Path(".agents") / "skills", Path(".claude") / "skills")


# A bare "bash" can resolve to C:\Windows\System32\bash.exe (the WSL launcher
# shim) instead of Git for Windows' bash when both are installed. That shim
# cannot accept a plain Windows-drive path, so resolve Git Bash explicitly.
def find_git_bash() -> str | None:
    if os.name != "nt":
        return shutil.which("bash")
    roots = [os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"), os.environ.get("LocalAppData")]
    for root in roots:
        if not root:
            continue
        candidate = Path(root) / ("Git/bin/bash.exe" if "AppData" not in root else "Programs/Git/bin/bash.exe")
        if candidate.is_file():
            return str(candidate)
    fallback = shutil.which("bash")
    if fallback and Path(fallback).resolve().as_posix().lower() != "c:/windows/system32/bash.exe":
        return fallback
    return None


BASH = find_git_bash()


class SkillsetSelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable skillsets ")
        self.root = Path(self.temp.name)
        agent = self.root / ".agent"
        agent.mkdir()
        shutil.copy2(MANIFEST, agent / "skillsets.json")
        shutil.copytree(RESEARCH_SOURCE, agent / "skillsets" / "research")
        for catalog in CATALOGS:
            baseline = self.root / catalog / "principles"
            baseline.mkdir(parents=True)
            (baseline / "SKILL.md").write_text("---\nname: principles\n---\n", encoding="utf-8")
        self.research = tuple(json.loads(MANIFEST.read_text(encoding="utf-8"))["skillsets"]["research"])

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SELECTOR), command, "--root", str(self.root)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_research_adds_and_software_removes_only_research_skills(self) -> None:
        initial = self.invoke("current")
        self.assertEqual(initial.returncode, 0, initial.stderr)
        self.assertEqual(initial.stdout.strip(), "software")

        enabled = self.invoke("research")
        self.assertEqual(enabled.returncode, 0, enabled.stderr)
        self.assertEqual(enabled.stdout.strip(), "research")
        for catalog in CATALOGS:
            self.assertTrue((self.root / catalog / "principles" / "SKILL.md").is_file())
            for skill in self.research:
                visible = self.root / catalog / skill
                source = self.root / ".agent" / "skillsets" / "research" / skill
                self.assertTrue((visible / "SKILL.md").is_file())
                self.assertEqual(
                    (visible / "SKILL.md").read_bytes(),
                    (source / "SKILL.md").read_bytes(),
                )

        disabled = self.invoke("software")
        self.assertEqual(disabled.returncode, 0, disabled.stderr)
        self.assertEqual(disabled.stdout.strip(), "software")
        for catalog in CATALOGS:
            self.assertTrue((self.root / catalog / "principles" / "SKILL.md").is_file())
            for skill in self.research:
                self.assertFalse((self.root / catalog / skill).exists())

    @unittest.skipUnless(BASH, "bash is required")
    def test_shell_wrapper_resolves_a_working_python_interpreter(self) -> None:
        # select-skillset.sh must actually run the candidate it picks, not just
        # confirm one exists on PATH: Windows ships a python3 App Execution
        # Alias stub by default that resolves via `command -v` but exits
        # nonzero telling the user to install from the Microsoft Store. This
        # exercises the real wrapper end to end, the same interpreter
        # resolution Claude Code's own hooks.sh uses.
        result = subprocess.run(
            [BASH, SELECTOR_SH.as_posix(), "current", "--root", str(self.root)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "software")

    def test_current_rejects_mismatched_visible_catalogs(self) -> None:
        skill = self.research[0]
        shutil.copytree(
            self.root / ".agent" / "skillsets" / "research" / skill,
            self.root / CATALOGS[0] / skill,
        )
        result = self.invoke("current")
        self.assertEqual(result.returncode, 2)
        self.assertIn("catalogs disagree", result.stderr)


if __name__ == "__main__":
    unittest.main()
