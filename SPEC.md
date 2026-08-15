# Portable Claude Code and Codex Workflow Specification

## 1. Purpose

Build a focused repository-local workflow that can be copied into an existing Git
repository and used immediately by both Codex and Claude Code.

The workflow should improve an agent's judgment, verification, continuity, and
optional task delegation without turning the host repository into an agent
orchestration platform. The goal is maximum practical usefulness per unit of
complexity, not minimum file count. It must remain understandable and maintainable
by one developer.

## 2. Goals

The workflow must:

1. Provide consistent core engineering instructions to Codex and Claude Code.
2. Prefer the smallest correct change and preserve unrelated user work.
3. Discover the host repository's existing tools instead of imposing a toolchain.
4. Make verification proportional to the scope and risk of a change.
5. Support simple single-agent work as the default.
6. Offer lightweight guidance for native subagents or command-line agent
   tasks—`codex exec` or `claude -p`—when delegation has a clear benefit.
7. Support an explicit checkpoint/handoff for long-running work.
8. Work after copying the files, with no installer, generated projection, bundled
   virtual environment, or persistent workflow service.
9. Behave honestly when a tool, project convention, or verification route cannot
   be determined.
10. Keep Claude- and Codex-specific configuration thin and keep shared policy in
    one canonical location wherever the products permit it.
11. Provide bounded process execution for commands that may hang, run for a long
    time, or leave child processes behind.
12. Preserve other broadly useful capabilities from the source workflows:
    isolated worktrees, evidence-based codebase queries, independent review,
    test-first implementation, API design, and deliberate commits.
13. Offer an optional, repository-owned strict script-routing policy with narrow
    Git-ignore-style exclusions when direct script launches have demonstrated a
    repeated supervision problem.

## 3. Non-goals

The portable baseline will not provide:

- an orchestration harness or coordinator daemon;
- mandatory multi-agent execution;
- agent rosters, role/model registries, locks, waves, or closure protocols;
- operating modes such as software, research, firmware, restricted, or unleashed;
- generated configuration projections;
- audit-event databases or verification evidence caches;
- a design ledger, mandatory decision identifiers, or fixed plan grammar;
- automatic Git hook installation or a mandatory commit gate;
- repository scaffolding or enforced directory topology;
- bundled language runtimes, package managers, linters, or virtual environments;
- mandatory adversarial review for ordinary changes;
- full-repository verification on every agent response or Stop event;
- universal support for every build system.

Domain-specific skills may be added by an individual repository, but are not part
of this baseline.

## 4. Design principles

### 4.1 Correctness and honesty

- Never report a write, test, build, or verification as successful unless its
  result was observed.
- Distinguish failure, skipped work, unavailable tooling, and uncertainty.
- Validate realistic mistakes that could produce a wrong target or false result.
- Do not add speculative guards against threats outside the host project's real
  trust boundary.

### 4.2 Simplicity and proportionality

- Every file and mechanism must solve a recurring, concrete problem.
- Prefer instructions and existing project commands over custom framework code.
- Add complexity only when its normal-use benefit clearly exceeds its maintenance
  and failure cost.
- A small task should remain a small task.

### 4.3 Portability

- Do not hardcode usernames, absolute paths, repository names, shell locations,
  language versions, or installed tools.
- Resolve paths relative to the repository root or the invoking file.
- Detect capabilities from repository files and available commands.
- Support Windows and Unix-like environments when scripts are included.
- Degrade with an actionable explanation when a supported operation is not
  available.

### 4.4 Respect for the host repository

- Existing repository instructions and explicit user requests outrank this
  baseline.
- Existing build, test, lint, and type-check commands remain authoritative.
- Preserve unrelated changes and avoid broad cleanup during scoped work.
- Never install dependencies, rewrite project configuration, or mutate Git hooks
  merely to run the workflow.

## 5. Proposed repository contents

The implementation should begin with this baseline:

```text
AGENTS.md
CLAUDE.md
README.md
.codex/
  config.toml
  hooks.json                 # optional; empty or minimal by default
.claude/
  settings.json              # optional; empty or minimal by default
.agents/
  skills/                    # one shared canonical skill catalog
    principles/SKILL.md
    project-topology/SKILL.md
    verify/SKILL.md
    checkpoint/SKILL.md
    bounded-run/SKILL.md
    worktree/SKILL.md
    review/SKILL.md
    query-codebase/SKILL.md
    test-first/SKILL.md
    api-design/SKILL.md
    commit/SKILL.md
.agent/
  hooks.ps1
  hooks.sh
  stop-verify.ps1           # dormant opt-in changed-source Stop verification
  stop-verify.sh
  run-bounded.ps1
  run-bounded.sh
  stop-verify.json.example
  worktree.ps1               # only if Git alone proves too error-prone
  worktree.sh
  verify.ps1                 # include if shared scripting proves worthwhile
  verify.sh
  verify.toml.example        # optional override documentation, not active config
.agent-runtime/              # ignored, disposable bounded-run results and logs
```

This is a proposed shape, not a requirement to create every listed wrapper. If both agents
can follow a canonical root instruction or shared skill without duplication, the
implementation should remove the duplicate.

