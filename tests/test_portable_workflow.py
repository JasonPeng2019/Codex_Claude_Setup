from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / ".agent"
HOOK = AGENT / "hooks.ps1"
HOOKS_SH = AGENT / "hooks.sh"
BOUNDED = AGENT / "run-bounded.ps1"
BOUNDED_SH = AGENT / "run-bounded.sh"
STOP_HOOK = AGENT / "stop-verify.ps1"
STOP_HOOK_SH = AGENT / "stop-verify.sh"
SHARED_VERIFICATION_SNAPSHOT = Path(".agent-runtime/stop-verify/verification-snapshot.json")
SCRIPT_POLICY_ADAPTER = AGENT / "bounded-script-adapter.py"
# A bare "bash" can resolve to C:\Windows\System32\bash.exe (the WSL launcher
# shim) instead of Git for Windows' bash when both are installed and WSL's
# System32 entry precedes Git's on PATH; that shim does not understand a plain
# Windows-drive path. Prefer Git Bash explicitly, and skip these direct-hook
# tests when it is not installed. Native Unix-like tests always use the host's
# Bash—never WSL.
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


def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, **kwargs)


@unittest.skipUnless(os.name == "nt", "PowerShell implementation tests run on Windows")
class PowerShellHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable workflow ")
        self.repo = Path(self.temp.name)
        result = run(["git", "init", "--quiet", str(self.repo)])
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(
        self,
        event: str,
        command: str | None = None,
        *,
        hook: Path = HOOK,
        session_id: str | None = "portable-workflow-test-session",
    ) -> dict[str, object] | None:
        payload: dict[str, object] = {
            "cwd": str(self.repo),
            "hook_event_name": {
                "session-start": "SessionStart",
                "pre-tool-use": "PreToolUse",
                "pre-compact": "PreCompact",
                "stop": "Stop",
            }[event],
        }
        if session_id is not None:
            payload["session_id"] = session_id
        if command is not None:
            payload["tool_input"] = {"command": command}
        result = run(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(hook),
                event,
            ],
            input=json.dumps(payload),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        return json.loads(output) if output else None

    def enable_stop_verification(self, command: list[str], full_command: list[str] | None = None) -> None:
        agent = self.repo / ".agent"
        agent.mkdir()
        shutil.copy2(BOUNDED, agent / "run-bounded.ps1")
        (agent / "stop-verify.json").write_text(
            json.dumps(
                {
                    "enabled": True,
                    "source_extensions": [".py"],
                    "commands": [command],
                    "full_commands": [
                        full_command
                        or ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "exit 0"]
                    ],
                    "expected_upper_bound_seconds": 5,
                    "cleanup_allowance_seconds": 2,
                    "heartbeat_interval_seconds": 1,
                    "timeout_basis": "portable standard-library regression test",
                }
            ),
            encoding="utf-8",
        )

    def enable_script_policy(self) -> None:
        agent = self.repo / ".agent"
        agent.mkdir(exist_ok=True)
        for source in (
            SCRIPT_POLICY_ADAPTER,
            AGENT / "bounded-launchers.json",
            AGENT / "bounded-exclusions.gitignore",
        ):
            shutil.copy2(source, agent / source.name)
        (agent / "bounded-script-policy.json").write_text(
            json.dumps({"schema": "portable-bounded-script-policy/v1", "enabled": True}),
            encoding="utf-8",
        )

    def start_stop_session(self) -> None:
        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK))

    def assert_denied(self, command: str, reason_fragment: str) -> None:
        output = self.invoke("pre-tool-use", command)
        self.assertIsNotNone(output)
        specific = output["hookSpecificOutput"]  # type: ignore[index]
        self.assertEqual(specific["permissionDecision"], "deny")  # type: ignore[index]
        self.assertIn(reason_fragment, specific["permissionDecisionReason"])  # type: ignore[index]

    def test_session_start_surfaces_handoff_without_scanning_repository(self) -> None:
        (self.repo / "HANDOFF.md").write_text("# Handoff\n\nNext: run the focused test.\n", encoding="utf-8")
        output = self.invoke("session-start")
        context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
        self.assertIn("HANDOFF.md exists", context)
        self.assertIn("run the focused test", context)
        self.assertLess(len(context), 4000)

    def test_cli_workers_remain_unbounded_when_listed_by_mistake(self) -> None:
        self.enable_script_policy()
        agent = self.repo / ".agent"
        (agent / "bounded-commands.txt").write_text("codex exec\nclaude -p\n", encoding="utf-8")
        self.assertIsNone(self.invoke("pre-tool-use", 'codex exec "review this diff"'))
        self.assertIsNone(self.invoke("pre-tool-use", 'claude -p "review this diff"'))

    def test_cli_worker_cannot_be_wrapped_by_the_bounded_launcher(self) -> None:
        command = (
            "& .agent/run-bounded.ps1 -Command 'codex exec \"review\"' "
            "-ExpectedUpperBoundSeconds 60 -CleanupAllowanceSeconds 10 -TimeoutBasis measured"
        )
        self.assert_denied(command, "must remain unbounded")

    def test_configured_bounded_command_uses_a_literal_fragment(self) -> None:
        agent = self.repo / ".agent"
        agent.mkdir()
        (agent / "bounded-commands.txt").write_text("npm run e2e\n", encoding="utf-8")
        self.assert_denied("npm run e2e -- --headed", "run-bounded.ps1")
        self.assertIsNone(self.invoke("pre-tool-use", "npm run unit"))

    def test_optional_script_policy_is_explicit_and_honors_narrow_exclusions(self) -> None:
        self.enable_script_policy()
        self.assert_denied("python tools/check.py", "bounded script policy")
        self.assert_denied("python -m pytest", "bounded script policy")
        self.assert_denied('python -c "print(1)"', "bounded script policy")
        self.assert_denied('sh -c "echo guarded"', "bounded script policy")
        exclusions = self.repo / ".agent" / "bounded-exclusions.gitignore"
        exclusions.write_text(exclusions.read_text(encoding="utf-8") + "\ntools/direct-setup.py\n", encoding="utf-8")
        self.assertIsNone(self.invoke("pre-tool-use", "python tools/direct-setup.py"))
        self.assertIsNone(
            self.invoke(
                "pre-tool-use",
                "& .agent/run-bounded.ps1 -Command 'python tools/check.py' "
                "-ExpectedUpperBoundSeconds 60 -CleanupAllowanceSeconds 10 -TimeoutBasis measured",
            )
        )

    def test_repository_root_delete_is_denied_but_narrow_delete_is_allowed(self) -> None:
        self.assert_denied(
            f"Remove-Item -LiteralPath '{self.repo}' -Recurse -Force",
            "recursive deletion",
        )
        narrow = self.repo / "generated" / "one-file.txt"
        self.assertIsNone(
            self.invoke("pre-tool-use", f"Remove-Item -LiteralPath '{narrow}' -Recurse -Force")
        )

    def test_direct_git_mutation_is_denied(self) -> None:
        self.assert_denied("Remove-Item -Recurse -Force .git", ".git internals")

    def test_malformed_input_fails_open_with_warning(self) -> None:
        result = run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HOOK), "pre-tool-use"],
            input="not json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertIn("malformed JSON", output["systemMessage"])

    def test_stop_verification_is_dormant_without_opt_in_config(self) -> None:
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))

    def test_stop_ignores_documentation_only_session_changes(self) -> None:
        self.enable_stop_verification(
            [
                "cmd.exe",
                "/d",
                "/c",
                "type",
                "{files}",
            ]
        )
        self.start_stop_session()
        (self.repo / "README.md").write_text("Documentation only.\n", encoding="utf-8")
        docs = self.repo / "docs"
        docs.mkdir()
        (docs / "example.py").write_text("# documentation snippet\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], [])

    def test_stop_verifies_only_new_source_changes_and_does_not_repeat_success(self) -> None:
        self.enable_stop_verification(
            [
                "cmd.exe",
                "/d",
                "/c",
                "type",
                "{files}",
            ]
        )
        self.start_stop_session()
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        legacy_hash_state = state_dir / ("b" * 64 + ".json")
        legacy_hash_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        legacy_provider_state = state_dir / "provider-old.json"
        legacy_provider_state.write_text(
            json.dumps({"schema": "portable-stop-verification-snapshot/v1", "baseline": [], "last_verified": []}),
            encoding="utf-8",
        )
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        source = self.repo / "app.py"
        source.write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        state_path = self.repo / SHARED_VERIFICATION_SNAPSHOT
        first = json.loads(state_path.read_text(encoding="utf-8"))["last_verified"]
        self.assertEqual([entry["path"] for entry in first], ["app.py"])
        self.assertFalse(legacy_hash_state.exists())
        self.assertFalse(legacy_provider_state.exists())
        self.assertTrue((state_dir / "run-kept.json").is_file())
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        self.assertEqual(json.loads(state_path.read_text(encoding="utf-8"))["last_verified"], first)
        source.write_text("value = 2\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        second = json.loads(state_path.read_text(encoding="utf-8"))["last_verified"]
        self.assertNotEqual(second, first)

    def test_stop_does_not_claim_preexisting_dirty_source_as_session_work(self) -> None:
        self.enable_stop_verification(
            [
                "cmd.exe",
                "/d",
                "/c",
                "type",
                "{files}",
            ]
        )
        (self.repo / "preexisting.py").write_text("old = True\n", encoding="utf-8")
        self.start_stop_session()
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], [])

    def test_session_start_replaces_the_shared_provider_neutral_snapshot(self) -> None:
        self.enable_stop_verification(["cmd.exe", "/d", "/c", "type", "{files}"])
        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK, session_id="older-session"))
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        legacy_state = state_dir / ("a" * 64 + ".json")
        legacy_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        (self.repo / "preexisting.py").write_text("old = True\n", encoding="utf-8")

        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK, session_id="current-session"))

        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        state = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(set(state), {"schema", "baseline", "last_verified"})
        self.assertEqual(state["schema"], "portable-stop-verification-snapshot/v1")
        self.assertIn("preexisting.py", [entry["path"] for entry in state["baseline"]])
        self.assertFalse(any(entry["path"].startswith(".agent-runtime/stop-verify/") for entry in state["baseline"]))
        self.assertEqual(state["last_verified"], [])
        self.assertFalse(legacy_state.exists())
        self.assertEqual([path.name for path in state_dir.glob("*snapshot*.json")], [snapshot.name])
        self.assertTrue((state_dir / "run-kept.json").is_file())

    def test_snapshot_is_shared_across_provider_session_ids(self) -> None:
        self.enable_stop_verification(["cmd.exe", "/d", "/c", "type", "{files}"])
        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK, session_id="codex-session"))
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")

        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK, session_id="claude-session"))

        state = json.loads((self.repo / SHARED_VERIFICATION_SNAPSHOT).read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in state["last_verified"]], ["app.py"])

    @unittest.skipUnless(BASH and shutil.which("jq"), "Git Bash and jq are required")
    def test_powershell_and_bash_share_the_same_snapshot(self) -> None:
        self.enable_stop_verification(
            ["git", "status", "--short", "--", "{files}"],
            ["git", "status", "--short"],
        )
        shutil.copy2(BOUNDED_SH, self.repo / ".agent" / "run-bounded.sh")
        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK, session_id="codex-session"))
        source = self.repo / "app.py"
        source.write_text("value = 1\n", encoding="utf-8")
        payload = {"cwd": str(self.repo), "hook_event_name": "Stop", "session_id": "claude-session"}

        bash_result = run([BASH, STOP_HOOK_SH.as_posix(), "stop"], input=json.dumps(payload))

        self.assertEqual(bash_result.returncode, 0, bash_result.stderr)
        self.assertEqual(bash_result.stdout.strip(), "")
        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        first = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in first["last_verified"]], ["app.py"])
        source.write_text("value = 2\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK, session_id="future-provider-session"))
        second = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertNotEqual(second["last_verified"], first["last_verified"])

    def test_stop_runs_full_verification_when_the_durable_snapshot_is_unavailable(self) -> None:
        self.enable_stop_verification(
            ["cmd.exe", "/d", "/c", "type", "{files}"],
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Add-Content -LiteralPath fallback-full.txt -Value ran",
            ],
        )
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        state_dir.mkdir(parents=True)
        legacy_state = state_dir / ("c" * 64 + ".json")
        legacy_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        output = self.invoke("stop", hook=STOP_HOOK)
        self.assertIsNotNone(output)
        self.assertIn("full verification fallback", output["systemMessage"].lower())  # type: ignore[index]
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").strip(), "ran")
        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        state = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(state["schema"], "portable-stop-verification-snapshot/v1")
        self.assertFalse(legacy_state.exists())
        self.assertTrue((state_dir / "run-kept.json").is_file())

        (self.repo / "next.py").write_text("value = 2\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK))
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").splitlines(), ["ran"])
        updated = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in updated["last_verified"]], ["next.py"])

    def test_stop_rejects_a_noncanonical_shared_snapshot_shape(self) -> None:
        self.enable_stop_verification(
            ["cmd.exe", "/d", "/c", "type", "{files}"],
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "Set-Content -LiteralPath fallback-full.txt -Value ran",
            ],
        )
        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(
            json.dumps(
                {
                    "schema": "portable-stop-verification-snapshot/v1",
                    "baseline": [
                        {"path": "app.py", "kind": "present", "hash": "0" * 64, "provider": "codex"}
                    ],
                    "last_verified": [],
                }
            ),
            encoding="utf-8",
        )

        output = self.invoke("stop", hook=STOP_HOOK, session_id="any-provider")

        self.assertIsNotNone(output)
        self.assertIn("provider-neutral schema", output["systemMessage"])  # type: ignore[index]
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").strip(), "ran")
        self.assertEqual(
            json.loads(snapshot.read_text(encoding="utf-8"))["schema"],
            "portable-stop-verification-snapshot/v1",
        )

    def test_stop_blocks_when_full_verification_fallback_fails(self) -> None:
        self.enable_stop_verification(
            ["cmd.exe", "/d", "/c", "type", "{files}"],
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "exit 9"],
        )
        output = self.invoke("stop", hook=STOP_HOOK)
        self.assertIsNotNone(output)
        self.assertFalse(output["continue"])  # type: ignore[index]
        self.assertIn("Full verification fallback failed", output["stopReason"])  # type: ignore[index]
        self.assertFalse((self.repo / SHARED_VERIFICATION_SNAPSHOT).exists())

    def test_stop_keeps_failure_pending(self) -> None:
        self.enable_stop_verification(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                "exit 7",
                "{files}",
            ]
        )
        self.start_stop_session()
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        output = self.invoke("stop", hook=STOP_HOOK)
        self.assertIsNotNone(output)
        self.assertFalse(output["continue"])  # type: ignore[index]
        self.assertIn("verification failed", output["stopReason"])  # type: ignore[index]
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], [])

    def test_snapshot_does_not_require_a_provider_session_id(self) -> None:
        self.enable_stop_verification(
            ["cmd.exe", "/d", "/c", "type", "{files}"]
        )
        self.assertIsNone(self.invoke("session-start", hook=STOP_HOOK, session_id=None))
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", hook=STOP_HOOK, session_id=None))
        state = json.loads((self.repo / SHARED_VERIFICATION_SNAPSHOT).read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in state["last_verified"]], ["app.py"])


