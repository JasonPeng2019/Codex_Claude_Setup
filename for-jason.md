# The Simple Version

## What we are building

This will be a small `.codex` and `.claude` setup that you can copy into almost
any Git repository.

It should give Codex and Claude the same good engineering habits and a useful set
of practical tools without adding a harness, installer, state database, or
complicated workflow. Copy it in, use it, and delete it if you no longer want it.

The goal is not to make it as small as possible. The goal is to keep the features
that regularly save time or prevent real failures, while removing the systems
needed only to coordinate the old harness.

The default workflow is one capable agent doing the work. Extra agents are tools
to use when they clearly help, not a required process.

## What it should improve

The workflow should teach both agents to:

- inspect the relevant code before changing it;
- make the smallest complete change;
- leave unrelated code and user changes alone;
- follow the repository's existing conventions;
- test changes in proportion to their size and risk;
- report honestly what was and was not verified;
- use a plan or extra agents only when the task benefits from them;
- save a clean handoff when a long task needs to be paused.
- keep long commands visible, time-bounded, and cleaned up;
- use isolated worktrees, fresh reviews, codebase queries, and deliberate commits
  when those tools help.

It should discover how each repository already works instead of assuming every
project is Python or requiring specific tools.

## What it will not include

It will not include:

- an orchestration harness;
- mandatory subagents;
- agent roles, rosters, locks, waves, or model mappings;
- software/research/firmware modes;
- audit logs or verification databases;
- mandatory design documents and IDs;
- generated configuration;
- installed Git hooks or mandatory commit gates;
- bundled virtual environments or development tools;
- full-repository tests every time an agent stops responding;
- mandatory review or multi-agent ceremony for ordinary work.

Projects can add specialized features later when they actually need them.

## The files

The finished template will probably contain:

```text
AGENTS.md                 shared engineering instructions
CLAUDE.md                 small Claude-specific pointer/instructions
README.md                 setup and usage

.codex/                   Codex configuration and hooks
.claude/                  Claude configuration and hooks
.agents/                  shared skill catalog
.agent/                   bounded runner and useful shared scripts
.agent-runtime/           ignored, disposable command logs/results
```

The workflow should still be understandable by one developer, but usefulness
matters more than hitting the smallest possible file count. Shared instructions
should live in one place whenever possible so the Claude and Codex versions do
not drift.

## The skills

The workflow will include a practical core and several focused utility skills.

### 1. Principles

This replaces `always-keep-in-mind` with a much shorter version.

It keeps the useful ideas:

- correctness over pretending something works;
- simple solutions over speculative frameworks;
- staying inside the requested scope;
- portability where the project actually needs it;
- protecting against likely mistakes without blocking intentional work;
- making new complexity justify its maintenance cost.

It removes the repetition, long migration example, arbitrary `4:1` rule,
overly universal requirements, harness language, and broken punctuation.

The new skill should be about 80–150 lines. It will be used for plans, specs,
architecture, and broad changes—not injected into every tiny task.

### 2. Project topology

This becomes a simple router that decides how much process a task needs.

It starts at the simplest level and only moves up when there is a concrete reason:

- **Level 0 — Direct work:** One agent handles a small or local task. No plan or
  delegation.
- **Level 1 — Single-agent plan:** One agent owns a larger task but writes a short
  plan because order, scope, or dependencies matter.
- **Level 2 — Delegated investigation:** One agent writes the code while extra
  agents independently investigate or review parts of the problem.
- **Level 3 — Parallel implementation:** Multiple agents implement genuinely
  separate pieces with clear file ownership. Worktrees or patch-returning
  command-line workers can provide isolation when needed.
- **Level 4 — Staged execution:** A large, risky, or externally stateful task gets
  a durable plan with ordering, ownership, recovery, and verification gates. It
  can still use one agent if the work is tightly coupled.

Levels 2 and 3 each point to a short reference explaining exactly how to construct
that setup. Level 4 has two forms: the normal readable staged plan, and—only for
a repository that really uses the formal harness—the preserved-rigor topology
compiler. Its output is one modular package: a composition root plus isolated
global rules, validation, `STEP-*` files, authoritative M01-M10 module files, and
a separate role-agent mapping. Steps compose module interfaces, so a compatible
module-process change propagates without rewriting the steps. The formal compiler
does not become the default process for every project. In this Generic workspace,
its authority boundary is strictly ROOT/orchestrator to direct workers.

