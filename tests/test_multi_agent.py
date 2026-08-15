from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agent" / "multi_agent.py"
SPEC = importlib.util.spec_from_file_location("portable_multi_agent", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {SCRIPT}")
multi_agent = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = multi_agent
SPEC.loader.exec_module(multi_agent)

# subprocess.Popen on Windows always checks system directories (e.g. System32)
# before PATH, so a bare "bash" resolves to the WSL launcher shim whenever WSL
# is installed, regardless of PATH order. Reuse the production fix itself
# (rather than duplicating its detection logic here) so these tests exercise
# whatever bash the real launcher would actually invoke.
BASH = multi_agent.resolve_bash(["bash"])[0] if shutil.which("bash") else None


class MultiAgentTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "workspace"
        roles = root / ".agent" / "roles"
        roles.mkdir(parents=True)
        (roles / "investigator.md").write_text(
            "---\nwrite_access: false\ndefault_scope: read-only research\n---\n\n# Investigator\nRead only.\n",
            encoding="utf-8",
        )
        (roles / "implementer.md").write_text(
            "---\nwrite_access: true\ndefault_scope: assigned files\n---\n\n# Implementer\nWrite only assigned files.\n",
            encoding="utf-8",
        )
        config = {
            "schema": multi_agent.SCHEMA,
            "defaults": {
                "runtime_directory": ".agent-runtime/multi-agent",
                "heartbeat_interval_seconds": 1,
                "max_parallel_agents": 2,
            },
            "agents": {
                "test-cli": {
                    "enabled": True,
                    "command": [
                        sys.executable,
                        "-c",
                        "import pathlib,sys; print(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))",
                        "{prompt_file}",
                    ],
                    "roles": ["investigator", "implementer"],
                    "environment": {"PORTABLE_MULTI_AGENT_TEST": "yes"},
                }
            },
        }
        (root / ".agent" / "multi-agent.json").write_text(json.dumps(config), encoding="utf-8")
        return root

    def run_launcher(self, workspace: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=15,
        )

    def test_validate_and_foreground_read_only_launch_write_durable_records(self) -> None:
        workspace = self.make_workspace()
        validated = self.run_launcher(workspace, "validate")
        self.assertEqual(validated.returncode, 0, validated.stderr)

        launched = self.run_launcher(
            workspace,
            "launch",
            "--agent",
            "test-cli",
            "--role",
            "investigator",
            "--id",
            "research-task",
            "--task",
            "Find the parser regression without editing files.",
            "--scope",
            "src/parser and tests/parser",
            "--acceptance-check",
            "Return evidence-backed findings",
        )
        self.assertEqual(launched.returncode, 0, launched.stderr + launched.stdout)
        delegation = workspace / ".agent-runtime" / "multi-agent" / "research-task"
        prompt = (delegation / "prompt.md").read_text(encoding="utf-8")
        self.assertIn("Find the parser regression", prompt)
        self.assertIn("Read-only: do not edit files.", prompt)
        result = json.loads((delegation / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(result["state"], "PASSED")
        self.assertEqual(result["execution_mode"], "unbounded")
        self.assertNotIn("timed_out", result)
        self.assertTrue((delegation / "worker.stdout.log").is_file())
        status = self.run_launcher(workspace, "status", "--id", "research-task")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(json.loads(status.stdout)["state"], "PASSED")

    def test_implementer_refuses_the_main_workspace_or_its_subdirectories_without_override(self) -> None:
        workspace = self.make_workspace()
        nested = workspace / "src"
        nested.mkdir()
        for working_directory in (workspace, nested):
            launched = self.run_launcher(
                workspace,
                "launch",
                "--agent",
                "test-cli",
                "--role",
                "implementer",
                "--task",
                "Make a change",
                "--working-directory",
                str(working_directory),
            )
            self.assertEqual(launched.returncode, 2)
            self.assertIn("isolated working directory", launched.stderr)

    def test_background_launch_reaches_a_terminal_status(self) -> None:
        workspace = self.make_workspace()
        launched = self.run_launcher(
            workspace,
            "launch",
            "--agent",
            "test-cli",
            "--role",
            "investigator",
            "--id",
            "background-research",
            "--task",
            "Inspect in the background",
            "--background",
        )
        self.assertEqual(launched.returncode, 0, launched.stderr + launched.stdout)
        status_path = workspace / ".agent-runtime" / "multi-agent" / "background-research" / "status.json"
        deadline = time.monotonic() + 10
        status: dict[str, object] = {}
        while time.monotonic() < deadline:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            if status.get("state") in {"PASSED", "FAILED", "LAUNCH_FAILED"}:
                break
            time.sleep(0.05)
        self.assertEqual(status.get("state"), "PASSED")
        # The terminal worker status is persisted just before the detached
        # supervisor exits and releases its own log handles on Windows.
        time.sleep(0.2)

    def test_launcher_rejects_removed_timeout_options(self) -> None:
        workspace = self.make_workspace()
        launched = self.run_launcher(
            workspace,
            "launch",
            "--agent",
            "test-cli",
            "--role",
            "investigator",
            "--task",
            "Inspect without a deadline",
            "--expected-upper-bound-seconds",
            "1",
        )
        self.assertEqual(launched.returncode, 2)
        self.assertIn("unrecognized arguments", launched.stderr)

    def test_config_rejects_an_unknown_command_placeholder(self) -> None:
        workspace = self.make_workspace()
        config_path = workspace / ".agent" / "multi-agent.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["agents"]["test-cli"]["command"][-1] = "{unknown_value}"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        result = self.run_launcher(workspace, "validate")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported placeholder", result.stderr)

    def test_command_placeholders_expand_to_forward_slash_paths(self) -> None:
        # A worker invoked through bash (Git Bash on Windows, required for
        # Claude Code's own hook execution, or a POSIX host) reparses its argv
        # and treats a backslash as an escape character. str(Path) is
        # backslash-separated on Windows, so every path substituted into a
        # command argument must use forward slashes regardless of host OS.
        workspace = self.make_workspace()
        launched = self.run_launcher(
            workspace,
            "launch",
            "--agent",
            "test-cli",
            "--role",
            "investigator",
            "--id",
            "slash-check",
            "--task",
            "check placeholder path formatting",
        )
        self.assertEqual(launched.returncode, 0, launched.stderr + launched.stdout)
        delegation = json.loads(
            (workspace / ".agent-runtime" / "multi-agent" / "slash-check" / "delegation.json").read_text(encoding="utf-8")
        )
        prompt_file_argument = delegation["command"][-1]
        self.assertNotIn("\\", prompt_file_argument)
        self.assertTrue(prompt_file_argument.endswith("prompt.md"), prompt_file_argument)


class ShippedConfigurationTests(unittest.TestCase):
    def test_shipped_config_and_role_templates_are_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "validate"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VALID", result.stdout)

    def test_shipped_config_declares_unbounded_agent_sessions(self) -> None:
        config = json.loads((ROOT / ".agent" / "multi-agent.json").read_text(encoding="utf-8"))
        self.assertEqual(config["schema"], "portable-multi-agent/v2")
        self.assertNotIn("expected_upper_bound_seconds", config["defaults"])
        self.assertNotIn("cleanup_allowance_seconds", config["defaults"])

    def test_claude_and_codex_entries_are_disabled_and_use_the_stdin_wrapper(self) -> None:
        config = json.loads((ROOT / ".agent" / "multi-agent.json").read_text(encoding="utf-8"))
        for name, worker in (("claude-cli", "claude"), ("codex-cli", "codex")):
            agent = config["agents"][name]
            self.assertFalse(agent["enabled"], f"{name} must ship disabled until a repository owner reviews it")
            self.assertIn("{workspace}/.agent/pipe-prompt-file.sh", agent["command"])
            self.assertIn(worker, agent["command"])
            self.assertNotIn("{prompt_file}", agent["command"][:2], "the worker CLI itself must not receive a raw path argument")


class ResolveBashTests(unittest.TestCase):
    """subprocess.Popen on Windows always checks system directories before
    PATH, so a bare "bash" resolves to the WSL launcher shim whenever WSL is
    installed, no matter how PATH is configured. resolve_bash prefers a
    located Git for Windows bash instead."""

    def test_leaves_non_bash_commands_untouched(self) -> None:
        self.assertEqual(multi_agent.resolve_bash(["python", "script.py"]), ["python", "script.py"])

    def test_is_a_noop_off_windows(self) -> None:
        with mock.patch.object(multi_agent.os, "name", "posix"):
            self.assertEqual(multi_agent.resolve_bash(["bash", "-c", "x"]), ["bash", "-c", "x"])

    def test_falls_back_to_literal_bash_when_none_is_located(self) -> None:
        with mock.patch.object(multi_agent.os, "name", "nt"), mock.patch.dict(
            multi_agent.os.environ, {"ProgramFiles": "", "ProgramW6432": "", "LocalAppData": ""}
        ):
            self.assertEqual(multi_agent.resolve_bash(["bash", "-c", "x"]), ["bash", "-c", "x"])

    def test_prefers_a_located_git_bash_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            local_app_data = Path(temp) / "LocalAppData"
            git_bash = local_app_data / "Programs" / "Git" / "bin" / "bash.exe"
            git_bash.parent.mkdir(parents=True)
            git_bash.write_text("", encoding="utf-8")
            with mock.patch.object(multi_agent.os, "name", "nt"), mock.patch.dict(
                multi_agent.os.environ,
                {"ProgramFiles": "", "ProgramW6432": "", "LocalAppData": str(local_app_data)},
            ):
                resolved = multi_agent.resolve_bash(["bash", "-c", "echo hi"])
        self.assertEqual(resolved, [str(git_bash), "-c", "echo hi"])


@unittest.skipUnless(BASH, "bash is required")
class PipePromptFileShellTests(unittest.TestCase):
    """Exercises .agent/pipe-prompt-file.sh, the wrapper that bridges the
    launcher's file-path prompt delivery to a worker CLI that reads its
    prompt from stdin instead (claude -p, codex exec)."""

    SCRIPT = ROOT / ".agent" / "pipe-prompt-file.sh"

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.prompt_file = Path(self.temp.name) / "prompt.md"
        self.prompt_file.write_text("hello from the prompt file\n", encoding="utf-8")

    def run_wrapper(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [BASH, self.SCRIPT.as_posix(), *arguments],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_pipes_prompt_file_content_to_the_downstream_command(self) -> None:
        result = self.run_wrapper(self.prompt_file.as_posix(), "--", "cat")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "hello from the prompt file\n")

    def test_requires_the_separator(self) -> None:
        result = self.run_wrapper(self.prompt_file.as_posix(), "cat")
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage:", result.stderr)

    def test_reports_a_missing_prompt_file(self) -> None:
        missing = (Path(self.temp.name) / "missing.md").as_posix()
        result = self.run_wrapper(missing, "--", "cat")
        self.assertEqual(result.returncode, 2)
        self.assertIn("not found", result.stderr)

    def test_propagates_the_downstream_exit_code(self) -> None:
        result = self.run_wrapper(self.prompt_file.as_posix(), "--", BASH, "-c", "exit 7")
        self.assertEqual(result.returncode, 7)


@unittest.skipUnless(os.name == "nt", "PowerShell implementation tests run on Windows")
class PipePromptFileWindowsTests(unittest.TestCase):
    """Exercises the PowerShell twin of pipe-prompt-file.sh."""

    SCRIPT = ROOT / ".agent" / "pipe-prompt-file.ps1"

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.prompt_file = Path(self.temp.name) / "prompt.md"
        self.prompt_file.write_text("hello from the prompt file\n", encoding="utf-8")

    def run_wrapper(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(self.SCRIPT),
                *arguments,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_pipes_prompt_file_content_to_the_downstream_command(self) -> None:
        result = self.run_wrapper(str(self.prompt_file), "cmd.exe", "/d", "/c", "more")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hello from the prompt file", result.stdout)

    def test_reports_a_missing_prompt_file(self) -> None:
        missing = str(Path(self.temp.name) / "missing.md")
        result = self.run_wrapper(missing, "cmd.exe", "/d", "/c", "more")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)

    def test_a_downstream_flag_that_looks_like_a_named_parameter_passes_through(self) -> None:
        # claude's -p and similar single-letter worker flags must reach the
        # worker untouched rather than being reinterpreted as an attempt to
        # set one of this script's own parameters by prefix. cmd's echo
        # prints its arguments back literally regardless of what they look
        # like, so it proves -p arrived unmangled without depending on any
        # particular downstream program's own flag semantics.
        result = self.run_wrapper(str(self.prompt_file), "cmd.exe", "/d", "/c", "echo", "-p", "marker")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-p marker", result.stdout)


if __name__ == "__main__":
    unittest.main()