No runtime output belongs in the copied template. Bounded runs may create
ephemeral logs and terminal results under `.agent-runtime/`; that directory must
be gitignored, safe to delete, and unnecessary for normal startup.

## 6. Instruction model

### 6.1 Precedence

Agents must apply instructions in this order:

1. Current explicit user request.
2. Host repository instructions and constraints.
3. The portable workflow's shared operating instructions.
4. Relevant optional skill guidance.
5. Agent defaults.

A lower-priority instruction must not silently override a higher-priority one.

### 6.2 Root instructions

`AGENTS.md` is the canonical cross-agent engineering policy where supported. It
should be concise and cover:

- inspect relevant files before editing;
- make reasonable low-risk assumptions and state material ones;
- implement the smallest complete solution;
- preserve unrelated work;
- use established repository conventions;
- verify in proportion to change risk;
- route only finite non-agent commands explicitly selected by the bounded-command
  manifest through the bounded launcher;
- report exactly what changed and what was checked;
- do not claim completion while required work remains;
- ask before materially expanding scope or performing an unauthorized external or
  destructive action.

`CLAUDE.md` should contain only Claude-specific integration guidance and point to
the canonical shared policy. It must not restate a second, drifting constitution.

## 7. Skills

### 7.0 Included skill set

The baseline includes a practical core plus focused utility skills. This is a
curated toolbelt, not the beginning of a large skill catalog.

| Skill | Status | Purpose | Typical trigger |
| --- | --- | --- | --- |
| `principles` | Core | Apply the shared engineering decision charter before design or broad changes. | Planning, specifications, architecture, mass edits, consequential implementation choices. |
| `project-topology` | Core | Route work to the least complex execution shape that fits it. | Project planning, decomposition, delegation, parallelism, or deciding whether a plan is needed. |
| `verify` | Core | Discover and run proportionate repository checks, then report their actual result. | Verification requests and completion of implementation work. |
| `checkpoint` | Core | Write a concise resumable handoff when continuity is explicitly needed. | Pause, handoff, compaction preparation, or save-state requests. |
| `bounded-run` | Core | Run long but finite or failure-prone commands with heartbeats, a deadline, captured output, and process-tree cleanup. | Long tests/builds, servers, and scripts with uncertain termination. |
| `worktree` | Utility | Create and retire isolated Git worktrees without losing dirty work. | Parallel writers or isolated experiments. |
| `review` | Utility | Ask a fresh read-only agent to critique a plan, diff, or risky decision with prioritized evidence. | Consequential plans, large/risky diffs, irreversible choices, or explicit review requests. |
| `query-codebase` | Utility | Answer structural questions from repository evidence instead of memory. | Definitions, references, imports, ownership, reachability, and dependency questions. |
| `test-first` | Utility | Guide behavior-first testing when a defect or feature has a useful executable contract. | Behavior changes where a focused regression or contract test is practical. |
| `api-design` | Utility | Review public interfaces for clear contracts and compatibility. | Public APIs, CLI contracts, schemas, library surfaces, or integration boundaries. |
| `commit` | Utility, user-triggered | Inspect, stage deliberately, and create a clean commit after relevant checks. | An explicit user request to commit. |

The copied default should include all listed skills because they are broadly
useful and remain dormant until their triggers apply. Specialized skills from the
source workflows—research-paper review, firmware flashing, presentations,
scaffolding, design-ledger maintenance, and mandatory multi-agent auditing—remain
excluded from the generic baseline.

A skill belongs in the baseline only when all of these are true:

- it applies across common repository types;
- it changes agent behavior in a useful, repeatable way;
- its purpose is not already covered adequately by root instructions;
- any custom backend is small, portable, and necessary for the skill's concrete
  benefit;
- it does not require persistent workflow state;
- a developer can understand and customize it from the `SKILL.md` alone.

Skills should contain decision guidance and output expectations. They should not
introduce mandatory artifact schemas, validators, databases, or wrapper commands
unless a concrete implementation need is demonstrated.

### 7.1 Principles

The `principles` skill is the renamed, compact successor to
`always-keep-in-mind`. The clearer name describes what it provides rather than
when the agent should remember it. It should trigger before plans,
specifications, architectural changes, broad edits, and decisions with meaningful
maintenance or correctness consequences. It should not trigger for simple
questions, repository reading, status reports, or trivial mechanical edits.

#### Content retained

The revised skill retains the strongest ideas from the existing charter:

- correctness;
- simplicity;
- proportionality;
- portability;
- truthful reporting;
- respect for working code;
- realistic trust boundaries;
- the distinction between catching a likely mistake and blocking an intended,
  correctly targeted risk.

It also retains these operational rules:

- do the complete requested work rather than return a partial approximation;
- do not disturb working code outside the requested scope;
- prefer detection, then configuration, then an honest limitation;
- never fabricate success or certainty;
- state a material assumption where the next maintainer will encounter it;
- make every guard, abstraction, limit, and new feature earn its maintenance cost.

#### Content changed or removed

