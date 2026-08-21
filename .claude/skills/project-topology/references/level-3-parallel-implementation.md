# Level 3 — parallel implementation

Use this level only to design future execution when independent deliverables have
real, non-overlapping ownership. If two changes touch the same contracts, files,
migrations, or release decision, plan one writer or use Level 4 staging instead.
This reference defines the topology; it does not launch writers, create
worktrees, or implement the deliverables.

## Prove the split before planning parallel writers

Write a compact ownership table before delegation:

| Deliverable | Owner | Allowed write area | Inputs from others | Acceptance check | Integration order |
| --- | --- | --- | --- | --- |
| <outcome> | <worker> | <paths/components> | <declared interface> | <focused check> | <number> |

Do not authorize parallel writers in the plan until every row has a disjoint
write area and a clear integration order. Shared tests, generated files,
schemas, lockfiles, and configuration are common reasons that a split is not
actually independent.

## Build the topology

1. Keep one primary agent as decision owner and integrator.
2. Freeze the shared contract or have the primary agent make the shared change
   first. Writers must not independently redesign the same seam.
3. Specify future isolation proportionately:
   - a shared workspace for truly non-overlapping paths;
   - a Git worktree for isolated writers or experiments; or
   - a `codex exec` / `claude -p` worker that returns a patch when that is easier
     to integrate.
4. Give each writer the ownership row plus a scoped task card: objective, write
   boundary, accepted inputs, local check, expected return, and completion
   condition.
5. Schedule independent read-only checks or reviews concurrently where useful.
6. Require serial integration in the declared order. The planned primary agent
   resolves conflicts and runs final checks on the integrated bytes, not on
   worker claims.
7. Require the future executor to retire temporary worktrees only after
   inspecting status and never discard dirty work.

## Return contract

Each worker returns: completed outcome, changed files, checks run and results,
assumptions made, integration notes, and unresolved risks. It does not merge,
commit, push, or alter another worker's area unless explicitly authorized.

## De-escalate when needed

If a shared seam, conflict, or changing requirement invalidates the ownership
table during execution, the plan must stop parallel writing and route the work
under one writer or promote it to Level 4 staging. Do not compensate with locks,
a roster, or an elaborate coordination protocol.
