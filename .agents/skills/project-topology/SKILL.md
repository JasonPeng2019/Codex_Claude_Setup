---
name: project-topology
description: Build and validate a significant project execution workflow and plan, including justified roles, dependencies, independently gated STEP-* units, verification, repair returns, resources, and integration. Use only when the user explicitly wants to design or build a substantial workflow/plan for executing a project. Do not use for general coding, ordinary task execution, questions, diagnosis, implementation, or merely deciding how to perform routine work. A harness is never assumed, and this skill plans work without executing it.
---

# Build a significant project execution topology

## Admission boundary

Use this skill only to design the significant workflow and plan the user requested. Do not invoke it
as background ceremony for general coding or task execution, and do not execute the planned project
while compiling its topology. If the request is not to build a substantial reusable or durable
execution plan, handle it without this skill.

After the admission boundary passes, start at Level 1 and escalate only for a concrete reason. Use
Level 0 only as an out-of-scope verdict that this skill should not have been invoked; do not perform
the underlying coding or task from this planning skill. Project size, file count, or available
subagents alone do not justify coordination.

## Inspect before routing

Evaluate:

- independently deliverable outcomes;
- dependency order and likely file overlap;
- codebase breadth and architectural uncertainty;
- consequence and reversibility of mistakes;
- available deterministic checks;
- external, scarce, destructive, or stateful resources;
- value of independent review;
- coordination cost relative to implementation cost; and
- available native subagents or a suitable command-line agent.

## Levels and construction references

| Level | Use when | Construct it by |
| --- | --- | --- |
| 0 — Out of skill scope | The request is general coding, diagnosis, a question, ordinary task execution, or does not ask for a significant workflow/plan. | Stop using this skill and return control to the ordinary task handler; do not execute that task from this skill. |
| 1 — Significant single-agent plan | One writer can own the substantial project, but durable dependencies, cross-component scope, or material decisions need an explicit workflow. | Author the requested plan: outcome, ordered stages, affected areas, material assumptions/risks, ownership, and verification. Keep one writer and one integration context. |
| 2 — Planned delegated investigation or review | The significant workflow benefits from an independent read-only lane or fresh review. | Read [Level 2 — investigation and review](references/level-2-investigation-and-review.md) and encode the delegation contract in the plan without dispatching it. |
| 3 — Planned parallel implementation | The significant workflow has deliverables with proven non-overlapping ownership and a clear integration contract. | Read [Level 3 — parallel implementation](references/level-3-parallel-implementation.md) and encode writers/worktrees in the plan without launching them. |
| 4 — Formal multi-agent execution plan | Work is large, consequential, externally stateful, or strongly dependency-bound, and the project actually needs a durable formal plan. | For an ordinary staged project, write the concise durable Level 4 plan described below. When the project has (or the user explicitly requests) the formal harness workflow, use the preserved [Level 4 plan compiler](references/level-4-design-project-topology/SKILL.md) and every reference it requires. |

### Level 4 without a formal harness

Keep one decision owner and construct a readable durable plan with only:

1. outcomes and acceptance checks;
2. dependent stages and their order;
3. writer/reviewer ownership, including where one writer is required;
4. resource authority, rollback/recovery, and stop conditions where genuinely relevant;
5. integration points; and
6. focused, relevant, and full verification gates appropriate to the risk.

An ordinary compact Level 4 plan remains one cohesive artifact. If it needs independently editable
steps or reusable workflow components—or the user requests modular output—select the formal compiler
and emit its one modular plan/workflow package: a composition root for outcomes and inter-step order,
shared rules defined once near the top, concrete role-to-agent allocation in one separate mapping, one
file per independently gated `STEP-*`, and configured instances of the reusable M01-M10 modules. Give
every STEP file exactly three entry-flow definitions: its normal flow, `FAST_LANE_V2_SERIES_1` as the
outbound-patch path for a scoped repair inside that step that exits toward the later current progress
bound, and
`FAST_LANE_V2_SERIES_2` as the inbound-reconcile path for receiving accepted repairs when that step is
the current progress bound.
Give their configured module instances the exclusive prefixes `MI-NORMAL-*`, `MI-FL2-S1-*`, and
`MI-FL2-S2-*`, respectively. Never reuse an MI across entries. Derive each fast path as a genuinely
lighter, purpose-built route; do not rename or replay the normal entry's heavy MI sequence.
Directly beneath every STEP's `## Normal and FAST_LANE_V2 entry flows` heading, copy the exact
canonical FAST_LANE_V2 usage block from the formal execution-plan template without editing it. Put the
step-specific three-entry table immediately after that identical block.
Give each M module one authoritative rule/process file and make steps reference its stable public interface
rather than copy module behavior. Preserve those interfaces so an internal M-module change propagates
to every consuming step without parallel edits. Do not invent a reduced modular variant or empty
sidecars; every formal compiler output uses the full fixed package.

Subagents remain optional. A tightly coupled Level 4 task may still have one
writer. Do not invent a role registry, lock service, evidence database, fixed
plan grammar, or harness just because the task is serious.

When agents are selected, use exactly one orchestration tier: the persistent
ROOT/orchestrator concretely defines and dispatches every worker task, and every
worker returns results or recommendations to ROOT. A worker never becomes a
sub-orchestrator, self-dispatches, or receives task-definition, scope-definition,
success-definition, acceptance, routing, or integration authority.

## Escalate and de-escalate

- Level 0 to 1: the user explicitly requests a significant workflow/plan and durable structure is justified.
- Level 1 to 2: an independent read-only lane saves time or provides valuable
  independent judgment.
- Level 2 to 3: implementation partitions into non-overlapping ownership with a
  clear integration contract.
- Any level to 4: durable sequencing, external resources, recovery, or
  consequential gates must survive a long execution.
- De-escalate as soon as added structure stops earning its cost.

Do not keep a task multi-agent merely because it was initially described that
way. Never create a role registry, model map, roster, lock service, module graph,
or plan validator for ordinary repository work.

## Delegation contract

Every delegated task represented in the plan states:

- exact scope and question/outcome;
- relevant files or repository area;
- whether it may write and its ownership boundary;
- expected response (findings, patch, or implementation summary);
- checks it may or must run; and
- completion condition.

Workers return concise findings, changed files, checks run, and unresolved risks.
The planned primary agent remains responsible for truth, integration, and final claims. Author these
contracts only; do not dispatch workers while using this skill.

## Output

Normally return:

```text
Topology: Level <0-4> — <name>
Reason: <one or two observed reasons>
Execution: <single agent, delegated reads, isolated writers, or staged plan>
Construction: <out-of-scope / significant plan / named reference>
Verification: <focused, relevant, or full strategy>
```

For Levels 1–4, add only enough plan detail for a later executor to execute safely. Do not perform the
planned work in this skill.
