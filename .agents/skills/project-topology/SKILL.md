---
name: project-topology
description: Design a detailed, repository-grounded execution plan for a substantial project or change. Use after project-specification or when dictated product boundaries, behaviors, constraints, and acceptance are already detailed enough to plan without inventing product intent. If the input is broad or leaves material product behavior undefined, use project-specification first. Produce a stable PLAN.md plus outcome-based STEP files that map governing behavior to concrete technical work, decisive evidence, and the smallest coordination structure that can work. Do not use for routine coding, diagnosis, status reporting, or to add process around ordinary work. This skill plans the work; it does not execute the planned project.
disable-model-invocation: true
user-invocable: true
---

# Design a detailed project execution plan

Create a plan that another capable agent can execute without rediscovering the
important architecture, decisions, dependencies, or acceptance conditions. Depth
comes from technical specificity, not from the number of artifacts, roles, gates,
or records.

This is a planning skill. Inspect the project and write the requested plan, but do
not implement the planned product work or dispatch the workers described by it.
The sole dispatch exception is the read-only Bullshit Checker in Step 7.

When a `project-specification` package exists, it owns dictated product meaning and
this plan owns repository implementation. Reference its behavior IDs and sections;
do not rewrite its requirements or acceptance scenarios into a second authority.

## Generic workspace orchestration

Keep planned delegation flat. One delivery owner assigns every investigator,
writer, reviewer, or tester directly and remains responsible for decisions,
integration, and final acceptance. A worker does not spawn or manage other workers.
Flat ownership is a workspace constraint, not a reason to add more direct workers.

## Stable modular plan package

Every plan uses the predictable two-layer package defined in the
[Modular plan template](references/modular-plan-template.md): one root `PLAN.md`
and one or more outcome-based `STEP-*` files.

`PLAN.md` owns the finish line, current-to-target strategy, shared contracts and
decisions, execution shape, dependency graph, integration, whole-product
verification, and plan-wide risks. Each `STEP-*` file owns one coherent behavioral
outcome and all implementation detail local to it. A small plan still has at least
one step file; a large plan adds steps, not new document tiers.

When the plan consumes a specification, the `PLAN.md` step map is also the single
coverage index from governing `BEHAVIOR-*` outcomes to implementation work. Do not
add a second traceability matrix, requirement ledger, or acceptance map.

The template is the sole authority for filenames, headings, deterministic ordering,
and stable step IDs. The structure exists for editability and navigation, not as a
conformance gate: harmless formatting drift never invalidates usable plan meaning,
product work, or behavioral evidence. When the interface cannot create files,
render the same file boundaries in the response.

Do not wrap the core package in another plan tier or auxiliary administrative
package unless a named external consumer requires it.

## Non-negotiable operating rules

### Validate requirement fit, not literal perfection

Development success means the requested behavior is implemented, supported by
sufficient evidence for the claim, and has no known material in-scope defect. It
does not mean every agent action, command, report, heading, optional check, or
unrelated repository surface is flawless.

Classify problems before deciding what they block:

- **Behavior-impacting defect:** required behavior is wrong or an in-scope
  regression exists. Block the affected step and consumers of its output.
- **Required-evidence gap:** a required claim cannot yet be decided. Hold that
  claim and its consumers, not unrelated completed work.
- **Prerequisite or authority gap:** an input needed by the next action is
  unavailable or permission for that action is missing. Hold only that action and
  its consumers until the gap is resolved.
- **Recoverable execution mistake:** a wrong path, command, fixture, edit, or
  assumption can be corrected locally. Retain valid work and continue.
- **Administrative or presentation defect:** a heading, summary, handoff, report,
  filename, missing duplicate record, or formatting issue is repaired only if a
  real consumer needs it. It is not a product failure and cannot overturn decisive
  behavioral evidence.
- **Unrelated or pre-existing failure:** disclose it and continue unless the
  planned work actually depends on it.
- **Live-safety condition:** stop or contain only the operation and shared resource
  that are threatened.

A nonzero command is an observed command result, not automatically a verdict on
the feature or entire run. Map the failure to the requirement, changed surface,
and downstream consumers it can invalidate.

An unsuccessful intermediate attempt, corrected edit, superseded test run, or
repaired tool invocation is execution history, not a defect in the final result.
After a correction, invalidate and rerun only evidence whose inputs changed; judge
the current product state rather than demanding a pristine first-pass history.

