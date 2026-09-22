# Coordination and recovery

Read this reference only when the plan uses delegated investigation, review,
multiple writers, staged integration, live/external operations, or a nontrivial
recovery path. It describes the facts a useful plan must carry; it does not require
an additional coordination artifact.

The generic workspace stays flat: one delivery owner directly assigns all workers
and owns every cross-task decision. Workers do not dispatch other workers.

## Decide whether delegation helps

Use a helper only when its result changes a concrete decision or safely shortens the
critical path. Good reasons include:

- a bounded unfamiliar subsystem must be mapped before design;
- a specialist must evaluate a security, data, performance, accessibility, or
  operational risk;
- an independent check is warranted for a consequential behavior; or
- genuinely separate implementation outcomes can proceed concurrently.

Do not delegate because agents are available, to fill a role list, to generate
approval records, or to review work already decided by stronger evidence. A single
owner remains preferable when coordination and reconciliation would cost more than
the independent work.

## Attach agent subroles to real work

An agent subrole is a temporary execution assignment, not a product partition or
document tier. Map each delegated implementer directly to one or more `STEP-*`
blocks and each investigator or specialist to a bounded question whose answer is
consumed by a named step or root decision.

State single-owner delivery once. When delegation is planned, add an `Owner or
lane` column to the existing `PLAN.md` step map and put bounded write ownership or
specialist inputs in the affected step. Do not create a separate role registry,
role module, persona catalog, or one agent per `BEHAVIOR-*` outcome. A role is not
an implementation step by itself, and its return is useful only through the work
or decision that consumes it.

## Scope a useful assignment

A delegated assignment should make these facts sufficiently clear for the worker
and the consuming decision:

- the question or completed outcome;
- why it is needed now and which decision consumes it;
- relevant context and initial entrypoints;
- in-scope and protected/out-of-scope surfaces;
- write authority and owned paths, if any;
- accepted inputs and dependencies;
- checks the worker should run or evidence it should inspect;
- expected return and completion condition; and
- the condition that should come back to the delivery owner instead of being
  guessed through.

Express those facts in the natural task description; do not force a fixed
20-field card or repeat context already supplied by the runtime. The worker’s
return normally needs only the result or findings, changed paths when it wrote,
checks actually run and their outcomes, and unresolved blockers or integration
notes. Do not require hashes, copied logs, evidence bundles, or acceptance forms
unless a specific downstream consumer needs them.

### Read-only support

A read-only investigator or reviewer receives a bounded question and enough project
context to answer it. Its response needs only enough substance for the delivery
owner to locate a material issue and understand what decision or requirement it can
affect. Cite a path or behavior when useful and recommend a change only when one is
warranted. “No material issue found” is a valid result. Missing presentation detail
does not justify a rerun when the consuming decision is already clear.

The delivery owner applies the skill's requirement-fit classification. Reviewer
confidence, severity wording, or agreement does not create acceptance authority or
expand what the finding can actually invalidate.

## Plan parallel writers only across stable boundaries

Before authorizing concurrent writes, establish:

- each lane’s completed outcome;
- a disjoint path, component, or artifact boundary;
- shared interfaces or assumptions that are already stable;
- inputs supplied by earlier work;
- local checks that do not mutate another lane’s state;
- the integration order and integration owner; and
- the route for a conflict or newly shared decision.

Put plan-wide lane grouping and shared boundaries in `PLAN.md`; put only local
inputs and write ownership in the relevant step file. Do not add a second ownership
table or lane registry containing the same facts.

Parallel writers are not independent when they both change the same interface,
migration, generated output, dependency lockfile, global configuration, or release
decision. Put that shared change under one owner before fan-out, serialize the
writers, or redraw the lanes.

Use worktrees or isolated writable roots only when concurrent changes or tools can
interfere. Isolation is not a substitute for clear ownership. The integration owner
reviews and tests the combined bytes; worker summaries do not prove integration.

## Use gates only for real decisions

A gate should answer one consequential question, such as:

- Is a required behavior established by sufficient evidence?
- Is the shared contract stable enough for consumers to start?
- Is a migration or external action authorized and recoverable?
- Is the integrated result safe to roll out?

Name what consumes the answer and what a failure blocks. An informational milestone,
report publication, reviewer sign-off, or format check is not a gate unless a binding
external process actually consumes it.

Prefer the cheapest decisive check. Combine compatible findings before returning
them to a writer. Do not stop at the first ordinary failure when other independent
checks can finish cheaply, and do not force every downstream lane to wait on an
unrelated failed administrative task.

## Coordinate external, stateful, or destructive work

For an operation against live services, hardware, user data, production state, or
another scarce resource, include only the controls the operation needs:

- exact authority and target;
- prerequisites and a safe readiness check;
- one owner for the operation and resource state;
- observable success and failure signals;
- stop/abort conditions;
- retry or idempotency behavior;
- rollback or containment when possible; and
- cleanup and readback.

Use a disposable rehearsal when it materially reduces the chance of live harm and
can exercise the relevant control path. A rehearsal is not proof that the live
outcome succeeded. Do not build a generic harness or simulation framework for a
single ordinary command.

## Preserve progress through failures