The revised skill removes:

- the long worked migration example;
- repeated explanations of the same trust-boundary distinction;
- arbitrary numeric policy such as a universal `4:1` expected-value threshold;
- claims that every project must support arbitrary inputs or learn and persist new
  cases, which are not appropriate for all software;
- requirements that every public unit document every possible usage detail,
  regardless of the host project's conventions;
- instructions already enforced globally by the agent host;
- repeated definitions of done and anti-pattern lists that restate earlier text;
- harness-specific persistence and autonomy language;
- corrupted punctuation and encoding artifacts.

The existing charter sometimes turns desirable qualities into universal product
requirements. The replacement must treat them as decision principles applied in
the context of the actual repository and user request. For example, portability
means avoiding accidental machine-specific assumptions; it does not mean every
internal application must become cross-platform.

#### Proposed structure

The skill should use this compact structure:

1. **Purpose and trigger boundary** — when the skill applies and when it does not.
2. **Decision order** — understand the goal, inspect reality, choose the smallest
   complete solution, verify the relevant behavior, report honestly.
3. **Six principles** — correctness, simplicity, scope discipline,
   proportionality, portability to the intended environments, and maintainability.
4. **Mistake guards** — block verified contradictions and likely unintended
   targets, but do not obstruct an explicitly authorized and correctly targeted
   operation.
5. **Conflict rules** — correctness over convenience; explicit scope over
   speculative generality; existing project conventions over personal preference.
6. **Short completion check** — outcome complete, relevant checks run, uncertainty
   disclosed, unrelated work preserved.

Target length: approximately 80 to 150 lines, with no more than one short example
if an example materially clarifies a rule. The file must be valid UTF-8 and
contain no corrupted punctuation.

The root `AGENTS.md` should contain a five-to-ten-line summary of these principles
so they influence ordinary work. The full skill adds the decision framework only
when its trigger applies; it must not be injected into every minor interaction.

### 7.2 Project topology

The topology skill becomes a **decision router for execution complexity**. It
answers two questions:

1. How much planning and coordination does this task actually need?
2. If delegation is useful, what is the simplest safe mechanism available?

It is advisory and must not require a harness, fixed plan template, validator,
role registry, role-agent map, or persistent runtime state. The skill may retain
an optional reference bundle for a repository that already uses the formal
harness compiler, but that bundle is never the ordinary route. The skill may
produce a short plan when needed, but most tasks should produce no planning
artifact.

#### Inputs used by the router

The router makes its decision from observable task properties:

