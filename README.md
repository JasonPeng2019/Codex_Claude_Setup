# Portable Codex and Claude Code workflow

This directory is a copy-paste Codex and Claude Code setup for Git repositories.
It provides useful engineering guidance, bounded command execution, lightweight
lifecycle hooks, proportional verification, optional delegation/review, and safe
worktree/commit workflows without an orchestration harness. Codex and Claude
Code receive the same engineering policy and the same hook behavior, driven by
one shared set of scripts under `.agent/`; only the thin per-product discovery
files differ.

`SPEC.md` is the complete design contract. `for-jason.md` is the plain-English
summary.

## What is included

- `AGENTS.md` — shared repository instructions, canonical for both agents.
- `CLAUDE.md` — Claude-specific pointer: imports `AGENTS.md` and adds the small
  amount of Claude-only integration detail (skill mirror, hook execution notes).
- `.codex/config.toml` — enables Codex project hooks.
- `.codex/hooks.json` — Codex's session context, command guard, pre-compaction
  reminder, and dormant opt-in Stop verifier.
- `.claude/settings.json` — the same four hooks registered for Claude Code,
  calling the identical shared scripts.
- `.agents/skills/` — the canonical default/software skill catalog, discovered
  directly by current Codex versions.
- `.claude/skills/` — Claude Code's mirror of the active visible catalog. Never
  hand-edit it; use the sync scripts for normal catalog edits or the skillset
  selector for the optional research catalog.
- `.agent/run-bounded.ps1` and `.agent/run-bounded.sh` — bounded process launchers.
- `.agent/hooks.ps1` and `.agent/hooks.sh` — deterministic hook implementations
  shared by both products.
- `.agent/bounded-commands.txt` — the explicit opt-in list of finite command fragments that
  must use the bounded launcher; agent and subagent sessions are excluded.
- `.agent/bounded-script-policy.*` — an optional strict policy, launcher catalog,
  and Git-ignore-style exclusions for repositories that need every direct script
  launch bounded.
- `.agent/select-skillset.py` — a small optional `software`/`research` catalog
  switcher. `research` adds six portable research skills to both visible agent
  catalogs; `software` removes only those optional skills.
- `.agent/skillsets/research/` — the canonical source for those optional
  research skills. It does not change permissions or other workflow behavior.
- `.agent/stop-verify.json.example` — opt-in changed-source verification at Stop.
- `tests/` — standard-library regression tests for the portable mechanics,
  covering both the PowerShell and bash implementations of the shared hooks.

There is no installer, service, bundled environment, audit database, automatic
commit gate, or default Stop **verification run**. Codex's registered Stop hook
exits immediately, and Claude Code's Stop hook is likewise a no-op, until a
repository explicitly enables the local Stop-verification configuration.

## Optional research skill catalog

The default is `software`: it exposes the normal general/software catalog and
does not expose research-only skills. To switch the visible catalog for both
Codex and Claude Code, run one of:

```powershell
python .agent/select-skillset.py research
python .agent/select-skillset.py software
```

The optional PowerShell and Unix wrappers are `.agent/select-skillset.ps1` and
`.agent/select-skillset.sh`. Restart the agent session after switching so skill
discovery refreshes. The selector changes skill visibility only—never command
permissions, hooks, verification, model settings, or CLI-worker behavior. Edit
the research sources under `.agent/skillsets/research/`, not the visible copies
under `.agents/skills/` or `.claude/skills/`.

## Install in another repository

1. Copy `AGENTS.md`, `CLAUDE.md`, `.codex/`, `.claude/`, `.agents/`, `.agent/`,
   and the relevant entries from `.gitignore` to the destination repository
   root. Copy only `.codex/` if you don't use Codex, or only `.claude/` and
   `CLAUDE.md` if you don't use Claude Code; both sides read the same
   `AGENTS.md` and `.agent/` scripts either way.
2. Review the copied instructions and remove any skill you do not want from
   `.agents/skills/`, then rerun the sync script so `.claude/skills/` matches.
3. Start Codex in the repository and use `/hooks` to review and trust the
   project-local hook definitions. Codex deliberately skips changed hooks until
   they are trusted. Claude Code has no equivalent trust step; it reads
   `.claude/settings.json` directly (prompting once for permission the first
   time a new hook command runs, per its normal permission model).
4. Ensure `bash`, `jq`, Python 3.10 or later, and ordinary process utilities are available.
   The Unix scripts support macOS's stock Bash 3.2 as well as current Linux
   Bash. This applies on Unix-like systems for Codex, and **on Windows too for
   Claude Code**, which runs project hook commands through Git Bash even on a
   Windows host. The hooks fail open with a visible warning when `jq` is
   absent. The bounded runner uses `setsid` when available; macOS and a
   minimal Git Bash may lack it, so they fall back to recursive `pgrep -P`
   cleanup and report whether containment was verified.
5. Optionally copy `.agent/verify.toml.example` to `.agent/verify.toml` and replace
   examples with repository-authoritative commands.