The router considers coupling, file overlap, dependencies, uncertainty, risk,
available tests, external resources, and coordination cost. Project size or the
mere availability of subagents is not a reason to use them.

Native subagent spawning is preferred when the active agent supports it. For
isolated command-line work, either product can launch an unbounded worker:
`codex exec "<task>"` for Codex or `claude -p "<task>"` for Claude Code. The workflow should use
the tool that is installed and appropriate to the current session; neither one is
the universal fallback. There is no default harness, role registry, compiled
plan, or persistent coordination state.

### 3. Verify

This skill finds and runs the repository's real checks.

It prefers, in order:

1. The command the user requested.
2. Commands documented by the repository.
3. Existing test, lint, build, or type-check scripts.
4. Normal commands inferred from files such as `pyproject.toml`, `package.json`,
   `Cargo.toml`, `go.mod`, or .NET project files.

Verification can be focused on changed behavior, cover the relevant package, or
run the repository's full gate. The agent should use the cheapest level that can
honestly support its claim.

A missing tool or ambiguous command is not a pass. The agent should explain what
it could not verify rather than installing tools or guessing.

There will be no default blocking Stop **verification run**. Full-repository
verification should be an intentional action, not something that runs whenever the
agent finishes a response.

### 4. Checkpoint

This writes one `HANDOFF.md` when you ask to pause, save state, prepare for
compaction, or hand work to another session.

It records the goal, completed work, remaining work, verification, important
decisions, relevant files, and exact next step.

Normal short tasks do not create handoff files or runtime state.

### 5. Bounded run

This keeps one of the most useful features from the current `.codex`: a launcher
for commands that might take a long time, hang, or leave child processes behind.

Use it for long but finite tests and builds, servers and watchers, and
failure-prone scripts explicitly listed in `.agent/bounded-commands.txt`. Do not
force every quick command—or any `codex exec`, `claude -p`, or native subagent—
through it.

The launcher will:

- print a heartbeat at least once per minute;
- use a stated expected runtime plus cleanup time;
- capture stdout and stderr;
- return the real exit code;
- stop the whole child-process tree at the deadline;
- verify cleanup as far as the operating system allows;
- write a small `PASSED`, `FAILED`, or `TIMED_OUT` result under the ignored
  `.agent-runtime/` directory.

We will adapt the proven launcher rather than throw it away. Its normal mode will
not force every Python, PowerShell, or shell script through it. But repositories
that have a real repeated problem with unbounded scripts can opt into that stricter
rule. That optional rule keeps the useful interpreter detection and Git-ignore
style exclusions, while avoiding the old policy's accidental all-repository
blocking behavior. Harness plan requirements and permanent evidence systems stay
out.

It must work on both Windows and Unix-like systems and handle paths with spaces.
It will also check that an explicitly stated maximum lifetime is exactly the
expected runtime plus cleanup time, reject implausibly padded cleanup budgets, and
allow a small task-local wrapper for unusual quoting or environment setup while
the shared launcher still owns timeout, cleanup, and logs.

## Other useful skills

The baseline will also include:

- `worktree` to create and safely close isolated Git worktrees, refusing to remove
  dirty work;
- `review` to get a fresh, read-only critique of a plan, diff, or risky decision
  when independent judgment is valuable;
- `query-codebase` to find definitions, references, imports, callers, and
  dependencies from evidence instead of guessing;
- `test-first` for features and bugs with a practical executable behavior
  contract;
- `api-design` for public APIs, CLIs, schemas, libraries, and integration
  boundaries;
- `commit`, which runs only when you ask and stages deliberately after relevant
  repository checks.

These tools are included but dormant until their trigger applies. Review will not
be mandatory after every milestone, worktrees will not be created for simple
tasks, and the commit skill will never commit or push on its own.

Specialized research, firmware, presentation, scaffolding, design-ledger, and
mandatory multi-agent-auditing systems will not be part of the generic baseline.