- number of independently deliverable outcomes;
- coupling and likely file overlap;
- dependency order between outcomes;
- breadth of the affected codebase;
- uncertainty about architecture or repository behavior;
- consequence and reversibility of mistakes;
- availability of deterministic checks;
- external, scarce, destructive, or stateful resources;
- whether independent review would materially improve confidence;
- available native subagents or a suitable command-line agent (`codex exec` or
  Claude Code's non-interactive `claude -p` mode);
- expected coordination cost relative to implementation cost.

It must not use raw file count, project size, or the mere availability of
subagents as sufficient reasons to add complexity.

#### Complexity levels

The router selects the lowest level that adequately handles the task:

**Level 0 — Direct work**

- Use for questions, diagnosis, documentation, configuration tweaks, and small
  localized changes.
- One agent inspects, acts if authorized, runs proportionate checks, and reports.
- No written plan, task IDs, handoff, or delegation.

**Level 1 — Single-agent plan**

- Use when one agent can own the work but the task has several dependent steps,
  crosses a few components, or has a material decision that should be made before
  editing.
- Produce a short in-conversation plan or use the host's native plan mechanism.
- Keep one writer and one integration context.
- The plan contains only outcome, key steps, affected areas, risks/assumptions,
  and verification.

**Level 2 — Delegated investigation or review**

- Use when independent repository inspection, research, diagnosis, or review can
  run concurrently without multiple writers touching shared implementation.
- The primary agent remains the sole writer and integrator.
- Delegate scope-bounded questions with explicit expected outputs.
- Prefer native subagent spawning when the active agent supports it. Otherwise,
  or when an isolated command-line worker is more practical, use the locally
  available matching CLI: `codex exec "<task>"` or `claude -p "<task>"`. These
  agent sessions remain unbounded. Neither product is the universal preferred fallback.
- This is the preferred multi-agent level for most tasks because it gains
  parallelism without merge coordination.

**Level 3 — Parallel implementation**

- Use only when there are genuinely independent deliverables with clear file or
  component ownership and low merge risk.
- Assign each worker one scope-bounded outcome, write boundary, acceptance condition,
  and return format.
- Use native subagents in a shared workspace only when their write scopes cannot
  conflict. Use Git worktrees or patch-returning command-line workers via
  `codex exec` or `claude -p` when writers need isolation.
- The primary agent integrates results, resolves conflicts, and performs final
  verification on the integrated state.
- Do not create a coordinator protocol, roster, locks, or evidence database.

**Level 4 — Explicit staged execution**

- Reserve for large, high-risk, externally stateful, or strongly dependency-bound
  work where incorrect ordering or integration could cause meaningful harm.
- Produce a concise durable plan describing deliverables, dependency order,
  ownership, integration points, resource constraints, rollback/recovery where
  relevant, and verification gates.
- Subagents remain optional. A Level 4 task may still be best executed by one
  agent if the work is tightly coupled.
- This level coordinates the project through a readable plan, not a harness.

#### Construction references

The router must make the construction guidance discoverable rather than merely
name a level:

- Level 2 points to a short reference covering read-only task cards, the single
  primary-writer boundary, review contracts, and isolated unbounded CLI-worker fallback.
- Level 3 points to a short reference covering proven ownership boundaries,
  worktree/patch isolation, integration ordering, and de-escalation to one writer.
- Level 4 normally uses the concise durable plan above. When the host repository
  already has the formal harness workflow, or the user explicitly asks for it,
  the preserved-rigor compiler bundle supplies its project-truth audit, compiler
  passes, validator, and modular template set: one composition root, isolated
  global rules and validation, independent step files, one authoritative file per
  M01-M10 module, and a separate role-agent mapping. Steps cite stable module
  interfaces rather than copying module process. Direct ROOT-to-worker authority
  remains the default; one justified direct lane-sub-orchestrator tier is optional,
  and a third orchestration tier is forbidden. Do not import that machinery into
  ordinary work merely because the task is serious.

#### Escalation rules

Start at Level 0 and escalate only for a named reason:

- Escalate to Level 1 when dependency order or scope is easy to lose during
  direct work.
- Escalate to Level 2 when at least one independent read-only lane saves time or
  provides valuable independent judgment.
- Escalate to Level 3 when implementation can be partitioned into non-overlapping
  ownership with a clear integration contract.
- Escalate to Level 4 when durable sequencing, external resources, rollback, or
  consequential gates must remain visible across a long execution.

De-escalate whenever new information shows the extra structure is not earning its
cost. A task does not remain multi-agent merely because it was initially planned
that way.

#### Routing examples

| Task shape | Route |
| --- | --- |
| Fix one parser bug with an existing focused test | Level 0 |
| Add a feature spanning API, storage, and tests in a known codebase | Level 1 |
| Diagnose an unfamiliar failure while separately mapping relevant tests | Level 2 |
| Implement independent backend and frontend changes with separate ownership | Level 3 |
| Perform a staged data migration with external validation and recovery needs | Level 4 |
| Refactor many overlapping modules with no clean ownership boundary | Level 1 or 4 with one writer, not Level 3 |

#### Delegation contract

Delegation is justified only by at least one of:

- meaningful wall-clock savings from independent work;
- useful independent review of a consequential change;
- isolation of a bounded specialist investigation;
- context reduction for a clearly separable subproblem.

Delegation should be avoided when coordination, duplicated repository reading,
merge risk, or review cost is likely to exceed the benefit.

Each delegated task must state its scope, expected output, write authority, and
completion condition. The parent agent remains responsible for integration and
the final claim. A harness must never be assumed. Workers should return concise
findings, changed files, checks run, and unresolved risks; no special JSON schema
or runtime artifact is required.

#### Output contract

The skill's normal output is deliberately small:

```text
Topology: Level <0-4> — <name>
Reason: <one or two concrete reasons>
Execution: <single agent, delegated reads, isolated writers, or staged plan>
Verification: <focused, relevant, or full strategy>
```

For Levels 1–4, add only the plan detail needed to execute safely. The skill must
not assign identifiers to every requirement, compile a module graph, validate a
fixed document grammar, or create role/model configuration.

### 7.3 Verify

The verify skill runs or identifies the host repository's authoritative checks.
It must prefer explicit project commands over guesses.

Verification has three levels:

- **Focused:** checks directly covering the changed files or behavior.
- **Relevant:** the owning package or subsystem's normal checks.
- **Full:** the repository's documented complete gate.

The agent selects the least expensive level that can support the current claim.
Before claiming a non-trivial implementation complete, it should normally run at
least focused verification. Full verification is used when requested, when the
repository requires it, or when the change is broad/high-risk enough to justify
it.

Detection order:

1. Explicit user command or requested check.
2. Commands documented by the host repository.
3. Existing scripts or task-runner entries clearly named for verification, test,
   lint, type-check, or build.
4. Conventional ecosystem commands inferred from authoritative project files.
5. Optional local `.agent/verify.toml` overrides, if the implementation adopts
   that format.

Initial conventional ecosystems may include Python, Node.js, Rust, Go, and .NET,
but the implementation must not pretend detection is authoritative when multiple
plausible commands exist. It should report the ambiguity or use repository-local
documentation.

Verification output must state:

- commands run;
- checks passed;
- failures with actionable locations when available;
- checks skipped and why;
- whether the result supports a focused, relevant, or full claim.

Missing tools are not passes. An unchanged or documentation-only task may require
no automated checks, but the final response must say so.

### 7.4 Checkpoint

The checkpoint skill creates or refreshes a single `HANDOFF.md` only when the user
asks to save state, pause, prepare for compaction, or hand work to another session.

The handoff should contain only:

- objective and current status;
- completed changes;
- remaining work;
- verification performed and its result;
- important decisions or assumptions;
- relevant files;
- exact next action.

It is a human-readable continuity document, not a workflow authority or state
database. Normal short tasks must not create it.

### 7.5 Bounded run

The bounded-run skill preserves the most useful operational feature from the
current `.codex` workflow: a long-running command remains visible and cannot hang
forever or silently leave a process tree behind.

Use it for commands that are expected to take long enough to disappear behind a
tool-call wait, have previously hung, start child processes, run a server or
watcher, or perform broad tests/builds. Do not wrap quick read-only commands,
  Git inspection, `rg`, every language-tool invocation, or any `codex exec` /
  `claude -p` worker. Agent and subagent sessions are never bounded commands.

Each bounded run must accept:

- exact command and working directory;
- expected upper-bound runtime and the concrete basis for it;
- cleanup allowance and resulting hard deadline;
- heartbeat interval no longer than 60 seconds;
- unique result path under `.agent-runtime/`.

The launcher must:

- emit flushed progress heartbeats while the child is live;
- capture stdout and stderr without hiding their locations;
- preserve and return the child's exit code;
- on timeout, terminate the launched process tree and check cleanup;
- write a small terminal result containing status, timing, command, output paths,
  exit code, and cleanup result;
- report timeout as `TIMED_OUT`, not as a product test failure or success;
- never retry an unchanged failure automatically;
- handle paths and commands containing spaces.

The implementation should adapt the proven launcher rather than discard it. An
explicit maximum lifetime is valid only when it equals expected runtime plus
cleanup allowance. Cleanup is capped at the smaller of 120 seconds or 25% of the
expected runtime, with a five-second minimum cap for short commands. For unusual
quoting, environment setup, or exit normalization, use a task-local wrapper that
the shared launcher still supervises.

The default must not globally wrap every Python, PowerShell, or shell script. A
repository that has demonstrated a repeated supervision problem may explicitly
enable direct script routing with a small configuration, narrow Git-ignore-style
exclusions, and a deterministic adapter for explicit interpreter-plus-script,
Python `-m`/`-c`, and POSIX-shell `-c` forms. That enabled policy must fail visibly if its required interpreter,
configuration, adapter, or Git repository is unavailable; the absent policy must
remain completely inert. No plan IDs or permanent evidence database are needed.

The launcher must work on Windows and Unix-like systems. Equivalent `.ps1` and
`.sh` implementations are acceptable if process-tree handling cannot be shared
without adding a runtime dependency. Both must satisfy the same observable tests.

### 7.6 Worktree

The worktree skill provides safe isolation when topology Level 3 selects multiple
writers or when the user asks for an isolated experiment.

It must support create, list, and close operations using ordinary Git worktrees;
derive paths from the current repository; use clear task names; show branch and
worktree paths; refuse to remove a dirty worktree; and leave integration to the
primary agent. It must not require a registry or coordinator lock. A helper script
is justified only if it reliably prevents wrong-root, name-collision, and dirty-
removal mistakes better than documented Git commands.

### 7.7 Review

The review skill keeps the valuable fresh-context critic while removing mandatory
review cadence and recorded verdict state.

It launches or instructs a read-only reviewer to inspect one explicit artifact:
a plan, working diff, staged diff, design choice, or named files. Findings must be
prioritized by consequence, cite file/line evidence when available, distinguish
confirmed defects from questions, and end with `SHIP`, `REVISE`, or `BLOCK`.

Use review when requested or when a change is consequential, broad, hard to
reverse, security-sensitive, or benefits materially from independent judgment.
Do not require it after every milestone or for routine low-risk work. No review
database, freshness hash, or commit gate is required.

### 7.8 Query codebase

The query skill preserves the rule “look up wiring; do not guess.” It guides the
agent to answer definitions, references, imports, callers, ownership, and
dependency questions using `rg`, Git, and the host language's existing analyzer.
It returns the command or source locations supporting the answer.

The first version should not ship a universal language-query backend. Existing
tools already cover much of this behavior. A backend may be added later only for
repeated gaps demonstrated across repositories.

### 7.9 Test first and API design

Test-first is recommended when a focused executable contract can reproduce a bug
or define new behavior. It follows red, green, then cleanup, and avoids tests that
only mirror implementation details. It is not mandatory for documentation,
exploratory prototypes, or behavior that cannot be usefully automated.

API design applies to public functions, CLIs, configuration, schemas, protocols,
and integration boundaries. It asks for callers, inputs, outputs, defaults,
failures, compatibility, idempotency/concurrency where relevant, and deliberate
non-goals before implementation. It must remain project-neutral.

### 7.10 Commit

The commit skill is user-triggered only. It inspects status and the staged diff,
runs or confirms relevant repository checks, stages deliberately, and creates a
concise commit message consistent with repository conventions.

It must preserve unrelated changes, never stage everything blindly, never push,
and never require plans, review records, or workflow state that the task did not
otherwise need.

## 8. Verification implementation

### 8.1 Default behavior

The preferred first implementation is instruction-driven: the agent reads the
repository and runs its existing commands directly. A shared verification script
should be added only if it eliminates meaningful duplication between Claude and
Codex without becoming a build-system abstraction layer.

If scripts are implemented, they must:

- locate the Git root from the working directory;
- avoid searching or acting above that root;
- avoid assuming that the copied workflow itself is a Git repository;
- inspect changed paths with Git when change-scoped verification is requested;
- include tracked staged and unstaged changes and relevant untracked files;
- never equate an empty check set with a successful full verification;
- return the underlying failing exit status;
- print concise commands and results;
- avoid installing missing tools;
- accept a documented override for ambiguous repositories.

PowerShell and shell entrypoints must provide equivalent behavior. Shared logic
should not be duplicated if a portable implementation can be invoked reliably on
both platforms; conversely, a new runtime dependency must not be introduced only
to share a small amount of code.

### 8.2 Hooks

Hooks should automate small lifecycle tasks and catch high-confidence mistakes.
They must not become a second workflow engine. Claude and Codex should expose the
same behavior through their current project-local hook formats, backed by shared
scripts where their input/output contracts can be normalized safely.

#### Enabled hooks

**1. SessionStart — load useful local context**

- Locate the current Git root without searching above it after discovery.
- If `HANDOFF.md` exists, tell the agent to read it and show its status/next-action
  summary within a small output limit.
- Surface the presence of repository instructions, verification overrides, and
  the bounded launcher.
- Do not create state, install tools, run checks, inspect the entire repository,
  or block session startup because optional context is unavailable.
- Target runtime: under two seconds in an ordinary local repository.

**2. PreToolUse for shell commands — mistake guard and bounded-run routing**

- Block only high-confidence destructive mistakes: recursive deletion aimed at a
  filesystem root, home directory, or repository root, and direct mutation of
  `.git` internals. Ordinary destructive Git commands remain subject to the host's
  permission model because a hook cannot reliably infer user authorization.
- Recognize only finite non-agent commands explicitly declared in the bounded-command
  configuration and require them to use the bounded launcher. Always exempt direct
  `codex exec`, `claude -p`, native-subagent, and agent-launcher sessions.
- Do not wrap every Python, PowerShell, shell, test, build, or package-manager
  command. Do not attempt to be a shell security parser.
- On uncertainty, leave the host permission system in control rather than invent
  a denial. A block must explain the exact matched condition and recovery.
- The guard must be fast, side-effect free, and independently disableable.

**3. PreCompact — continuity reminder**

- If work is in progress or `HANDOFF.md` already exists, remind the agent to use
  the checkpoint skill before compaction.
- Do not create or rewrite `HANDOFF.md` automatically; the agent must record a
  truthful checkpoint from live context.
- Never block compaction.

#### Optional hooks

Repositories may opt into a **changed-file verification hook** after edits or at
Stop. It must be disabled by default and explicitly declare its eligible source
file types, changed-file argument-vector commands, full-fallback argument-vector
commands, and short timeout. Changed-file commands must use a whole-argument
`{files}` placeholder; the implementation replaces that placeholder only with
eligible files changed since the shared authoritative snapshot. Full-fallback commands must not
contain `{files}` and run only when no valid durable verification snapshot is available.

The hook must record one disposable, ignored, provider-neutral state file at
`.agent-runtime/stop-verify/verification-snapshot.json`, with exactly the schema,
baseline, and last-successful-verification fields defined by
`portable-stop-verification-snapshot/v1`. The **baseline** captures Git-relevant
working-tree file hashes at `SessionStart`, so pre-existing dirty work is not
attributed to the provider that started afterward. The **last successful verification
view** is updated only after every configured check passes. At each later Stop, the
hook verifies only eligible changes whose bytes differ from that view. Therefore a
successful Stop check is not repeated until eligible code changes again; a failed
check remains pending. Every provider and every platform implementation reads and
writes this same path and shape; provider/session identity is not part of the key or
stored state. Each successful `SessionStart` replaces the authoritative file, and
each successful end-of-turn changed-file verification updates the same file. Every
such publication removes legacy hashed or provider-named snapshot states while
preserving independent run logs. A failed verification must not advance or replace
the snapshot.

Eligibility is allowlisted by repository configuration rather than inferred. With
no opted-in source extensions, the hook does nothing. Documentation-only changes
must not invoke verification: Markdown, MDX, reStructuredText, text, AsciiDoc,
JSONL, and documentation-directory files are ignored by default. A repository may
explicitly include another file type, such as JSON configuration, only when it has
an appropriate targeted command for it.

With a valid durable verification snapshot, the hook may inspect only changed or directly
affected files and must run through the bounded launcher. If an eligible deletion
or rename cannot be checked by the configured file-targeted commands, it must
report that verification is incomplete rather than treating the diff as verified.
If the canonical snapshot is missing, unreadable, or has any other schema, the hook
must run the explicit, bounded full-fallback commands instead of
silently skipping verification. A successful full fallback must publish the
current verified worktree state as the new canonical snapshot, after which later
Stops use changed-file verification. A failed full fallback, or failure to publish
its snapshot, must block Stop and leave no newly claimed durable state. The
changed-file and full-fallback command sets
are validated separately, and the larger lifetime total must fit the hook budget.

A repository may also opt into its existing formatter, linter, or policy hook.
Those commands remain repository-owned and are not inferred or installed by this
template.

#### Hooks intentionally excluded

The baseline will not include:

- a blocking Stop verification enabled by default;
- a default advisory Stop hook based only on a dirty worktree;
- automatic full-repository checks without an explicit opt-in fallback command;
- post-edit formatting or test execution on every write;
- audit-event logging or command-history databases;
- automatic commits, staging, pushes, dependency installation, or cleanup;
- mandatory plan, review, worktree, or multi-agent gates;
- automatic checkpoint creation;
- Git hook installation.

#### Hook implementation requirements

- Hook scripts must resolve paths from the event payload and repository root, not
  from hardcoded machine paths.
- They must handle malformed or missing optional payload fields without crashing
  the agent session.
- Advisory hooks fail open with a concise warning. Only the narrow destructive
  mistake guard may fail closed when it positively matches a forbidden target.
- Hook timeouts must be short and documented; hooks must never invoke the bounded
  launcher and then wait for an unrelated long project operation.
- Codex and Claude parity is behavioral, not necessarily byte-for-byte config.
  Claude Code currently exposes project hooks through `.claude/settings.json` and
  lifecycle events including `SessionStart`, `PreToolUse`, `PreCompact`, and
  `Stop`. Codex configuration should use the equivalent project-local events
  supported by the installed Codex version. If an event lacks a reliable
  equivalent, document the difference rather than emulate it with polling.
- Every hook must be removable by deleting one obvious entry from the provider's
  project configuration. No global settings are modified.

Full verification remains an explicit agent action except for the repository's
explicitly configured no-baseline Stop fallback.

## 9. Installation and use

Installation is copying the documented files into a repository. No install script
is required.

The README must explain:

1. Which files to copy.
2. How Codex and Claude discover their instructions and skills.
3. Which files are safe to customize per repository.
4. How to invoke verification and checkpointing.
5. How optional delegation works with native subagents, `codex exec`, or
   `claude -p`.
6. How to remove the workflow completely.
7. Known limitations and recovery when project checks cannot be detected.

Removal must consist only of deleting the copied workflow files and disposable
`.agent-runtime/` output. It must not leave installed Git hooks, global
configuration, background processes, or generated state elsewhere on the machine.

## 10. Configuration policy

Configuration is added only for demonstrated variability that cannot be reliably
discovered. Defaults must cover ordinary repositories.

If `.agent/verify.toml` is implemented, it should remain intentionally small. A
possible shape is:

```toml
[verify]
focused = ["command for focused checks"]
full = ["command for the full repository gate"]
```

The exact schema is not fixed by this specification. It should be designed only
after concrete repositories demonstrate what detection cannot express. There
must not be mode inheritance, role configuration, generated state paths, or a
general plugin system.

## 11. Safety and destructive operations

The workflow relies primarily on the agent host's permission and sandbox model.
It should not attempt to parse every possible shell command as a security
boundary.

Shared instructions must require agents to:

- resolve and inspect the exact target before destructive filesystem or Git
  operations;
- avoid broad recursive deletion targets and destructive Git recovery unless
  clearly requested;
- preserve user changes;
- request direction when the target or authority is materially ambiguous;
- allow intentional, correctly targeted risky work that the user authorized.

The baseline command guard is limited to the high-confidence targets defined in
Section 8.2. Expanding it into a broader shell policy requires concrete incidents
showing that the added parser complexity and false-positive risk are worthwhile.

## 12. Acceptance criteria

The first release is complete when all of the following are true:

1. Copying the documented files into a normal Git repository requires no path
   edits, installer, or generated configuration.
2. Codex discovers its repository instructions and listed skills.
3. Claude Code discovers its repository instructions and listed skills.
4. Both agents receive materially equivalent core engineering guidance without
   two independently maintained policy documents.
5. A small task can be completed by one agent without creating a plan, handoff,
   runtime state, or delegation artifacts.
6. The topology skill recommends single-agent work for a small coupled task and
   permits delegation for a clearly independent task without requiring a harness.
7. Verification follows an existing documented project command when one exists.
8. Verification reports missing or ambiguous tooling honestly rather than passing
   or installing dependencies.
9. A bounded run emits heartbeats, propagates success/failure, times out at its
   declared bound, terminates a spawned child-process tree, and writes usable
   terminal output on Windows and Unix-like systems.
10. CLI agent workers launched with `codex exec` or `claude -p`, native subagents,
    and agent launchers remain unbounded and may not be routed through the bounded launcher.
11. No default Stop hook runs the entire repository's checks.
12. No workflow file contains a repository-specific absolute path, project name,
    package name, or tool version.
13. The workflow works in a clean example repository on Windows and one Unix-like
    environment, or platform-specific limitations are explicitly documented.
14. Removing the copied files completely removes the workflow and leaves no Git
    hooks, global settings, services, or runtime database behind.
15. Worktree cleanup refuses to remove dirty work, review remains read-only, and
    commit behavior runs only after an explicit user request.
16. The maintained workflow remains understandable by one developer. Rich
    references and optional policy adapters are allowed only when they preserve a
    demonstrated capability without burdening the default path.
17. Any automated implementation has focused tests for discovery, exit-code
    propagation, missing tools, changed-file scope, repository-root resolution,
    paths containing spaces, bounded timeout, heartbeat output, process-tree
    cleanup, safe worktree closure, hook pass/block decisions, malformed hook
    input, and hook behavior in a pre-existing dirty worktree.

## 13. Implementation sequence

Implementation should proceed in these bounded stages:

1. Adapt and test the bounded process launcher as a standalone cross-platform
   utility, removing its harness-specific enforcement and state assumptions.
2. Write the shared root instructions and concise principles skill.
3. Write the project-topology, verify, checkpoint, worktree, review,
   query-codebase, test-first, API-design, and commit skills.
4. Add the smallest Codex and Claude discovery/configuration files required by
   their current supported formats.
5. Test the workflow in representative repositories, including bounded success,
   failure, timeout, and child cleanup.
6. Add shared verification or worktree wrappers only for concrete shortcomings
   observed in step 5.
7. Document copying, customization, use, runtime cleanup, and removal.
8. Validate on Windows and a Unix-like environment.

Each stage should remove requirements from later stages when native agent or
repository behavior already solves them reliably.

## 14. Open implementation questions

These questions should be resolved through small prototypes, not speculative
framework design:

- Can both products reference one physical skill directory reliably, or is a
  small mirrored set required?
- What exact Codex project-hook schema is supported by the minimum Codex version
  chosen during implementation, and which enabled events map without behavioral
  compromise?
- Which current Claude Code settings are necessary for local skill discovery?
- Is a cross-platform verification script materially better than direct
  instruction-driven command discovery?
- If an override file is needed, what is the smallest schema demonstrated by real
  repositories?

Answers should update this specification only when they affect user-visible
behavior or acceptance criteria. Tool-specific wiring belongs in the README or
implementation comments rather than expanding the architecture.

## 15. Provider-neutral multi-agent extension

This workspace additionally includes an opt-in, provider-neutral delegated CLI
worker facility under `.agent/`. It is intentionally a small launcher and task
card format, not a persistent orchestration harness, model registry, provider
adapter service, or authorization boundary.

### Configuration and roles

`.agent/multi-agent.json` has schema `portable-multi-agent/v1`. It contains
bounded defaults and a named catalog of local CLI entries. Each entry has an
explicit `enabled` flag, a command **argument vector**, a narrow list of roles,
and string environment overrides. The launcher never uses a shell to execute the
vector. It permits only these placeholders in command arguments:

- `{prompt_file}`
- `{role}`
- `{task_id}`
- `{workspace}`
- `{delegation_dir}`

An entry must include `{prompt_file}` so every worker receives the exact task
card saved in its evidence directory. The shipped generic entry is disabled and
uses a placeholder executable. A repository owner must review, replace, and
enable it before the launcher will run it. No bundled configuration presumes
Codex, Claude Code, a model name, a network service, or credentials.

Role templates live in `.agent/roles/`. Their small metadata block declares
`write_access` and a default scope. Investigator, reviewer, and verifier roles
are read-only. An implementer role has write access, but the launcher rejects an
implementer pointed at the workspace root unless the caller expressly supplies
the shared-workspace override. This is a coordination guard rather than sandbox
enforcement: the primary agent must still give writers disjoint ownership and a
worktree where isolation matters.

### Delegation lifecycle

`multi_agent.py validate` validates the configuration and all referenced role
templates. `launch` creates a unique directory below
`.agent-runtime/multi-agent/`, writes `delegation.json` and `prompt.md`, then
runs the configured command in either foreground or supervisor-backed background
mode. Every invocation writes `status.json`, worker stdout/stderr logs, and a
terminal `result.json`. The result distinguishes `PASSED`, `FAILED`,
`TIMED_OUT`, and `LAUNCH_FAILED`; a timeout exits 124 and separately reports
whether cleanup was verified.

The launcher rejects duplicate delegation identifiers and honors a configured
maximum count of queued/running workers during launch preparation. It prints
heartbeats while a foreground supervisor waits. On timeout, it requests process
group termination and escalates to forced termination; cleanup is strongest on
platforms where a child process group can be observed and killed reliably.

The PowerShell and bash wrappers are thin entry points to the same Python
implementation. Python 3 is the only added launcher prerequisite. The worker
CLI itself, its credentials, permissions, and provider-specific arguments remain
repository-owner choices.

### Operational contract

Use the launcher only after applying the existing topology guidance: one agent is
the default; delegate reads/reviews only when independent judgment helps; launch
parallel writers only with disjoint ownership and an integration order. A worker
returns findings or a bounded implementation summary, never final repository
truth. The primary agent validates any claimed change in the integrated state and
retains authority for commits, pushes, external actions, and destructive work.
