# Stable modular plan template

This template fixes where plan information lives so plans remain predictable,
modular, and easy to edit. It does not turn Markdown conformance into a development
gate.

## Fixed package

Every project-topology plan has exactly this core package:

```text
<plan-directory>/
|-- PLAN.md
`-- steps/
    |-- STEP-01-<outcome-slug>.md
    `-- STEP-02-<outcome-slug>.md
```

`PLAN.md` owns cross-step truth. Each `STEP-*` file owns one executable outcome.
When a `project-specification` package governs the work, its `SPEC.md` and
`BEHAVIOR-*` files continue to own product meaning; the `PLAN.md` step map is the
single index connecting those behaviors to implementation work.
Do not add companion files for requirements, evidence, reviews, acceptance, status,
handoffs, hashes, or validation. Add another artifact only when the user, repository,
regulator, or a named downstream consumer requires it.

The initial author should use the canonical headings below. Later agents must read
them semantically: a harmless rename, ordering difference, typo, or misplaced fact
is a local editing issue, not evidence that the plan or implemented product failed.
Only missing meaning that prevents implementation, dependency reasoning, or
requirement-fit validation is substantive.

## Deterministic step rules

1. Create one `PLAN.md` and at least one `STEP-*` file.
2. Make each step one coherent behavioral outcome, not one file, role, command,
   review, report, or administrative action.
3. Give a shared foundation its own step only when multiple later outcomes consume
   it or when it produces an independently usable and verifiable result.
4. During initial authoring, number steps in dependency order. Break ties by their
   first position in the end-to-end product flow, then by lexical outcome slug.
5. Use lowercase hyphenated slugs that describe the completed outcome.
6. After the plan is published, keep existing step IDs stable. Assign the next
   unused ID to added work and express any new predecessor relationship in the step
   map rather than renumbering unaffected files.
7. Keep each shared fact in `PLAN.md` once. Step files link to or name that source
   instead of copying it.
8. Give every step a concrete, independently runnable fast test suite. It may
   reference shared tests and lives inside the step rather than in another artifact.

## Canonical `PLAN.md`

```markdown
# <Project or change> execution plan

## Outcome and boundaries

<Link the governing `SPEC.md` and relevant behavior map when one exists. State the
implementation result, technical boundary, real constraints, non-goals, and
authority limits without copying the specification's product requirements or
acceptance scenarios. If no separate specification is needed, the governing request
supplies the product outcome and observable acceptance. Distinguish inspected facts,
working assumptions, and decisions that are genuinely unresolved.>

## Current system and target design

<The relevant current call, data, state, build, or operational flow; the target
flow; concrete change points; and why this is the smallest complete design. Name
paths, symbols, interfaces, schemas, and confirmed commands where they help an
executor act without rediscovery.>

## Shared decisions and contracts

<Cross-step interfaces, data shapes, state rules, compatibility choices, error
semantics, and design decisions. Keep each shared fact here once. If the plan has
no cross-step contract, say that briefly rather than inventing one.>

## Step map and execution order

<The selected execution shape and its short justification. Single owner is the
default. Name delegated ownership or write boundaries only when delegation is
actually planned. If work will run concurrently, name the planned lanes and the
shared boundary that makes them safe; do not enumerate every theoretically
compatible pair of steps. State a single delivery owner once. If delegation is
planned, append an `Owner or lane` column rather than creating a role registry. For
parallel, staged, or externally costly work whose schedule materially affects
elapsed time, capacity, or costly cycles, state the approximate critical path,
the real reason for consequential serial edges, and the observation that would
trigger schedule reassessment. Use uncertainty rather than a timing ledger or
promised savings.>

| Step | Produces | Depends on |
| --- | --- | --- |
| [STEP-01](steps/STEP-01-<slug>.md) | <usable outcome> | <real prerequisite> |

<Use one row per step. When a `project-specification` package governs the work, add
a `Governing behavior` column between `Produces` and `Depends on`; link the
`BEHAVIOR-*` outcomes each step serves and mark an indirect technical prerequisite
without copying behavior text. Without a separate specification, `Produces` already
connects the step to the root outcome, so do not add a traceability column. This
table must not repeat implementation detail or validation evidence from step files.>

## Integration and whole-product validation

<How step outputs join; integration order; the combined behaviors that must be
observed; and the focused, relevant, or whole-product evidence sufficient for the
requested result. Identify a mandatory repository or release gate and its consumer
separately from behavioral proof when they are not equivalent. Refer to step-local
checks instead of copying them here. When verification is costly, stateful,
dependent, or repeatedly rerun, describe its dependency- and resource-aware
schedule, isolation, concurrency limits, continuous refill, and complete feasible
failure collection in this existing section; do not add a matrix artifact.>

## Risks, assumptions, and unresolved decisions

<Only items that can change implementation, ordering, authority, shared state,
acceptance, or recovery. State the smallest affected scope and earliest useful
resolution point. If there is no special plan-wide item, one sentence is enough.>
```

