# Level 3 — parallel implementation

Use this level only when independent deliverables have real, non-overlapping
ownership. If two changes touch the same contracts, files, migrations, or release
decision, keep one writer or use Level 4 staging instead.

## Prove the split before launching writers

Write a compact ownership table before delegation:

| Deliverable | Owner | Allowed write area | Inputs from others | Acceptance check | Integration order |
| --- | --- | --- | --- | --- |
| <outcome> | <worker> | <paths/components> | <declared interface> | <focused check> | <number> |

Do not launch parallel writers until every row has a disjoint write area and a
clear integration order. Shared tests, generated files, schemas, lockfiles, and
configuration are common reasons that a split is not actually independent.

## Build the topology

1. Keep one primary agent as decision owner and integrator.
2. Freeze the shared contract or have the primary agent make the shared change
   first. Writers must not independently redesign the same seam.
3. Choose isolation proportionately:
   - a shared workspace for truly non-overlapping paths;
   - a Git worktree for isolated writers or experiments; or
   - a `codex exec` / `claude -p` worker that returns a patch when that is easier
     to integrate.
4. Give each writer the ownership row plus a scoped task card: objective, write
   boundary, accepted inputs, local check, expected return, and completion
   condition.
5. Run independent read-only checks or reviews concurrently where useful.
6. Integrate serially in the declared order. The primary agent resolves conflicts
   and runs final checks on the integrated bytes, not on worker claims.
7. Retire temporary worktrees only after inspecting status; never discard dirty
   work.

## Return contract

Each worker returns: completed outcome, changed files, checks run and results,
assumptions made, integration notes, and unresolved risks. It does not merge,
commit, push, or alter another worker's area unless explicitly authorized.

## De-escalate when needed

If a shared seam, conflict, or changing requirement invalidates the ownership
table, stop parallel writing. Recombine the work under one writer or promote to a
Level 4 staged plan. Do not compensate with locks, a roster, or an elaborate
coordination protocol.