@unittest.skipUnless(BASH and shutil.which("jq"), "bash and jq are required")
class BashHookTests(unittest.TestCase):
    """Exercises .agent/hooks.sh directly through bash, the same interpreter Claude
    Code uses to run project hooks on both Windows (Git Bash) and Unix-like hosts."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable workflow bash ")
        self.repo = Path(self.temp.name)
        result = run(["git", "init", "--quiet", str(self.repo)])
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, event: str, command: str | None = None) -> dict[str, object] | None:
        payload: dict[str, object] = {
            "cwd": str(self.repo),
            "hook_event_name": {
                "session-start": "SessionStart",
                "pre-tool-use": "PreToolUse",
                "pre-compact": "PreCompact",
            }[event],
        }
        if command is not None:
            payload["tool_input"] = {"command": command}
        # bash.exe (MSYS2/Git for Windows) re-tokenizes its raw argv and treats a
        # backslash as an escape character, so a Windows-style path passed as an
        # argv element (as opposed to expanded by bash itself from a shell string,
        # e.g. Claude Code's own hook command invocation) must use forward slashes.
        result = run([BASH, HOOKS_SH.as_posix(), event], input=json.dumps(payload))
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        return json.loads(output) if output else None

    def assert_denied(self, command: str, reason_fragment: str) -> None:
        output = self.invoke("pre-tool-use", command)
        self.assertIsNotNone(output)
        specific = output["hookSpecificOutput"]  # type: ignore[index]
        self.assertEqual(specific["permissionDecision"], "deny")  # type: ignore[index]
        self.assertIn(reason_fragment, specific["permissionDecisionReason"])  # type: ignore[index]

    def test_session_start_surfaces_handoff_without_scanning_repository(self) -> None:
        (self.repo / "HANDOFF.md").write_text("# Handoff\n\nNext: run the focused test.\n", encoding="utf-8")
        output = self.invoke("session-start")
        context = output["hookSpecificOutput"]["additionalContext"]  # type: ignore[index]
        self.assertIn("HANDOFF.md exists", context)
        self.assertIn("run the focused test", context)

    def test_cli_workers_remain_unbounded_when_listed_by_mistake(self) -> None:
        self.enable_script_policy()
        agent = self.repo / ".agent"
        (agent / "bounded-commands.txt").write_text("codex exec\nclaude -p\n", encoding="utf-8")
        self.assertIsNone(self.invoke("pre-tool-use", 'codex exec "review this diff"'))
        self.assertIsNone(self.invoke("pre-tool-use", 'claude -p "review this diff"'))

    def test_cli_worker_cannot_be_wrapped_by_the_bounded_launcher(self) -> None:
        command = (
            "bash .agent/run-bounded.sh --command 'codex exec \"review\"' "
            "--expected-upper-bound-seconds 60 --cleanup-allowance-seconds 10 --timeout-basis measured"
        )
        self.assert_denied(command, "must remain unbounded")

    def test_configured_bounded_command_uses_a_literal_fragment(self) -> None:
        agent = self.repo / ".agent"
        agent.mkdir()
        (agent / "bounded-commands.txt").write_text("npm run e2e\n", encoding="utf-8")
        self.assert_denied("npm run e2e -- --headed", "run-bounded.sh")
        self.assertIsNone(self.invoke("pre-tool-use", "npm run unit"))

    def enable_script_policy(self) -> None:
        agent = self.repo / ".agent"
        agent.mkdir(exist_ok=True)
        for source in (
            SCRIPT_POLICY_ADAPTER,
            AGENT / "bounded-launchers.json",
            AGENT / "bounded-exclusions.gitignore",
        ):
            shutil.copy2(source, agent / source.name)
        (agent / "bounded-script-policy.json").write_text(
            json.dumps({"schema": "portable-bounded-script-policy/v1", "enabled": True}),
            encoding="utf-8",
        )

    def test_optional_script_policy_is_explicit_and_honors_narrow_exclusions(self) -> None:
        # This exercises bounded-script-adapter.py through hooks.sh's own
        # python-resolution logic, not just the adapter in isolation: a
        # Windows machine with the default python3 App Execution Alias stub
        # present (command -v succeeds, invoking it does not) must still find
        # a working interpreter by falling through to "python".
        self.enable_script_policy()
        self.assert_denied("python tools/check.py", "bounded script policy")
        self.assert_denied("python -m pytest", "bounded script policy")
        self.assert_denied('python -c "print(1)"', "bounded script policy")
        self.assert_denied('sh -c "echo guarded"', "bounded script policy")
        exclusions = self.repo / ".agent" / "bounded-exclusions.gitignore"
        exclusions.write_text(exclusions.read_text(encoding="utf-8") + "\ntools/direct-setup.py\n", encoding="utf-8")
        self.assertIsNone(self.invoke("pre-tool-use", "python tools/direct-setup.py"))
        self.assertIsNone(
            self.invoke(
                "pre-tool-use",
                "bash .agent/run-bounded.sh --command 'python tools/check.py' "
                "--expected-upper-bound-seconds 60 --cleanup-allowance-seconds 10 --timeout-basis measured",
            )
        )

    def test_repository_root_delete_is_denied_but_narrow_delete_is_allowed(self) -> None:
        # hooks.sh matches command text against the forward-slash path git itself
        # reports for $root, so the command text must use that same form here.
        self.assert_denied(f"rm -rf '{self.repo.as_posix()}'", "recursive deletion")
        narrow = self.repo / "generated" / "one-file.txt"
        self.assertIsNone(self.invoke("pre-tool-use", f"rm -rf '{narrow.as_posix()}'"))

    def test_direct_git_mutation_is_denied(self) -> None:
        self.assert_denied("rm -rf .git", ".git internals")

    def test_malformed_input_fails_open_with_warning(self) -> None:
        result = run([BASH, HOOKS_SH.as_posix(), "pre-tool-use"], input="not json")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertIn("malformed JSON", output["systemMessage"])


@unittest.skipUnless(BASH and shutil.which("jq"), "bash and jq are required")
class BashStopVerificationTests(unittest.TestCase):
    """Exercises .agent/stop-verify.sh directly through bash, the same
    interpreter Claude Code uses to run project hooks on both Windows (Git
    Bash) and Unix-like hosts. Mirrors PowerShellHookTests' stop-verify
    coverage so the full_commands fallback behavior is verified on a machine
    that has bash and jq but no WSL, exactly the common Claude-on-Windows case."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable workflow stop-verify ")
        self.repo = Path(self.temp.name)
        result = run(["git", "init", "--quiet", str(self.repo)])
        self.assertEqual(result.returncode, 0, result.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, event: str, *, session_id: str | None = "portable-workflow-test-session") -> dict[str, object] | None:
        payload: dict[str, object] = {
            "cwd": str(self.repo),
            "hook_event_name": "SessionStart" if event == "session-start" else "Stop",
        }
        if session_id is not None:
            payload["session_id"] = session_id
        result = run([BASH, STOP_HOOK_SH.as_posix(), event], input=json.dumps(payload))
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        return json.loads(output) if output else None

    def enable_stop_verification(self, command: list[str], full_command: list[str] | None = None) -> None:
        agent = self.repo / ".agent"
        agent.mkdir(exist_ok=True)
        shutil.copy2(BOUNDED_SH, agent / "run-bounded.sh")
        (agent / "stop-verify.json").write_text(
            json.dumps(
                {
                    "enabled": True,
                    "source_extensions": [".py"],
                    "commands": [command],
                    "full_commands": [full_command or ["true"]],
                    "expected_upper_bound_seconds": 5,
                    "cleanup_allowance_seconds": 2,
                    "heartbeat_interval_seconds": 1,
                    "timeout_basis": "portable standard-library regression test",
                }
            ),
            encoding="utf-8",
        )

    def start_stop_session(self) -> None:
        self.assertIsNone(self.invoke("session-start"))

    def test_stop_verification_is_dormant_without_opt_in_config(self) -> None:
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop"))

    def test_stop_verifies_only_new_source_changes_and_does_not_repeat_success(self) -> None:
        self.enable_stop_verification(["cat", "{files}"])
        self.start_stop_session()
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        legacy_hash_state = state_dir / ("b" * 64 + ".json")
        legacy_hash_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        legacy_provider_state = state_dir / "provider-old.json"
        legacy_provider_state.write_text(
            json.dumps({"schema": "portable-stop-verification-snapshot/v1", "baseline": [], "last_verified": []}),
            encoding="utf-8",
        )
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        source = self.repo / "app.py"
        source.write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop"))
        state_path = self.repo / SHARED_VERIFICATION_SNAPSHOT
        first = json.loads(state_path.read_text(encoding="utf-8"))["last_verified"]
        self.assertEqual([entry["path"] for entry in first], ["app.py"])
        self.assertFalse(legacy_hash_state.exists())
        self.assertFalse(legacy_provider_state.exists())
        self.assertTrue((state_dir / "run-kept.json").is_file())
        self.assertIsNone(self.invoke("stop"))
        self.assertEqual(json.loads(state_path.read_text(encoding="utf-8"))["last_verified"], first)
        source.write_text("value = 2\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop"))
        second = json.loads(state_path.read_text(encoding="utf-8"))["last_verified"]
        self.assertNotEqual(second, first)

    def test_stop_does_not_claim_preexisting_dirty_source_as_session_work(self) -> None:
        self.enable_stop_verification(["cat", "{files}"])
        (self.repo / "preexisting.py").write_text("old = True\n", encoding="utf-8")
        self.start_stop_session()
        self.assertIsNone(self.invoke("stop"))
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], [])

    def test_session_start_replaces_the_shared_provider_neutral_snapshot(self) -> None:
        self.enable_stop_verification(["cat", "{files}"])
        self.assertIsNone(self.invoke("session-start", session_id="older-session"))
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        legacy_state = state_dir / ("a" * 64 + ".json")
        legacy_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        (self.repo / "preexisting.py").write_text("old = True\n", encoding="utf-8")

        self.assertIsNone(self.invoke("session-start", session_id="current-session"))

        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        state = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(set(state), {"schema", "baseline", "last_verified"})
        self.assertEqual(state["schema"], "portable-stop-verification-snapshot/v1")
        self.assertIn("preexisting.py", [entry["path"] for entry in state["baseline"]])
        self.assertFalse(any(entry["path"].startswith(".agent-runtime/stop-verify/") for entry in state["baseline"]))
        self.assertEqual(state["last_verified"], [])
        self.assertFalse(legacy_state.exists())
        self.assertEqual([path.name for path in state_dir.glob("*snapshot*.json")], [snapshot.name])
        self.assertTrue((state_dir / "run-kept.json").is_file())

    def test_snapshot_is_shared_across_provider_session_ids(self) -> None:
        self.enable_stop_verification(["cat", "{files}"])
        self.assertIsNone(self.invoke("session-start", session_id="claude-session"))
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")

        self.assertIsNone(self.invoke("stop", session_id="codex-session"))

        state = json.loads((self.repo / SHARED_VERIFICATION_SNAPSHOT).read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in state["last_verified"]], ["app.py"])

    def test_stop_runs_full_verification_when_the_durable_snapshot_is_unavailable(self) -> None:
        self.enable_stop_verification(
            ["cat", "{files}"],
            ["bash", "-c", "echo ran >> fallback-full.txt"],
        )
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        state_dir = self.repo / ".agent-runtime" / "stop-verify"
        state_dir.mkdir(parents=True)
        legacy_state = state_dir / ("c" * 64 + ".json")
        legacy_state.write_text('{"schema":"portable-stop-verify-v1"}', encoding="utf-8")
        (state_dir / "run-kept.json").write_text('{"result":"kept"}', encoding="utf-8")
        output = self.invoke("stop")
        self.assertIsNotNone(output)
        self.assertIn("full verification fallback", output["systemMessage"].lower())  # type: ignore[index]
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").strip(), "ran")
        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        state = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual(state["schema"], "portable-stop-verification-snapshot/v1")
        self.assertFalse(legacy_state.exists())
        self.assertTrue((state_dir / "run-kept.json").is_file())

        (self.repo / "next.py").write_text("value = 2\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop"))
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").splitlines(), ["ran"])
        updated = json.loads(snapshot.read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in updated["last_verified"]], ["next.py"])

    def test_stop_rejects_a_noncanonical_shared_snapshot_shape(self) -> None:
        self.enable_stop_verification(
            ["cat", "{files}"],
            ["bash", "-c", "echo ran > fallback-full.txt"],
        )
        snapshot = self.repo / SHARED_VERIFICATION_SNAPSHOT
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(
            json.dumps(
                {
                    "schema": "portable-stop-verification-snapshot/v1",
                    "baseline": [
                        {"path": "app.py", "kind": "present", "hash": "0" * 64, "provider": "claude"}
                    ],
                    "last_verified": [],
                }
            ),
            encoding="utf-8",
        )

        output = self.invoke("stop", session_id="any-provider")

        self.assertIsNotNone(output)
        self.assertIn("provider-neutral schema", output["systemMessage"])  # type: ignore[index]
        self.assertEqual((self.repo / "fallback-full.txt").read_text(encoding="utf-8").strip(), "ran")
        self.assertEqual(
            json.loads(snapshot.read_text(encoding="utf-8"))["schema"],
            "portable-stop-verification-snapshot/v1",
        )

    def test_stop_blocks_when_full_verification_fallback_fails(self) -> None:
        self.enable_stop_verification(["cat", "{files}"], ["false"])
        output = self.invoke("stop")
        self.assertIsNotNone(output)
        self.assertFalse(output["continue"])  # type: ignore[index]
        self.assertIn("Full verification fallback failed", output["stopReason"])  # type: ignore[index]
        self.assertFalse((self.repo / SHARED_VERIFICATION_SNAPSHOT).exists())

    def test_stop_keeps_failure_pending(self) -> None:
        self.enable_stop_verification(["false", "{files}"])
        self.start_stop_session()
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        output = self.invoke("stop")
        self.assertIsNotNone(output)
        self.assertFalse(output["continue"])  # type: ignore[index]
        self.assertIn("verification failed", output["stopReason"])  # type: ignore[index]
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], [])

    def test_snapshot_does_not_require_a_provider_session_id(self) -> None:
        self.enable_stop_verification(["cat", "{files}"])
        self.assertIsNone(self.invoke("session-start", session_id=None))
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop", session_id=None))
        state = json.loads((self.repo / SHARED_VERIFICATION_SNAPSHOT).read_text(encoding="utf-8"))
        self.assertEqual([entry["path"] for entry in state["last_verified"]], ["app.py"])