Apply the skill's
[requirement-fit classification](../SKILL.md#validate-requirement-fit-not-literal-perfection)
before changing execution state. Then map the affected fact to its direct consumers.

Track dependencies rather than ceremony. A changed input invalidates direct
consumers and their downstream conclusions, not unrelated results. A corrected
report does not rerun implementation or tests. A repaired local component reruns
its focused checks and only the integration checks whose inputs changed.

### Use the per-step fast lane

The fast lane is an execution shortcut, not another coordination lane. Reuse the
current owner, session, workspace, still-valid outputs, and check results unless a
concrete isolation, authority, lost-context, or write-conflict risk prevents it.
When an earlier step owns the correction, repair it there and return the corrected
output plus what changed. At the furthest step already in progress, invalidate only
direct consumers, run the entries selected by changed inputs from the owning step's fast test suite
plus any invalidated integration check, and resume at the earliest affected action.
Do not relaunch the original agent, worktree, review, and validation topology merely
because a correction crossed a step boundary. Use the normal route when changed-input
impact cannot be bounded or retained state cannot be trusted.

### Worker or handoff problems

If useful work exists but a worker return is incomplete:

1. Recover the result from available artifacts or ask for the exact missing fact.
2. Keep valid implementation and check results.
3. Resume the same worker only when the runtime supports it and continuity is
   useful; otherwise give a fresh worker the retained state and first unresolved
   action.
4. Do not ask the worker to repeat discovery, implementation, or tests whose inputs
   have not changed.

There is no mandatory retry count. Continue while each attempt produces meaningful
progress and the expected value exceeds its cost. Stop repeating the same approach
when the failure signature or lack of progress shows that a prerequisite,
assignment, tool, or assumption must change.

Before retrying a failed worker or tool launch, read the native error and verify the
exact configuration or credential home actually consumed, relevant freshness and
permission conditions, target, and command. Authentication or a text response does
not prove the required action is permitted. Repair an authoritative configuration once when that
is the cause; do not copy workarounds, silently change a user-selected provider or
model, or repeat an unchanged launch.

For an approved stateful command whose process handle is lost or reported unknown,
reconcile its durable checkpoint, output, and exact process identity before
deciding whether work remains. Keep at most one outstanding wait per process handle.
Do not blindly poll, relaunch, or replay a side effect. If the state cannot be
established, hold only the result or operation that consumes it and return the
decision to the delivery owner. These rules require no retry log or recovery report.

### Review old work and repair narrowly

A review of previously completed or inherited work names the step outcome, governing
behavior or risk, changed or suspect surface, and that step's fast test suite. Inspect
direct dependencies or consumers only as needed to decide whether a material defect
exists. An adjacent improvement or imperfect report does not expand the assignment.
If no material defect is established and no relevant input changed, make no repair
and do not rerun checks merely to refresh a record.

Pool compatible material findings and make the smallest coherent repair that restores
the required behavior. Expand the write surface only through a demonstrated code or
contract dependency. Re-review the changed surface and any invalidated invariant,
then run only fast-suite entries selected by changed inputs and direct-consumer or
integration checks whose inputs changed. Preserve every other trustworthy result.
A full suite belongs here only when the repair changed a genuinely broad foundation.
A binding repository or release gate still runs once at its normal integration or
release point rather than after every narrow repair.

When a loop stops making progress:

- preserve the last known-good baseline and still-valid checks;
- state the unresolved behavior or evidence;
- diagnose the repeated cause;
- change the approach, boundary, owner, prerequisite, or oracle;
- plan only the remaining work; and
- continue independent work that does not consume the blocker.

Do not reset history, replace reviewers to obtain a preferred verdict, relabel
failure as success, or restart from zero to make records look clean.

## Keep costly schedules honest

Apply this only when parallel, staged, substantial-matrix, or externally costly work
has scheduling choices that materially affect elapsed time, capacity, or costly
cycles.
Name the approximate critical path and the concrete reason for each consequential
serial edge: a consumed output, shared mutable resource, authority boundary, or
unresolved isolation fact. Compare a safe concurrent alternative when plausible,
using actual host, service, hardware, and provider capacity; spare agent slots or
separate worktrees do not prove that an external resource can run concurrently.

Use approximate ranges and state uncertainty. Account for real overlap rather than
summing concurrent effort as wall-clock time, and do not promise savings that have
not been observed or credibly estimated. Name the observation that triggers
reassessment before another expensive cycle, such as an overrun, demonstrated
contention, changed dependency, or repeated repair. Reassess only future work and
preserve accepted results. Serial integration does not force ready local checks to
wait when their inputs and writable resources are independent. Retire terminal
roles and temporary resources, then activate only the repair or review work still
needed. Do not create a timing ledger or schedule-approval record.

## Integrate and finish

The delivery owner:

1. inspects actual changes for write-boundary overlap or contract impact, correcting
   harmless deviations locally instead of rejecting an otherwise valid lane;
2. resolves shared-contract or merge conflicts serially;
3. integrates in the declared dependency order;
4. runs focused checks after each risky join when useful;
5. runs the planned combined verification on the actual integrated result;
6. states unresolved material product risks honestly; and
7. retires temporary resources without deleting dirty or still-needed work.

Completion is based on the requested behavior and sufficient required evidence,
not universal process perfection. A concise summary of the integrated outcome,
observed checks, and remaining material risks is enough unless the user or an
existing project process asks for more.