## Canonical `steps/STEP-<NN>-<outcome-slug>.md`

```markdown
# STEP-<NN> - <Completed behavioral outcome>

## Outcome

<What is observably true when this step is finished, why it is needed, and which
part of the root outcome it advances. When a specification governs the work, name
the relevant `BEHAVIOR-*` IDs without restating their product meaning.>

## Scope and touchpoints

<Relevant current behavior and concrete files, components, symbols, interfaces,
schemas, configuration, generated outputs, or operational surfaces. Identify a
protected surface only when an executor could plausibly change it by mistake.>

## Implementation

<The actionable design: logic and control flow, data or state transitions,
interface changes, validation and error behavior, compatibility, important edge
cases, and any migration, rollout, cleanup, or documentation work this outcome
actually requires. Leave choices local when they do not affect a contract,
dependency, risk, or acceptance condition.>

## Dependencies and integration

<Inputs consumed from earlier steps or external decisions; the exact usable output
this step produces; downstream consumers; and ownership or write boundaries when
relevant. Keep plan-wide lane grouping in `PLAN.md`.>

## Requirement-fit validation

<The material behavior claims and sufficient evidence for each. Refer to the
relevant specification acceptance scenario or root acceptance condition instead of
copying it. For a new test, state the setup, action, and important assertion. Give
exact commands only when confirmed. Separate focused behavioral evidence from any
broader repository or release gate. Before planning product repair from a failed
assertion, compare the exact contract, observed behavior, and assertion; distinguish
a product defect, an overstrong oracle, and an unresolved fact. For consequential
tests, state how the decisive check distinguishes a realistic known-broken
behavior.>

### Fast test suite

<Name the repository-native test files, cases, selectors, targets, smoke checks,
or confirmed commands that form an independently runnable fast suite for this step.
It must decide the material step behavior and changed seams without invoking unrelated
verification. State concisely which changed code, configuration, contract, or
dependency selects which part of the suite; do not create an invalidation matrix.
Reference the tests described above rather than duplicating their setup and
assertions. If no suitable subset exists, include
the smallest focused tests or test target needed in Implementation; it must exist
by step completion. A single focused test may be the suite. “Run relevant tests”
or a full-suite alias containing unrelated checks is insufficient. A shared test
may be referenced by several steps without copying or reimplementing it.>

## Fast lane and failure recovery

<Define the smallest safe route for a scoped correction or changed input after
useful progress exists: its trigger and affected scope, still-valid work and
evidence to retain, direct repair owner and action, only the checks invalidated, and
the earliest affected re-entry or resume point. Reuse the current owner, session,
workspace, and still-valid outputs by default. Fall back to the normal route only
when impact cannot be bounded or a concrete isolation, authority, context, or
write-conflict need requires it. If the normal route is already one local
correction and focused check, say that it is already minimal. For review of
previously completed or inherited work, bound inspection to this outcome, the
changed or suspect surface, and direct dependencies or consumers needed to decide a
material finding. If no material defect is established, make no repair and do not
rerun checks merely to refresh a record. Otherwise pool compatible findings, make
the smallest coherent correction,
and run only the fast-suite entries and direct-consumer or integration checks whose
inputs changed. Expand repair or retest scope only through a demonstrated dependency,
shared contract, or genuinely broad invalidation. A binding full repository or
release gate still runs once at its normal integration or release point rather than
after every repair. Findings are compatible only when they share one correction
objective, owner/source context, authority boundary, proof, and invalidation domain.
When worker or command recovery applies, treat resolved errors, new relevant
evidence or eliminated hypotheses, completed actions, and contract-directed artifact
changes as progress; elapsed time or silence alone is insufficient. A replacement
must change the failed prerequisite, boundary, authority, or next action. Diagnose
the native launch context before retrying, and reconcile checkpoint, output, and
process identity before replaying a stateful command after a lost handle. Also cover
realistic broader product, evidence, integration, or live-state failures
only when they require rollback, containment, cleanup, or a changed approach.>
```

## Execution interpretation

This template organizes authoring; it does not decide product success. Apply the
skill's [requirement-fit rules](../SKILL.md#validate-requirement-fit-not-literal-perfection):
corrected mistakes and format drift do not invalidate behavior, and only evidence
whose inputs changed needs to be rerun. A missing usable fast suite is a substantive
plan gap; a renamed or misplaced heading is not. Do not create a status or
acceptance record.