@unittest.skipUnless(os.name == "nt", "PowerShell implementation tests run on Windows")
class PowerShellBoundedRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bounded runner space ")
        self.workdir = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, command: str, name: str, expected: int = 5) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result_path = self.workdir / f"{name}.json"
        result = run(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(BOUNDED),
                "-Command",
                command,
                "-WorkingDirectory",
                str(self.workdir),
                "-ExpectedUpperBoundSeconds",
                str(expected),
                "-CleanupAllowanceSeconds",
                "2",
                "-HeartbeatIntervalSeconds",
                "1",
                "-TimeoutBasis",
                "standard-library regression test",
                "-ResultPath",
                str(result_path),
            ],
            timeout=20,
        )
        self.assertTrue(result_path.is_file(), result.stdout + result.stderr)
        return result, json.loads(result_path.read_text(encoding="utf-8"))

    def test_success_captures_output_and_returns_zero(self) -> None:
        result, record = self.invoke("Write-Output 'hello bounded world'; exit 0", "pass")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(record["status"], "PASSED")
        self.assertEqual(record["exit_code"], 0)
        stdout = Path(str(record["stdout_path"])).read_text(encoding="utf-8")
        self.assertIn("hello bounded world", stdout)
        self.assertIn("RUNNING", result.stdout)

    def test_failure_propagates_child_exit_code(self) -> None:
        result, record = self.invoke("Write-Error 'expected failure'; exit 7", "fail")
        self.assertEqual(result.returncode, 7, result.stdout + result.stderr)
        self.assertEqual(record["status"], "FAILED")
        self.assertEqual(record["exit_code"], 7)

    def test_timeout_returns_124_and_cleans_process_tree(self) -> None:
        child = (
            "Start-Process -WindowStyle Hidden powershell.exe "
            "-ArgumentList '-NoProfile','-Command','Start-Sleep -Seconds 30'; "
            "Start-Sleep -Seconds 30"
        )
        result, record = self.invoke(child, "timeout", expected=1)
        self.assertEqual(result.returncode, 124, result.stdout + result.stderr)
        self.assertEqual(record["status"], "TIMED_OUT")
        self.assertEqual(record["exit_code"], 124)
        self.assertTrue(record["cleanup_verified"])

    def test_explicit_maximum_must_match_the_computed_lifetime(self) -> None:
        result = run(
            [
                "powershell.exe",
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(BOUNDED),
                "-Command",
                "exit 0",
                "-WorkingDirectory",
                str(self.workdir),
                "-ExpectedUpperBoundSeconds",
                "20",
                "-CleanupAllowanceSeconds",
                "2",
                "-MaximumLifetimeSeconds",
                "21",
                "-TimeoutBasis",
                "regression test",
            ]
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must equal", result.stderr)


@unittest.skipUnless(os.name != "nt" and BASH, "native Unix-like Bash is unavailable")
class UnixBoundedRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable bounded shell ")
        self.workdir = Path(self.temp.name)
        self.runner = BOUNDED_SH

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, command: str, name: str, expected: int = 5) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        result_path = self.workdir / f"{name}.json"
        result = run(
            [
                BASH,
                str(self.runner),
                "--command",
                command,
                "--working-directory",
                str(self.workdir),
                "--expected-upper-bound-seconds",
                str(expected),
                "--cleanup-allowance-seconds",
                "2",
                "--heartbeat-interval-seconds",
                "1",
                "--timeout-basis",
                "native Unix-like regression test",
                "--result-path",
                str(result_path),
            ],
            timeout=20,
        )
        self.assertTrue(result_path.is_file(), result.stdout + result.stderr)
        return result, json.loads(result_path.read_text(encoding="utf-8"))

    def test_success_and_timeout_are_bounded_on_unix(self) -> None:
        success, success_record = self.invoke("printf 'hello bounded world\\n'", "success")
        self.assertEqual(success.returncode, 0, success.stdout + success.stderr)
        self.assertEqual(success_record["status"], "PASSED")
        self.assertIn("RUNNING", success.stdout)
        timeout, timeout_record = self.invoke("sleep 30 & sleep 30", "timeout", expected=1)
        self.assertEqual(timeout.returncode, 124, timeout.stdout + timeout.stderr)
        self.assertEqual(timeout_record["status"], "TIMED_OUT")
        self.assertTrue(timeout_record["cleanup_verified"])