Reason separately about required behavior, the sufficiency of evidence for that
behavior, and any named repository or release gate. Do not collapse those questions
into one global pass/fail verdict. This separation guides decisions; it does not
require three reports or status fields.

Describe execution outcomes in ordinary language. Distinguish required behavior
that is established, required behavior or evidence that remains unresolved,
nonblocking limitations, and an operation that cannot safely proceed. Do not
require status tokens, completion forms, or an acceptance record to make those
distinctions.

If the repository or release process mandates a literal full gate, its failure can
block that gate's consumer or the release. It does not erase implemented behavior,
passing focused evidence, or completed independent steps.

Apply this same classification to review and test findings. Severity wording,
reviewer confidence, or consensus does not create authority. A true but out-of-scope
improvement remains nonblocking, and the delivery owner applies the smallest
correction that restores the required outcome.

### Preserve valid progress

A failure invalidates only the work and evidence that depend on the failed or
changed fact. Keep completed changes, accepted decisions, and passing checks whose
inputs remain valid. Do not restart a whole run, replay unrelated work, or reopen
accepted scope because a handoff, review note, plan section, or test report is
imperfect.

A full restart is justified only when a changed global input, corrupted shared
state, or invalid foundational assumption reaches the entire result. State that
dependency explicitly. Otherwise repair or replan only the unfinished or affected
portion.

### Keep one source of truth

Put each decision or fact in one authoritative place and reference it elsewhere.
The governing specification owns product behavior, while the plan owns technical
design, execution, and development evidence. If planning exposes a missing product
decision, update or resolve the authoritative specification rather than silently
inventing a competing requirement in the plan.
Do not create parallel evidence ledgers, acceptance records, reviewer-approval
records, status histories, or copies of the same plan facts. Do not hash ordinary
files or repeat repository hashes. Use a revision, checksum, receipt, or immutable
record only when a named consumer needs identity, integrity, auditability, rollback,
or exact targeting.

### Make every piece of process earn its cost

Do not require a reviewer panel, consensus vote, fixed number of review rounds,
role registry, model map, module catalog, plan compiler, bespoke validator,
per-step recovery document, test matrix, harness, lock service, or separate report
unless the user, repository, regulator, runtime, or a concrete project risk requires
it. Existing mandatory controls remain binding only when they govern the planned
action or its release and have a real consumer; this skill does not invent new ones.

Do not add empty prose, placeholder rows, or inventories of `N/A` merely to make a
plan look complete. Keep the canonical files and core headings when authoring the
plan, but handle an absent special case with one useful sentence at most. Plan
quality is judged by whether its meaning lets the work be performed and verified
correctly; cosmetic conformance does not outrank that meaning.

## Build the plan

### 1. Establish the real assignment

First decide whether product intent is implementation-ready. The material product
outcomes, boundaries, preserved behavior, constraints, and acceptance must be clear
enough to choose technical work without inventing product decisions. For broad or
behaviorally incomplete input, use the sibling
[project-specification skill](../project-specification/SKILL.md) first, then plan
from its result. Do not hide substantial specification work inside an implementation
step.

When a specification is supplied, read its root and relevant `BEHAVIOR-*` files and
apply the
[specification-to-plan handoff](../project-specification/references/spec-to-plan-handoff.md).
Treat background documents as context unless they actually govern the requested
result. Surface contradictions that would change the product or implementation;
do not silently merge them. A harmless format difference or missing approval record
does not make an otherwise decidable specification unusable.

If no separate specification is needed, state the requested outcome, user-visible
or operational acceptance conditions, non-goals, constraints, and authority
boundary directly from the governing request.

Ask a question only when the missing answer would materially change scope,
architecture, safety, authority, or the next safe action. Otherwise make the
smallest reasonable assumption, label it, and put its validation at the earliest
useful point in the plan.

### 2. Inspect enough of the project to plan concretely

Read applicable repository instructions and inspect the relevant source, tests,
configuration, schemas, generated artifacts, and operational tooling. Trace the
current call path or data flow far enough to identify the real change points and
shared contracts. Prefer current source and executable configuration over old
plans or history.

