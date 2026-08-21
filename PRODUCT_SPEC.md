# Product specification: portable multi-agent workflow

## Purpose

This is a repository-local workflow for Codex, Claude Code, and optional
reviewed command-line workers. It provides shared engineering instructions,
skills, lifecycle safeguards, optional verification, and a provider-neutral
delegation launcher. Copy it into a Git repository without changing global
provider settings, Git hooks, application code, or package-manager settings.

The owner chooses models, providers, permissions, verification commands, and all
optional policies. Normal agent work is available by default; Stop verification,
strict script routing, and every CLI worker entry are opt-in.

`README.md` is the quick-start guide. `SPEC.md` is the detailed design contract.

## Products and requirements

| Environment | General hooks | Stop verification |
| --- | --- | --- |
| Codex on Windows | PowerShell | PowerShell |
| Codex on macOS/Linux | Bash | Bash |
| Claude Code on Windows | Git Bash | Git Bash |
| Claude Code on macOS/Linux | Bash | Bash |

Bash scripts support macOS Bash 3.2 and current Linux Bash. Bash Stop
verification requires `jq`; without it, the hook warns and takes no verification
action. Python 3.10+ is needed for the health check, strict routing, and the
worker launcher.

Copy `AGENTS.md`, `CLAUDE.md`, `.agent/`, `.agents/`, and the provider folders
you use into the host repository root. Codex users trust changed hooks through
`/hooks`; Claude uses its ordinary project-hook permission model. Then run:

```text
python .agent/validate-workspace.py
```

The health check validates the workspace surface; it does not install dependencies
or run the host project's application tests.

## Instructions and skills

`AGENTS.md` is the shared policy; `CLAUDE.md` adds only Claude integration facts.
The default `software` catalog includes skills for principles, topology,
verification, worktrees, review, checkpointing, bounded execution, API design,
and test-first work.

Research skills are optional:

```text
python .agent/select-skillset.py research
python .agent/select-skillset.py software
```

The first command adds citation, experiment, reproducibility, and paper-oriented
skills to both providers. The second removes only those optional skills. Restart
the provider after switching. This changes skill visibility only, never access,
permissions, hooks, verification, or worker behavior.

## Lifecycle and safeguards

| Event | Behavior | Default |
| --- | --- | --- |
| SessionStart | Shows `HANDOFF.md` when present, local verification overrides, and a bounded-run reminder. | Active |
| PreToolUse | Blocks a small set of high-confidence destructive mistakes and optionally applies selected finite-command policy. | Active, narrow |
| PreCompact | Suggests a checkpoint for dirty work or a handoff; never writes one or blocks compaction. | Active, advisory |
| Stop | Optionally verifies changed source files. | Off unless enabled twice |

The guard blocks recursive deletion of a filesystem root, home, or repository
root; direct `.git` mutation; and configured long-running commands. It is not a
security sandbox. Permissions, approvals, filesystem/network access, and any
elevated provider mode remain repository-owner choices.

## Verification and the Stop gate

Agents choose focused, relevant, or full checks according to the task. A
repository can define its own commands in `.agent/verify.toml`. Missing tools,
skipped checks, and timeouts are incomplete outcomes, not passes.

The Stop gate requires both:

1. Start Codex or Claude with `AGENT_STOP_GATE_ENABLED=1`.
2. Create `.agent/stop-verify.json` from the example and set `"enabled": true`.

```powershell
$env:AGENT_STOP_GATE_ENABLED='1'
codex
```

```bash
AGENT_STOP_GATE_ENABLED=1 claude
```

Restart after changing the inherited environment. Unset the variable or use any
other value to turn the complete Stop gate off. It affects only Stop verification
and companion baseline capture; all other hooks remain active.

The JSON policy defines eligible extensions, path-targeted commands with exactly
one standalone `"{files}"` item, full-fallback commands without it, and a timeout
budget. The disabled Python example uses `ruff check {files}` and `pyright
{files}`, with full `ruff check .` and `pyright` fallbacks. A root `.venv` is used
for these tools: `.venv/Scripts` on Windows and `.venv/bin` on macOS/Linux.

At enabled SessionStart, the workflow records the current Git-relevant state,
including pre-existing dirty work. At Stop, it sends only eligible file paths
changed after that baseline and not already successfully verified to the
changed-file commands. A one-line edit checks the complete changed file, not a
text-diff hunk. A successful unchanged file is skipped on later Stops; another
edit makes it pending again. Markdown, MDX, RST, text, AsciiDoc, JSONL, and
`docs/` paths are ignored by default.