@unittest.skipUnless(os.name != "nt" and BASH and shutil.which("jq"), "native Unix-like Bash and jq are required")
class UnixStopVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="portable stop shell ")
        self.repo = Path(self.temp.name)
        result = run(["git", "init", "--quiet", str(self.repo)])
        self.assertEqual(result.returncode, 0, result.stderr)
        agent = self.repo / ".agent"
        agent.mkdir()
        shutil.copy2(AGENT / "run-bounded.sh", agent / "run-bounded.sh")
        shutil.copy2(AGENT / "stop-verify.sh", agent / "stop-verify.sh")
        (agent / "stop-verify.json").write_text(
            json.dumps(
                {
                    "enabled": True,
                    "source_extensions": [".py"],
                    "commands": [["sh", "-c", "test -f \"$1\"", "stop-verify", "{files}"]],
                    "full_commands": [["sh", "-c", "test -f app.py"]],
                    "expected_upper_bound_seconds": 5,
                    "cleanup_allowance_seconds": 2,
                    "heartbeat_interval_seconds": 1,
                    "timeout_basis": "native Unix-like smoke test",
                }
            ),
            encoding="utf-8",
        )
        self.stop_script = agent / "stop-verify.sh"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, event: str) -> dict[str, object] | None:
        payload = json.dumps(
            {
                "cwd": str(self.repo),
                "session_id": "portable-workflow-shell-session",
                "hook_event_name": "SessionStart" if event == "session-start" else "Stop",
            }
        )
        result = run([BASH, str(self.stop_script), event], input=payload, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout.strip()
        return json.loads(output) if output else None

    def test_stop_verifies_a_changed_source_once(self) -> None:
        self.assertIsNone(self.invoke("session-start"))
        (self.repo / "app.py").write_text("value = 1\n", encoding="utf-8")
        self.assertIsNone(self.invoke("stop"))
        state = self.repo / SHARED_VERIFICATION_SNAPSHOT
        first = json.loads(state.read_text(encoding="utf-8"))["last_verified"]
        self.assertEqual([entry["path"] for entry in first], ["app.py"])
        self.assertIsNone(self.invoke("stop"))
        self.assertEqual(json.loads(state.read_text(encoding="utf-8"))["last_verified"], first)


class ConfigurationTests(unittest.TestCase):
    def test_hooks_have_expected_events_and_documented_timeouts(self) -> None:
        data = json.loads((ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
        hooks = data["hooks"]
        self.assertEqual(set(hooks), {"SessionStart", "PreToolUse", "PreCompact", "Stop"})
        for event, groups in hooks.items():
            for group in groups:
                for handler in group["hooks"]:
                    self.assertLessEqual(handler["timeout"], 300 if event == "Stop" else 15)
                    self.assertIn("commandWindows", handler)
        self.assertEqual(hooks["Stop"][0]["hooks"][0]["timeout"], 300)

    def test_codex_config_enables_hooks_only(self) -> None:
        config = tomllib.loads((ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertEqual(config, {"features": {"hooks": True}})

    def test_claude_settings_hooks_have_expected_events_and_call_shared_scripts(self) -> None:
        data = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        hooks = data["hooks"]
        self.assertEqual(set(hooks), {"SessionStart", "PreToolUse", "PreCompact", "Stop"})
        for event, groups in hooks.items():
            for group in groups:
                for handler in group["hooks"]:
                    self.assertLessEqual(handler["timeout"], 300 if event == "Stop" else 15)
                    self.assertNotIn("commandWindows", handler)
                    command = handler["command"]
                    self.assertIn("$CLAUDE_PROJECT_DIR", command)
                    self.assertTrue(
                        ".agent/hooks.sh" in command or ".agent/stop-verify.sh" in command,
                        command,
                    )
        self.assertEqual(hooks["Stop"][0]["hooks"][0]["timeout"], 300)
        stop_events = {handler["command"].split()[-1] for handler in hooks["SessionStart"][0]["hooks"]}
        self.assertEqual(stop_events, {"session-start"})

    def test_stop_example_is_explicit_opt_in_and_uses_whole_argument_placeholder(self) -> None:
        config = json.loads((AGENT / "stop-verify.json.example").read_text(encoding="utf-8"))
        self.assertFalse(config["enabled"])
        self.assertTrue(config["source_extensions"])
        self.assertTrue(config["commands"])
        self.assertTrue(config["full_commands"])
        for command in config["commands"]:
            self.assertEqual(command.count("{files}"), 1)
        for command in config["full_commands"]:
            self.assertNotIn("{files}", command)

    def test_optional_script_policy_is_disabled_by_example_and_adapter_compiles(self) -> None:
        config = json.loads((AGENT / "bounded-script-policy.json.example").read_text(encoding="utf-8"))
        self.assertEqual(config, {"schema": "portable-bounded-script-policy/v1", "enabled": False})
        compiled = compile(SCRIPT_POLICY_ADAPTER.read_text(encoding="utf-8"), str(SCRIPT_POLICY_ADAPTER), "exec")
        self.assertIsNotNone(compiled)

    def test_topology_references_include_every_constructed_level(self) -> None:
        topology = ROOT / ".agents" / "skills" / "project-topology"
        for relative in (
            "references/level-2-investigation-and-review.md",
            "references/level-3-parallel-implementation.md",
            "references/level-4-design-project-topology/SKILL.md",
            "references/level-4-design-project-topology/references/artifact-architecture.md",
            "references/level-4-design-project-topology/references/compiler-pass-recipes.md",
            "references/level-4-design-project-topology/references/execution-plan-template.md",
            "references/level-4-design-project-topology/references/module-recipes.md",
            "references/level-4-design-project-topology/references/project-truth-audit.md",
            "references/level-4-design-project-topology/scripts/validate_execution_plan.py",
        ):
            self.assertTrue((topology / relative).is_file(), relative)
        validator = topology / "references/level-4-design-project-topology/scripts/validate_execution_plan.py"
        self.assertIsNotNone(compile(validator.read_text(encoding="utf-8"), str(validator), "exec"))
        completed = subprocess.run(
            [sys.executable, str(validator), "--self-test"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("execution plan validator self-test: PASS", completed.stdout)

    def test_skill_catalog_uses_current_repository_discovery_location(self) -> None:
        skills = sorted(path.parent.name for path in (ROOT / ".agents" / "skills").glob("*/SKILL.md"))
        self.assertEqual(
            skills,
            [
                "api-design",
                "bounded-run",
                "checkpoint",
                "commit",
                "principles",
                "project-topology",
                "query-codebase",
                "review",
                "test-first",
                "verify",
                "worktree",
            ],
        )
        for skill in (ROOT / ".agents" / "skills").glob("*/SKILL.md"):
            content = skill.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\nname: "), skill)
            self.assertIn("\ndescription: ", content.split("---", 2)[1])

    def test_claude_skills_mirror_matches_canonical_catalog(self) -> None:
        # Claude Code only discovers project skills from .claude/skills/*/SKILL.md.
        # The default/software catalog mirrors .agents/skills/; the optional
        # research selector updates both visible catalogs together.
        canonical = ROOT / ".agents" / "skills"
        mirror = ROOT / ".claude" / "skills"
        canonical_files = {p.relative_to(canonical) for p in canonical.rglob("*") if p.is_file()}
        # Codex-only per-skill provider policy has no Claude Code equivalent.
        canonical_files = {p for p in canonical_files if "agents" not in p.parts}
        mirror_files = {p.relative_to(mirror) for p in mirror.rglob("*") if p.is_file()}
        self.assertEqual(canonical_files, mirror_files)
        for relative in canonical_files:
            self.assertEqual(
                (canonical / relative).read_bytes(),
                (mirror / relative).read_bytes(),
                relative,
            )

    def test_no_template_file_contains_user_specific_absolute_path(self) -> None:
        excluded = {"SPEC.md", "for-jason.md"}
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.name in excluded or "tests" in path.parts or "__pycache__" in path.parts:
                continue
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("C:\\Users\\", content, path)
            self.assertNotIn("/Users/", content, path)
            self.assertNotIn("/home/", content, path)

    def test_shell_scripts_parse_when_native_bash_is_available(self) -> None:
        if os.name == "nt":
            self.skipTest("native Unix-like shell parsing runs on macOS and Linux")
        bash = shutil.which("bash")
        if not bash:
            self.skipTest("bash is unavailable")
        for script in AGENT.glob("*.sh"):
            result = run([bash, "-n", str(script)])
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_shell_scripts_avoid_known_macos_bash_and_bsd_find_extensions(self) -> None:
        for script in AGENT.glob("*.sh"):
            content = script.read_text(encoding="utf-8")
            self.assertNotRegex(content, r"\$\{[^}]*,,\}", script)
            self.assertNotIn("declare -A", content, script)
            self.assertNotIn("mapfile", content, script)
            self.assertNotIn("readarray", content, script)
        sync = (AGENT / "sync-claude-skills.sh").read_text(encoding="utf-8")
        self.assertNotIn("-mindepth", sync)
        self.assertNotIn("-maxdepth", sync)


if __name__ == "__main__":
    unittest.main()