## Verification scripts

The bounded launcher is part of the initial implementation because it already
solves a demonstrated problem. For ordinary verification, agents should first
read the repository and run its existing commands directly. More shared scripts
should only be added when testing shows repeated discovery or safety problems.

If scripts are needed, they must:

- find the current Git repository instead of using hardcoded paths;
- stay inside that repository;
- work with paths containing spaces;
- handle staged, unstaged, and relevant untracked changes;
- return real failure codes;
- never install dependencies;
- work on Windows and Unix-like systems, or clearly document a limitation.

We should not build a universal build-system abstraction just to avoid a few
lines of agent instructions.

## Hooks we will include

Hooks will handle a few automatic lifecycle jobs. They will not run the whole
workflow behind the scenes.

Three useful hooks run by default, plus one dormant opt-in Stop entry:

1. **Session start:** If a `HANDOFF.md` exists, point the agent to it and show a
   short status/next-step summary. Also mention available workflow instructions,
   verification overrides, and the bounded launcher. It will not scan the repo,
   create state, run tests, or block startup.
2. **Before a shell command:** Block only obvious destructive mistakes, such as a
   recursive delete aimed at a filesystem/home/repository root or direct `.git`
   mutation. Ordinary destructive Git commands stay under the agent host's normal
   permission rules because a hook cannot reliably know what you authorized. The
   hook will require only commands you explicitly mark as long-running to use
   the bounded launcher. It will not automatically bound direct `codex exec` or
   `claude -p` workers, every Python script, test command, or build. The optional
   strict script policy can cover direct scripts plus `python -m`, `python -c`,
   and `sh -c` when explicitly enabled.
3. **Before compaction:** Remind the agent to create a truthful checkpoint when
   work is in progress. It will not write `HANDOFF.md` automatically or block
   compaction.
Repositories can optionally enable the dormant changed-file verification hook with
one small local configuration file. It names exact argument-list commands, allowed
source extensions, and a measured timeout. On session start it remembers hashes of
already-dirty Git files, so it does not take credit for another person's existing
work. At Stop it checks only eligible source files changed since that baseline and
different from the last successful check. That means a passing check is not run
again on the next turn unless source code changes again. Markdown, JSONL, ordinary
text, and files under `docs/` do not trigger it. If the session baseline is absent
or invalid at Stop, it runs the repository's separately configured full fallback
commands instead of silently skipping verification. Code deletion or rename that
cannot be checked this way is still reported as incomplete. Existing project
formatter or policy hooks can also remain in use, but this template will not
invent them.

We will not include a default Stop verification run or automatic full verification
without an explicit no-baseline fallback command, tests after every edit, audit
logging, automatic formatting, automatic commits,
Git-hook installation, mandatory review/plan gates, or automatic handoff creation.
A dirty worktree alone is not enough evidence that the current session changed
anything.

Claude and Codex will get the same behavior using their own project hook formats.
If one product does not support a reliable equivalent event, the difference will
be documented instead of building a polling workaround. Every hook will be easy
to disable in one obvious configuration entry.

## How installation works

Installation means copying the files into a repository. There is no installer.

The README will explain what to copy, how both agents discover the workflow, how
to customize verification, how to use delegation and checkpoints, and how to
remove everything.

Removing the copied files must completely remove the workflow. It should leave no
Git hooks, global settings, services, or databases behind.

## How we will build it

1. Adapt the bounded launcher into a standalone Windows and Unix utility.
2. Write the shared root instructions and shorter principles skill.
3. Write the topology, verification, checkpoint, worktree, review, query,
   test-first, API-design, and commit skills.
4. Add only the Codex and Claude configuration needed for discovery.
5. Try the workflow in several real repositories.
6. Add more wrappers only if those tests reveal a real need.
7. Document setup, customization, runtime cleanup, and removal.
8. Test it on Windows and a Unix-like environment.

## What “done” means

The workflow is done when it can be copied into an ordinary repository without
editing paths or running an installer; both agents find and follow it; small tasks
stay simple; larger tasks get only as much coordination as they need; project
checks are run and reported honestly; and deleting the files removes the workflow
completely.
