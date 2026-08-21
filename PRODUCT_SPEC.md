# Product specification: portable Codex and Claude Code workflow

## Purpose and scope

This repository-local product gives Codex and Claude Code the same engineering
instructions, skills, lifecycle behavior, optional verification, and optional
finite-command controls. Copy it into a Git repository; it does not change global
provider settings, Git hooks, package-manager configuration, or application code.

The repository owner chooses providers, models, permissions, checks, and every
optional policy. Normal agent work is available by default. Stop verification,
strict script routing, and research skills are all deliberate opt-ins.

`README.md` is the quick-start guide. `SPEC.md` is the detailed design contract.

## Products, platforms, and requirements

| Environment | General hooks | Stop verification |
| --- | --- | --- |
| Codex on Windows | PowerShell | PowerShell |
| Codex on macOS/Linux | Bash | Bash |
| Claude Code on Windows | Git Bash | Git Bash |
| Claude Code on macOS/Linux | Bash | Bash |

The Bash scripts support macOS's stock Bash 3.2 and current Linux Bash. Bash Stop
verification requires `jq`; if it is unavailable, the hook warns and takes no
verification action. Python 3.10+ is required for the workspace health check and
the optional strict script-routing policy.

Copy `AGENTS.md`, `CLAUDE.md`, `.agent/`, `.agents/`, and the provider folders
you use (`.codex/`, `.claude/`) to the host repository root. Codex users review
and trust changed project hooks through `/hooks`; Claude uses its normal
project-hook permission model. No global settings are modified.

After import, run:

```text
python .agent/validate-workspace.py
```

The health check validates the shipped workspace surface. It does not install
dependencies or run the host repository's application tests.

## Instructions and skills

`AGENTS.md` is the shared repository policy. `CLAUDE.md` imports it and adds only
Claude-specific integration facts. The default `software` catalog includes skills
for engineering principles, topology selection, verification, worktrees, review,
checkpointing, bounded execution, API design, and test-first work.

### Research mode

```text
python .agent/select-skillset.py research
python .agent/select-skillset.py software
```

`research` adds citation, experiment, reproducibility, and paper-oriented skills
to both Codex and Claude discovery locations. `software` removes only those
optional skills. Restart the provider after switching. This changes skill
visibility only; it does not change hooks, permissions, verification, or access.

## Lifecycle behavior

| Event | User-visible behavior | Default |
| --- | --- | --- |
| SessionStart | Shows `HANDOFF.md` when present, local verification overrides, and a bounded-run reminder. | Active |
| PreToolUse | Prevents a small set of high-confidence destructive mistakes and optionally enforces selected finite-command policy. | Active, narrow |
| PreCompact | Suggests a checkpoint when work is dirty or a handoff exists. It never writes one or blocks compaction. | Active, advisory |
| Stop | Can verify changed source files before the session ends. | Off unless enabled twice |

The safety guard blocks recursive deletion of a filesystem root, home directory,
or repository root; direct `.git` mutation; and commands explicitly selected for
bounded execution. It is a mistake guard, not a security sandbox. Provider
permissions, approvals, filesystem/network access, and elevated modes remain
owner decisions.

## Verification

Agents select focused, relevant, or full checks based on the task. A repository
may create `.agent/verify.toml` from the example to name authoritative commands.
Missing tools, skipped checks, and timeouts are reported as incomplete, not passes.

### Optional Stop gate

The Stop gate needs both opt-ins:

1. Start the provider with `AGENT_STOP_GATE_ENABLED=1`.
2. Create `.agent/stop-verify.json` from the example and set `"enabled": true`.

For example:

```powershell
$env:AGENT_STOP_GATE_ENABLED='1'
codex
```

```bash
AGENT_STOP_GATE_ENABLED=1 claude
```

Restart the provider after changing its inherited environment. Unset the
variable, use any other value, or restart without it to disable the entire gate.
Only Stop verification and its companion baseline capture use this variable; the
other lifecycle behavior continues normally.

The JSON policy defines eligible extensions, changed-file commands containing
exactly one standalone `"{files}"` value, full-fallback commands without it, and
a justified timeout budget. The shipped disabled Python example uses:

```json
"commands": [["ruff", "check", "{files}"], ["pyright", "{files}"]],
"full_commands": [["ruff", "check", "."], ["pyright"]]
```

When a root `.venv` exists, its command directory is used: `.venv/Scripts` on
Windows and `.venv/bin` on macOS/Linux.

### Observable Stop outcomes

An enabled SessionStart records the current Git-relevant working-tree state. This
means pre-existing dirty work is not attributed to the new provider session. At
Stop, eligible states changed after that baseline and not already successfully
verified are passed to the changed-file commands.

A one-line edit causes the complete changed file path—not a literal text diff
hunk—to be checked. A successful unchanged file is not rechecked on every Stop;
changing it again makes it pending again. Markdown, MDX, RST, text, AsciiDoc,
JSONL, and `docs/` paths are ignored by default.

| Situation | Result |
| --- | --- |
| No eligible change | Session ends normally. |
| Changed-file commands pass | New file states are recorded as verified. |
| Changed-file command fails | Stop is blocked; the file remains pending. |
| Eligible deletion or rename | Stop is blocked as incomplete. |
| Baseline missing, unreadable, or invalid | Configured full-fallback commands run. |
| Full fallback passes | A new verified baseline is published. |
| Full fallback fails or cannot publish state | Stop is blocked; no new verified state is claimed. |

Codex and Claude share one provider-neutral snapshot at
`.agent-runtime/stop-verify/verification-snapshot.json`; either can continue from
the state created by the other.

## Finite-command bounding

Use `run-bounded.ps1` or `run-bounded.sh` for finite tests, builds, servers,
watchers, or scripts with a justified expected lifetime. It provides heartbeats,
captured output, a terminal JSON result, timeout cleanup, and a cleanup-containment
result. Timeout is exit code 124 and `TIMED_OUT`; it is not a product pass/fail.

Never bound `codex exec`, `claude -p`, native subagents, or another open-ended
agent launcher. They intentionally remain unbounded sessions.

The normal policy applies only to command fragments listed in
`.agent/bounded-commands.txt`. An optional strict policy, enabled through
`.agent/bounded-script-policy.json`, covers direct Python files, PowerShell
`-File`, shell scripts, Python `-m`/`-c`, and POSIX-shell `-c`. A covered launch
must use the bounded runner unless its resolved path matches a narrow Git-ignore
style entry in `.agent/bounded-exclusions.gitignore`. Launchers are excluded so
they can start unbounded agent sessions.

## Delegation, review, and worktrees

One agent is the normal shape. The topology guidance adds investigation, review,
parallel writing, or a formal modular plan only when the work needs it. A primary
agent owns integration and final verification; independent writers should use
separate worktrees.

The optional formal topology mode supports a ROOT decision owner, explicit steps,
reusable modules, role mapping, and acceptance checks. It is not created for
ordinary work automatically.

## Data, removal, and limits

Disposable operational data, including bounded-run results and enabled Stop state,
lives under ignored `.agent-runtime/`. The workflow does not create an audit
database, command history, commits, staging, pushes, dependency installation,
branches, worktrees, or subagents by itself.

To remove it, delete the copied workflow files and `.agent-runtime/`; no global
Codex or Claude state needs removal.

This product is not a sandbox, antivirus, or generic shell-security system. It
does not select a model, provider, approval mode, or permission tier; enable
repository checks by default; or turn incomplete work into a pass.

## Configuration index

| Need | User-facing control |
| --- | --- |
| Shared instructions | `AGENTS.md` |
| Claude integration | `CLAUDE.md` and `.claude/settings.json` |
| Codex hooks | `.codex/config.toml` and `.codex/hooks.json` |
| Skills | `.agents/skills/`; sync with `.agent/sync-claude-skills.*` |
| Research skills | `.agent/select-skillset.py` |
| Repository checks | `.agent/verify.toml` |
| Stop gate | `AGENT_STOP_GATE_ENABLED` plus `.agent/stop-verify.json` |
| Finite command catalog | `.agent/bounded-commands.txt` |
| Strict routing and exclusions | `.agent/bounded-script-policy.json` and `.agent/bounded-exclusions.gitignore` |
| Workspace health | `.agent/validate-workspace.py` |