Do not pad the plan with an inventory of everything inspected. Record only findings
that affect the implementation, ordering, risk, or verification. For the detailed
inspection and writing standard, read
[Detailed planning guide](references/detailed-planning-guide.md), then author the
package with the [Modular plan template](references/modular-plan-template.md).

### 3. Choose the smallest sufficient execution shape

Planning detail and coordination complexity are independent. A single-owner plan
may be extremely detailed; a large file count does not require multiple agents.
Choose from these shapes:

| Shape | Use when | Required coordination |
| --- | --- | --- |
| Single owner | One capable executor can maintain the necessary context and safely implement and verify the result. This is the default. | Ordered implementation and verification only. |
| Single owner with focused support | One owner can deliver, but a bounded unknown or consequential risk benefits from a read-only investigation, design critique, or targeted independent check. | One concrete support question and one collection point. |
| Parallel delivery lanes | Two or more substantial deliverables have stable inputs, disjoint write ownership, and a clear integration order. | Frozen shared contracts, explicit lane boundaries, and one integration owner. |
| Staged coordination | Long dependency chains, live or scarce resources, migrations, rollout/rollback, or repeated cross-lane integration require durable stage boundaries. | Only the stages, decision points, and recovery controls demanded by those facts. No extra coordination package. |

Select multiple agents only when independent work, specialist judgment, isolation,
or wall-clock benefit exceeds coordination cost. Availability of agents, a request
for modular files, or the word “topology” is not sufficient.

If the plan uses any support lane, parallel writer, staged external operation, or
nontrivial recovery route, also read
[Coordination and recovery](references/coordination-and-recovery.md).

### 4. Decompose by executable outcomes

Organize work around coherent behavioral outcomes and dependency boundaries, not
equal-sized chunks or arbitrary phases. Use the detailed planning guide to cover
the current constraints, concrete change points, implementation logic, dependencies,
verification, and only the migration or recovery mechanics the outcome needs.

Put each implementation block in one canonical `STEP-*` file using the template's
semantic sections. They are information homes, not report fields or acceptance
gates. Link shared context from `PLAN.md` instead of repeating it in every step.
The plan must be granular enough to implement, not merely a list such as "update
backend, add tests, review."

When a governing specification exists, map every material `BEHAVIOR-*` outcome to
at least one step and justify every step by a behavior or a necessary technical
prerequisite. Several steps may jointly deliver one behavior, and one coherent step
may advance several behaviors. Keep this mapping in the root step map only.

### 5. Design requirement-fit validation

