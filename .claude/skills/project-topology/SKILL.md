---
name: project-topology
description: Route a task to the least complex useful execution shape, then use the matching reference to construct it. Use when deciding whether work needs a plan, delegation, parallel agents, worktrees, independent review, staged gates, or a single agent. A harness is never assumed.
---

# Choose and construct the execution topology

Start at Level 0 and escalate only for a concrete reason. Project size, file
count, or available subagents alone do not justify coordination.

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
| 0 — Direct work | A question, diagnosis, documentation/configuration change, or small localized implementation. | One agent inspects, acts, runs proportionate checks, and reports. No plan, handoff, or delegation artifact. |
| 1 — Single-agent plan | One writer can own the work, but dependencies, cross-component scope, or a material decision are easy to lose. | Write a short in-conversation plan: outcome, ordered steps, affected areas, material assumptions/risks, and verification. Keep one writer and one integration context. |
| 2 — Delegated investigation or review | An independent read-only question or fresh review can save time or improve confidence. | Read [Level 2 — investigation and review](references/level-2-investigation-and-review.md) before delegating. The primary agent remains the sole writer. |
| 3 — Parallel implementation | Deliverables have proven non-overlapping ownership and a clear integration contract. | Read [Level 3 — parallel implementation](references/level-3-parallel-implementation.md) before assigning writers or worktrees. |
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
each M module one authoritative rule/process file and make steps reference its stable public interface
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

- Level 0 to 1: dependency order or scope is easy to lose during direct work.
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

Every delegated task states:

- exact scope and question/outcome;
- relevant files or repository area;
- whether it may write and its ownership boundary;
- expected response (findings, patch, or implementation summary);
- checks it may or must run; and
- completion condition.

Workers return concise findings, changed files, checks run, and unresolved risks.
The primary agent remains responsible for truth, integration, and final claims.

## Output

Normally return:

```text
Topology: Level <0-4> — <name>
Reason: <one or two observed reasons>
Execution: <single agent, delegated reads, isolated writers, or staged plan>
Construction: <direct / short plan / named reference>
Verification: <focused, relevant, or full strategy>
```

For Levels 1–4, add only enough plan detail to execute safely.