6. Optionally copy `.agent/stop-verify.json.example` to
   `.agent/stop-verify.json`, set `enabled` to `true`, and replace its source
   extensions and argument-vector commands with checks that genuinely accept a
   list of changed files.

No global Codex or Claude Code settings, and no Git hooks, are modified. To
remove the workflow, delete the copied files and the disposable
`.agent-runtime/` directory.

## Bounded commands

Use the launcher when a command has a justified finite lifetime but may take a
long time, hang, start child processes, run a server/watcher, or execute a broad
test/build.

PowerShell:

```powershell
& .agent/run-bounded.ps1 `
  -Command 'npm test' `
  -WorkingDirectory . `
  -ExpectedUpperBoundSeconds 180 `
  -CleanupAllowanceSeconds 20 `
  -HeartbeatIntervalSeconds 30 `
  -TimeoutBasis 'The normal CI job completes within 150 seconds; 30 seconds is measured headroom.'
```

macOS and Linux:

```bash
bash .agent/run-bounded.sh \
  --command 'npm test' \
  --working-directory . \
  --expected-upper-bound-seconds 180 \
  --cleanup-allowance-seconds 20 \
  --heartbeat-interval-seconds 30 \
  --timeout-basis 'The normal CI job completes within 150 seconds; 30 seconds is measured headroom.'
```

The launcher prints `RUNNING` heartbeats, captures stdout/stderr, returns the
child exit code, terminates the process tree on timeout, and writes a terminal
JSON result under `.agent-runtime/` unless `ResultPath`/`--result-path` is given.
A timeout exits `124` and reports `TIMED_OUT`; it does not decide whether product
behavior passed or failed.

The launcher computes its maximum lifetime as expected runtime plus cleanup
allowance. You may state that maximum explicitly with
`-MaximumLifetimeSeconds`/`--maximum-lifetime-seconds`; it must agree with the
computed value. Cleanup is limited to the smaller of 120 seconds or 25% of the
expected runtime, with a five-second minimum for short commands.

Direct `codex exec` and `claude -p` workers and native subagents remain
unbounded. Do not place them inside `run-bounded` or list them in
`.agent/bounded-commands.txt`. Add only a high-confidence finite test, script,
build, server, watcher, or other command fragment to that file.

### Optional strict script routing

Most repositories should stop there. If direct Python, PowerShell, or POSIX shell
scripts repeatedly bypass useful process bounds, read
[`.agent/bounded-script-policy.md`](.agent/bounded-script-policy.md). It is an
explicit opt-in: copy the example configuration, set `enabled` to `true`, ensure
Python 3.10 or later is available to the hook, and maintain narrow exclusions in
`.agent/bounded-exclusions.gitignore`. The policy recognizes direct script
launches plus Python `-m`/`-c` and POSIX-shell `-c` forms; it does not guess
whether a command is a test or scan the repository.
An enabled policy fails visibly for a malformed configuration, unavailable Python,
or non-Git repository instead of silently failing to enforce its declared policy.

## Hooks

Four hooks are registered for both products, `.codex/hooks.json` for Codex and
`.claude/settings.json` for Claude Code, calling the same underlying scripts:

- `SessionStart` surfaces `HANDOFF.md`, local verification overrides, and the
  bounded-run reminder. It does not scan or verify the repository.
- `PreToolUse` blocks recursive deletion of a filesystem root, user home, or repository root,
  direct `.git` mutation, and commands explicitly configured as long-running. It
  is a narrow mistake guard, not a shell security boundary.
- `PreCompact` suggests a checkpoint when the worktree is dirty or a handoff
  exists. It never writes the handoff or blocks compaction.
- `Stop` is dormant unless `.agent/stop-verify.json` exists with `enabled: true`.
  When enabled, every provider's `SessionStart` replaces the one shared snapshot at
  `.agent-runtime/stop-verify/verification-snapshot.json`. That provider-neutral
  snapshot records the authoritative baseline of pre-existing dirty files and the
  last successfully verified file states. At Stop, any hooked provider reads that
  same file and passes only configured source extensions changed since its baseline
  to the exact configured changed-file commands. If the snapshot is unavailable or
  invalid, the hook instead runs the separately configured full commands. Markdown,
  MDX, RST, text, AsciiDoc, JSONL, and `docs/` files are ignored by changed-file
  verification. A successful source check is not repeated until that source changes
  again.

Eligible deletions or renames are reported as incomplete. A missing or invalid
durable verification snapshot runs the explicit `full_commands` fallback rather
than attributing existing dirty work to the active provider. Provider session IDs
are neither stored nor required: Codex, Claude Code, and future integrations use
the same schema and fixed path. When the full fallback passes, its verified state
is published as the new durable snapshot, so later Stops return to changed-file
verification; a failed full fallback publishes nothing. Every successful
SessionStart or end-of-turn verification-state update atomically replaces the
canonical snapshot and removes superseded baseline-state files while preserving
independent run logs. Full verification otherwise remains an explicit agent action. Delete an event entry from
`.codex/hooks.json` or `.claude/settings.json` to disable that hook for the
corresponding product, or set `[features].hooks = false` in `.codex/config.toml`
to disable all Codex project hooks at once.