Use the [detailed validation standard](references/detailed-planning-guide.md#design-requirement-fit-validation)
to map each material acceptance claim to sufficient, decisive evidence, specify
focused tests, and avoid duplicated checks or invented commands.

For a governing specification, translate each material acceptance scenario into
the least expensive technical evidence that can decide it. Reference the relevant
behavior or scenario instead of copying its prose. The specification owns the
observable product result; the plan owns fixtures, assertions, commands, and
environment needs.

Keep behavioral evidence separate from any named exhaustive repository or release
gate. Apply the problem classification above to adverse results: a result affects
only the claims and consumers it can actually invalidate. Report shape, optional
signals, warnings, and unrelated repository failures are not development-success
conditions.

Every `STEP-*` file must contain a concrete **fast test suite** as defined by the
[detailed planning guide](references/detailed-planning-guide.md#define-the-fast-test-suite).
It must identify an independently runnable repository-native test or check subset
that can decide the step's material behavior and changed seams without invoking
unrelated verification. If no suitable subset exists, the step's implementation must add the
smallest focused tests or test target needed by step completion. One focused test
can be the suite; there is no minimum test count, time quota, new runner, or evidence
record. A vague instruction such as “run relevant tests” is a substantive planning
gap, while a harmless heading or formatting defect is not.

### 6. Make integration and recovery local

Name shared-contract changes before their consumers. Put serial integration in the
order the actual dependencies require. When parallel lanes are used, the integration
owner validates the combined result rather than accepting worker summaries as proof.

For each realistic failure, identify the smallest affected scope, the owner of the
repair decision, and the check that proves recovery. Administrative or tooling
failures block only their direct consumers. Findings are compatible only when one
coherent correction objective can be owned in one source context and proved
together under the same required behavior or invariant, authority boundary, and
invalidation domain. Similar wording, proximity, or membership in one step is not
enough. Split findings that need different owners, product decisions, source
contexts, or proof. Batch each compatible group; do not alternate review and repair
after every individual note.

Every `STEP-*` file must define a **fast lane** inside its existing recovery
section. This is the smallest safe route for a scoped correction or changed input
after useful progress exists, not a second implementation topology. Name the
trigger and affected scope, the still-valid work and evidence to retain, the direct
repair action and owner, the checks actually invalidated, and the point where work
resumes. Reuse the current owner, session, workspace, and still-valid outputs by
default. Add a new worker, worktree, reviewer, or broad rerun only when a concrete
isolation, authority, context, write-conflict, or uncertain-impact need requires it.
If the normal route is already one local correction and focused check, state that
it is already minimal instead of inventing a parallel flow.

When a plan reviews previously completed or inherited work, bound the review to the
step outcome, the actual changed or suspect surface, and only the direct dependencies
or consumers needed to decide a material finding. If no material defect is
established, make no repair and do not rerun checks merely to refresh a record.
Otherwise pool compatible findings and make the smallest coherent correction that
restores required behavior. Expand the repair only through a demonstrated dependency
or shared contract. Then run only the
fast-suite entries selected by the changed inputs plus affected direct-consumer or
integration checks. A broader suite is justified only by genuinely broad invalidation
and is not the default repair loop. A binding full repository or release gate still
runs at its normal integration or release point, not after every narrow repair.

Retries are based on progress, not a ritual count. Correct a narrow report or tool
error in place when cheap. If the same approach repeats without meaningful progress,
stop repeating it, diagnose the shared cause, and replan the remaining work with a
concretely different approach. Meaningful progress includes a resolved error, new
relevant evidence or an eliminated hypothesis, a completed assigned action, or an
artifact change that moves toward the contract. Transcript growth, cosmetic
rewrites, repeated discovery, and unchanged commands are not progress; elapsed time,
silence, or a slow useful computation alone do not prove a stall. A replacement
must change the failed prerequisite, task boundary, authority or owner, or next
action. Preserve all still-valid progress.

### 7. Complete the plan, then run the Bullshit Checker loop

Perform a final self-review against the user request and current project:

- every requested behavior is owned by an implementation block;
- every governing specification behavior is mapped to work, and every step is
  justified by a behavior or necessary technical prerequisite;
- no plan decision weakens, expands, or contradicts dictated product behavior
  without explicit authority;
- material current-state claims are grounded in inspected project sources;
- dependencies, shared seams, and integration order are explicit;
- parallel work is genuinely independent and serial work has a real dependency;
- the technical instructions are specific enough to act on;
- verification can decide the claimed outcome, its design challenges whether a
  realistic known-broken behavior could still pass, and a failed assertion is
  compared with the governing contract and observed behavior before product repair;
- substantial costly, stateful, dependent, or repeatedly rerun verification is
  scheduled by its real dependencies and consumed resources without avoidable wave
  barriers or matrix-wide fail-fast;
- each repair batch has one coherent correction objective, owner/source context,
  authority boundary, proof, and invalidation domain;
- every parallel, staged, or externally costly plan whose schedule materially
  affects elapsed time, capacity, or costly cycles names its approximate critical
  path, the concrete reason for consequential serial edges, and an observation that
  triggers schedule reassessment without promising invented savings;
- destructive, external, or live actions have appropriate authority and recovery;
- assumptions are visible at the point they matter; and
- every step names a usable fast test suite, and its scoped repair or re-entry route
  is materially lighter or explicitly states that the normal local route is already
  minimal;
- every old-work review bounds its inspection, repair expansion, and retest scope
  through actual behavior and dependency impact; and
- every role, gate, artifact, rerun, and separate file has a concrete consumer or
  risk-based reason.

Once the plan is executable and its required coverage is sufficient, run the one
universally required planning review: a read-only **Bullshit Checker** focused only
on overcomplexity and ceremony.
Use one independent checker when the runtime provides one. If no independent
checker is available, ROOT performs the same critique as a deliberately separate
pass. This loop reviews the planning artifact; it does not execute product work,
run product tests, or become a lane in the authored plan.

Give the checker the current plan, the user request, and only the governing project
facts needed to distinguish required controls from invented process. Do not prepare
an evidence packet or custom report schema. Ask it to identify:

- roles, lanes, reviewers, gates, handoffs, waits, or approval steps without a
  concrete decision, consumer, risk, or authority boundary;
- duplicated requirements, evidence, acceptance statements, status, or reports;
- hashes, IDs, receipts, registries, ledgers, or immutable records without a named
  integrity, targeting, rollback, audit, or lifecycle need;
- repeated checks, broad reruns, matrices, environments, review cycles, or nominal
  fast suites that do not prove a distinct requirement or changed dependency;
- all-green or global pass/fail gates that let an unrelated, administrative, or
  corrected intermediate failure override current requirement-fit evidence;
- bespoke harnesses, compilers, validators, wrappers, templates, or coordination
  services whose cost exceeds their demonstrated payoff;
- arbitrary decomposition, extra mandatory files, placeholder sections, or
  task-card fields that make execution harder without improving correctness;
- serialization, retry loops, or full-run restarts where independent work or valid
  progress could be preserved; and
- nominal fast lanes that repeat the normal agent, workspace, review, or validation
  topology without a concrete need; and
- administrative defects incorrectly treated as product failures or blockers.

The canonical `PLAN.md` plus `STEP-*` package is a user-required stability and
editability invariant, so its existence is not a valid overcomplexity criticism.
Empty sections, duplicated content, or needless splitting inside that package are
still valid targets for simplification.

The concrete fast test suite and concise fast lane inside each step are required
execution invariants. They live in the existing step and may reference the same
checks used for requirement-fit validation; they do not justify separate entry-flow
tables, test matrices, runners, path IDs, modules, manifests, reports, or duplicated
role and workspace setup.

A detailed governing specification, direct behavior-to-step references, and
technical evidence for dictated acceptance are correctness inputs, not ceremony by
themselves. They become valid simplification targets only when duplicated,
irrelevant to a governing behavior, or more elaborate than a concrete consumer or
risk requires.

A useful criticism identifies the challenged plan element, the coordination or
failure cost it adds, and the smallest simplification. These are decision criteria,
not required report fields: imperfect phrasing does not invalidate the checker pass
or force a rerun. ROOT asks for clarification only when a missing fact prevents
adjudication. The checker may not broaden scope, demand more reviewers or records,
remove required technical detail or verification, or treat plan length and
implementation granularity as ceremony by themselves.

ROOT adjudicates every criticism against the request, repository, runtime, and
actual risk:

- **Valid:** the challenged complexity is not required by a governing constraint
  and has no concrete consumer or risk-reduction payoff. Apply the smallest
  correction while preserving technical specificity, required evidence, authority,
  and recovery.
- **Invalid:** a binding requirement, named consumer, real dependency, or concrete
  risk justifies it. Keep it. A brief working reason is enough; do not create a
  disposition table or ask the checker to approve ROOT's decision.

Repeat the checker on the revised plan whenever ROOT accepts at least one valid
finding. Stop when a pass yields zero ROOT-validated findings. Candidate findings
that ROOT rejects do not keep the loop open, and the checker cannot veto delivery
or repeat a closed criticism unless the relevant plan or governing facts changed.
There is no fixed iteration count and no PASS/BLOCK record. The terminal condition
is ROOT's determination that no valid overcomplexity criticism remains.

The loop's terminal state does not belong in the plan package or an acceptance
record. Do not attach checker transcripts or iteration history. This is the only
universal independent plan review; do not add another by default.

## Output

Deliver the canonical modular package defined above. Do not add more plan artifacts
unless a real repository process or named consumer requires them.

When a `project-specification` package governs the work, link it from `PLAN.md`, use
its stable behavior IDs in the step map and step files, and leave product meaning
there. Return any material product contradiction or unresolved decision to that
authority; do not resolve it through an undocumented implementation assumption.

Keep cross-step truth and the dependency graph in `PLAN.md`; keep outcome-specific
implementation detail and validation in its step file. Preserve technical depth:
name concrete change points, contracts, logic, state transitions, edge cases,
commands when confirmed, integration behavior, and local recovery. Modularity must
not turn the plan into shallow task titles or repeated boilerplate.

End with unresolved decisions only if they truly prevent a complete plan. Optional
refinements, formatting repairs, and unrelated failures are not blockers.