| Situation | Result |
| --- | --- |
| No eligible change | Session ends normally. |
| Changed-file commands pass | New file states become verified. |
| Changed-file commands fail | Stop blocks; files remain pending. |
| Eligible deletion or rename | Stop blocks as incomplete. |
| Baseline missing, unreadable, or invalid | Configured full-fallback commands run. |
| Full fallback passes | A new verified baseline is published. |
| Full fallback fails | Stop blocks and claims no new verified state. |

Codex and Claude share `.agent-runtime/stop-verify/verification-snapshot.json`.
Either provider can continue from the other provider's state.

## Finite commands and strict routing

Use `run-bounded.ps1` or `run-bounded.sh` only for finite tests, builds, servers,
watchers, or known scripts with justified expected lifetimes. It provides
heartbeats, captured output, terminal JSON evidence, timeout cleanup, and a
containment result. Timeout is exit code 124 and `TIMED_OUT`, not a product pass
or failure.

Never bound `codex exec`, `claude -p`, native subagents, or this workspace's
agent launchers. They are deliberately unbounded sessions.

The normal finite-command policy covers only fragments in
`.agent/bounded-commands.txt`. Optional strict routing can cover direct Python
files, PowerShell `-File`, shell scripts, Python `-m`/`-c`, and POSIX-shell `-c`.
Enable it through `.agent/bounded-script-policy.json`. Covered paths must use the
bounded runner unless they match narrow Git-ignore-style exclusions in
`.agent/bounded-exclusions.gitignore`. Launchers are already excluded so they can
start unbounded workers.

## Delegation and provider-neutral CLI workers

One agent is the default. The topology guidance adds investigation, review,
parallel writers, or formal planning only when the work needs it. The primary
agent owns integration and final verification; writers should use worktrees.

The optional worker launcher does not choose a provider, model, or permission
tier. `generic-cli`, `claude-cli`, and `codex-cli` ship disabled. The owner must
review, configure, and enable an entry in `.agent/multi-agent.json` before it can
run.

Supported roles are `investigator`, `implementer`, `reviewer`, and `verifier`.
Each worker receives a task card containing task, scope, acceptance check, role,
and delegation identity. Command entries use literal argument vectors and may use
`{prompt_file}`, `{role}`, `{task_id}`, `{workspace}`, and `{delegation_dir}`;
each entry must include `{prompt_file}`.

Validate before use:

```text
python .agent/multi_agent.py validate
```

Use the PowerShell or Bash launcher to start a worker. Read-only roles may use
the main repository. Writer roles require a dedicated worktree unless the owner
explicitly accepts a shared-workspace override. The launcher can run in the
foreground or background. Its disposable directory under `.agent-runtime/multi-agent/`
contains the task card, status, logs, and terminal result; inspect it with:

```text
python .agent/multi_agent.py status --id <delegation-id>
```

The supplied Claude/Codex command entries feed prompt files through a stdin bridge
because `claude -p` and `codex exec` read prompts from stdin. The template never
adds approval-bypass or elevated-permission flags. The owner must explicitly
configure any noninteractive permission access needed by the selected CLI.

## Data, removal, and limits

Disposable bounded-run, Stop, and delegation data lives in ignored
`.agent-runtime/`. The workflow does not create command history, commits,
staging, pushes, dependencies, branches, worktrees, or workers automatically.

To remove it, delete the copied workflow files and `.agent-runtime/`; no global
provider state needs removal.

This is not a sandbox, antivirus, or general shell-security system. It does not
choose a provider/model/permission configuration, enable checks by default, or
turn an incomplete result into a pass.

## Configuration index

| Need | Control |
| --- | --- |
| Shared policy | `AGENTS.md` |
| Provider hooks | `.codex/`, `.claude/`, and `CLAUDE.md` |
| Skills and research mode | `.agents/skills/` and `.agent/select-skillset.py` |
| Repository checks | `.agent/verify.toml` |
| Stop gate | `AGENT_STOP_GATE_ENABLED` plus `.agent/stop-verify.json` |
| Finite commands | `.agent/bounded-commands.txt` |
| Strict routing/exclusions | `.agent/bounded-script-policy.json` and `.agent/bounded-exclusions.gitignore` |
| Worker catalog and roles | `.agent/multi-agent.json` and `.agent/roles/` |
| Workspace health | `.agent/validate-workspace.py` |
