# Claude Code integration

@AGENTS.md

The instructions imported above are the canonical, cross-agent engineering
policy. This file adds only what is specific to running that policy under
Claude Code; it is not a second constitution.

## Skills

`.agents/skills/` is the canonical default/software catalog. Claude Code only
discovers project skills from a fixed `.claude/skills/*/SKILL.md` location, so
`.claude/skills/` mirrors the active visible catalog. Edit default skills under
`.agents/skills/` and rerun the sync script; edit optional research skills under
`.agent/skillsets/research/` and use `.agent/select-skillset.py research`.
Do not hand-edit files under `.claude/skills/` directly.

## Hooks

`.claude/settings.json` registers the same four lifecycle hooks Codex uses:
`SessionStart`, `PreToolUse`, `PreCompact`, `Stop`, calling the identical
shared scripts in `.agent/` (`hooks.sh`, `stop-verify.sh`) that the Codex side
calls. Claude Code runs project hook commands through bash even on Windows, so
these hooks need `bash` and `jq` on `PATH` regardless of host OS; if `jq` is
missing, the hooks fail open with a warning rather than blocking work. The
`PreToolUse` guard only blocks a small set of high-confidence mistakes
(recursive deletion of a filesystem root, home directory, or repository root;
direct `.git` mutation);
everything else stays under Claude Code's normal permission model.

Process-tree cleanup for anything routed through `.agent/run-bounded.sh` (for
example the optional Stop verifier) depends on `setsid` and `pgrep` being on
`PATH`. Stock Git Bash for Windows normally ships without either, so a timed-
out command's cleanup there is best-effort rather than a guaranteed full tree
kill; genuinely Unix-like hosts are unaffected. Install those utilities in the
Git Bash environment if you need the stronger guarantee.

## Delegation

Use `claude -p "<task>"` directly for open-ended command-line workers. Agent and
subagent sessions must remain unbounded; use `.agent/run-bounded.ps1` or
`.agent/run-bounded.sh` only for finite non-agent commands explicitly named in
`.agent/bounded-commands.txt`. Prefer a native Claude Code subagent when one is
available; the command-line worker is the fallback, not the default.

The optional `.agent/multi_agent.py` launcher is deliberately outside the
Claude-specific integration. It can launch any reviewed local CLI command entry
for an investigator, implementer, reviewer, or verifier role. `.agent/multi-agent.json`
ships a disabled `claude-cli` entry as a ready-to-review starting point (it
pipes the task card into `claude -p` via `.agent/pipe-prompt-file.sh`, since
`-p` reads its prompt from stdin, not a file path); review and enable it only
if it fits the local Claude CLI installation, and configure permissions
yourself before relying on it non-interactively. Do not assume that every
multi-agent worker is Claude Code.