Codex reaches Windows through a native PowerShell command declared alongside
each hook's Unix `bash` command. Claude Code has no equivalent per-OS command
field: it runs every project hook through `bash` regardless of host OS
(confirmed against a real Claude Code session — it resolves `$CLAUDE_PROJECT_DIR`
to the repository root and executes hook commands via Git Bash even on
Windows), so `.claude/settings.json` calls `.agent/hooks.sh` and
`.agent/stop-verify.sh` directly rather than the `.ps1` scripts.

### Opt-in Stop verification

Copy `.agent/stop-verify.json.example` to `.agent/stop-verify.json`, then make
four deliberate choices: source extensions, changed-file commands, full fallback
commands, and a measured timeout budget. Each changed-file command is an array of
literal arguments with exactly one `"{files}"` entry. The hook replaces that whole
argument with relative paths such as `src/widget.py`; it never appends `.` or
invents a broad command. Each `full_commands` entry is a separate literal argument
array and must not contain `"{files}"`; it runs only when no valid durable
verification snapshot is available.

The hook uses `.agent/run-bounded.ps1` or `.agent/run-bounded.sh` for each command.
The larger of the changed-file and full-fallback command lifetime totals must fit
240 seconds, leaving 60 seconds
of the registered Stop hook's 300-second timeout (both `.codex/hooks.json` and
`.claude/settings.json` declare the same 300-second ceiling) for setup, result
handling, and the hook response. Leave the example disabled—or do not copy it
at all—for projects
whose checks cannot accept individual paths.

## Verification

The `verify` skill prefers commands in this order:

1. The command requested by the user.
2. Commands documented by the repository.
3. Existing test/lint/type/build task entries.
4. Conventional commands supported by authoritative project files.
5. An optional `.agent/verify.toml` override.

It reports focused, relevant, or full verification. Missing tools and skipped
checks are reported rather than treated as passes.

## Delegation and review

The topology skill starts with one agent and escalates only when work is truly
independent or risk warrants a durable staged plan. Its Level 2 and Level 3
references provide the actual investigation/review and parallel-writer
construction rules. Its Level 4 reference preserves the original formal topology
compiler's rigor while emitting one modular package: a composition root, isolated
global rules and validation, independent `STEP-*` files, one authoritative file
for each M01-M10 module, and one separate role-agent mapping. Steps compose module
interfaces instead of copying module process, so a compatible M-module change is
inherited without parallel edits. The formal bundle is for a repository that
already uses that harness; it is never required for normal work. Its authority
shape is strictly one ROOT/orchestrator directly defining and dispatching worker
contracts; workers never direct workers or sub-orchestrators. Native Codex
subagents are preferred. An isolated command-line worker may use `codex exec` or
`claude -p` directly. Agent and subagent sessions always remain unbounded and
must never be routed through the bounded runner.

Independent writers should use non-overlapping ownership, and worktrees when
isolation is useful. The primary agent integrates and verifies the final state.

## Run this workflow's tests

From this directory:

```powershell
python -m unittest discover -s tests -v
```

On macOS or Linux, use `python3 -m unittest discover -s tests -v` when
`python` is not a Python 3.10+ command.

The suite uses only Python's standard library plus the platform shell it tests.
It never installs dependencies. `PowerShellHookTests`/`PowerShellBoundedRunTests`
exercise the `.ps1` implementations; `BashHookTests` exercises `.agent/hooks.sh`
directly through `bash` (skipped if `bash` or `jq` is unavailable) — the same
interpreter Claude Code uses to run project hooks on both Windows and Unix-like
hosts; `UnixBoundedRunTests`/`UnixStopVerificationTests` additionally exercise
the `.sh` scripts natively on macOS and Linux. The test suite never uses WSL.

## Customize

- Edit `AGENTS.md` for repository-wide conventions; `CLAUDE.md` should stay a
  thin pointer, not a second copy of the policy.
- Add or remove default skills under `.agents/skills/`, then run
  `.agent/sync-claude-skills.sh` (or `.ps1`) to regenerate `.claude/skills/`.
  Edit optional research skills under `.agent/skillsets/research/` and reselect
  `research` instead. Never hand-edit files under `.claude/skills/`.
- Put repository-owned verification commands in `.agent/verify.toml`.
- Enable `.agent/stop-verify.json` only for short, path-targeted checks.
- Add only high-confidence finite-command fragments to `.agent/bounded-commands.txt`;
  never add an agent or subagent session.
- Enable `.agent/bounded-script-policy.json` only after a demonstrated direct-
  script supervision problem; it is intentionally not ignored so team policy can
  be reviewed and committed.
- Keep project-specific formatters, test hooks, and Git hooks owned by the host
  repository rather than this template.
