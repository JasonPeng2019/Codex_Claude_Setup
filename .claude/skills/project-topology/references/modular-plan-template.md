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

## Canonical `PLAN.md`

```markdown
# <Project or change> execution plan

## Outcome and boundaries

<The requested product or operational result; observable acceptance conditions;
non-goals; real constraints; and authority limits. Distinguish inspected facts,
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
compatible pair of steps.>

| Step | Produces | Depends on |
| --- | --- | --- |
| [STEP-01](steps/STEP-01-<slug>.md) | <usable outcome> | <real prerequisite> |

<Use one row per step. This table is the navigation and dependency index; it must
not repeat implementation detail or validation evidence from the step files.>

## Integration and whole-product validation

<How step outputs join; integration order; the combined behaviors that must be
observed; and the focused, relevant, or whole-product evidence sufficient for the
requested result. Identify a mandatory repository or release gate and its consumer
separately from behavioral proof when they are not equivalent. Refer to step-local
checks instead of copying them here.>

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
part of the root outcome it advances.>

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
relevant root acceptance condition instead of copying it. For a new test, state the
setup, action, and important assertion. Give exact commands only when confirmed.
Separate focused behavioral evidence from any broader repository or release gate.>

## Failure scope and recovery

<Realistic product, evidence, execution, integration, or live-state failures; the
smallest work and downstream claims they invalidate; and the local repair, recheck,
rollback, containment, or changed approach. If ordinary local correction is
sufficient, say so briefly instead of inventing a recovery procedure.>
```

## Execution interpretation

This template organizes authoring; it does not decide product success. Apply the
skill's [requirement-fit rules](../SKILL.md#validate-requirement-fit-not-literal-perfection):
corrected mistakes and format drift do not invalidate behavior, and only evidence
whose inputs changed needs to be rerun. Do not create a status or acceptance record.
