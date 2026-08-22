# Portable Agent Workspace Aid

This folder describes the optional agent-workspace files beside it. They are a
portable aid for a real repository, not that repository's product documentation.
Keep this folder below the target repository root so it cannot replace the target's
`README.md`, `SPEC.md`, or product documentation.

## What the aid provides

- `AGENTS.md` and `CLAUDE.md`: small repo-agnostic starter instructions. Merge
  them with any stronger target-repository instructions rather than overwriting
  those instructions blindly.
- `.agents/skills/`: the editable Codex skill catalog. `.claude/skills/` is the
  corresponding Claude mirror; regenerate it with `.agent/sync-claude-skills.*`
  after changing the source catalog.
- `.codex/` and `.claude/`: project-local discovery and lifecycle-hook settings.
- `.agent/`: optional helpers for workspace validation, bounded finite commands,
  skill-catalog selection, and provider-neutral multi-agent launches.

## Use in a target repository

Copy only the files and directories the target repository wants, then review
them against its existing instructions and tooling. Do not overwrite target
`README.md`, `SPEC.md`, product specs, or existing agent instructions without an
intentional merge. Run `python .agent/validate-workspace.py` after importing the
complete aid to check its portable structure and skill mirror.

The default helpers do not install Git hooks, make global configuration changes,
run broad checks, create commits, or create handoffs automatically. Configure
repository-specific verification and any optional workflow behavior in the target
repository after import.
