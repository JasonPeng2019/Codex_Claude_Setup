# Detailed planning guide

Use this guide to make a plan technically complete without turning it into a
compliance package. It supplies the reasoning and content standard; the
[modular plan template](modular-plan-template.md) supplies the stable file and
section structure. Combine related facts, keep irrelevant canonical sections
brief, and do not invent extra artifacts for concerns that have no bearing on
implementation or acceptance.

## Inspect the current system

Start from the smallest set of authoritative material that can establish how the
affected system works:

1. Read applicable repository instructions, the user’s source material, and the
   product or operational specification.
2. Locate the implementation entrypoints and trace the relevant call, event, data,
   or build path through the system.
3. Inspect nearby tests to learn existing behavior, fixtures, test boundaries, and
   the project’s normal verification commands.
4. Check configuration, schemas, migrations, generated sources, public types,
   dependency manifests, and deployment files only when the change can affect them.
5. Inspect current runtime or automation behavior before claiming it supplies a
   capability. A named script or directory is not proof that it performs the
   needed isolation, retry, rollout, or cleanup.
6. Use history only to resolve a specific ambiguity that current sources cannot
   answer.

The resulting plan should cite concrete paths and symbols where they help the
executor. It should not contain a research diary, a list of every file opened, or
copies of source text that the executor can read directly.

## Define the finish line

When no separate product specification is needed, translate the governing request
into a compact implementation boundary. When a specification exists, take these
facts from it and reference their authoritative sections instead of restating them:

- **Outcome:** the behavior, artifact, migration, or operational state that must
  exist when the work is complete.
- **Acceptance:** observable facts that distinguish complete from incomplete.
- **Non-goals:** plausible adjacent work that is intentionally outside this change.
- **Constraints:** compatibility, platform, performance, accessibility, security,
  data retention, tooling, timing, or organizational limits that actually apply.
- **Authority:** actions the executor may take and actions that still require a
  user or external decision.

Do not manufacture requirement IDs. Preserve stable `BEHAVIOR-*` IDs supplied by a
`project-specification` package; otherwise use labels only when a large plan needs
stable cross-references. Do not duplicate the same acceptance condition in a
requirement table, step table, evidence table, and review table; keep it once and
link or refer to it naturally.

Distinguish:

- **Observed:** established from current source, configuration, tests, or supplied
  material.
- **Assumed:** a reasonable working premise that the executor can validate early.
- **Unresolved:** a missing decision that changes the safe plan.

Ask about unresolved items only when their answer changes scope, architecture,
authority, or the next safe action. Avoid making the user decide implementation
details that repository inspection can settle.

## Consume the governing product specification

When a `project-specification` package governs the work, apply its
[specification-to-plan handoff](../../project-specification/references/spec-to-plan-handoff.md).
The specification owns dictated behavior, product boundaries, protected behavior,
and observable acceptance. The plan owns repository change design, technical
dependencies, execution ownership, test design, integration, and recovery.

Planning requires behavior that is decidable enough to choose a technical route;
it does not require a format-perfect or administratively approved specification.
Resolve or isolate a true product contradiction or material undecidable choice.
Carry a labeled working assumption to its earliest useful check, and repair a
broken reference locally without discarding usable behavior.

Use the `PLAN.md` step map as the sole behavior-to-work coverage index. Every
material governed behavior must reach at least one implementation block, and every
block must serve a governed behavior or a necessary technical prerequisite. A plan
may define internal contracts and prerequisites, but it cannot turn them into new
product requirements. Return any material product gap to the specification rather
than resolving it through a silent implementation preference.

## Map the affected architecture

Describe just enough current architecture to explain the proposed changes. Follow
the behavior across relevant boundaries:

- entrypoints and request/event sources;
- domain or business logic;
- state and persistence;
- public and internal interfaces;
- background jobs, queues, caches, or generated artifacts;
- UI state and user interaction;
- external services or live resources; and
- build, packaging, deployment, and observability paths.

For each material boundary whose behavior or contract can change, cover the
relevant owner, consumed and produced values, compatibility expectation, and
failure behavior. Omit dimensions that do not apply and untouched boundaries that
do not affect implementation. This prevents a locally plausible step from silently
breaking a downstream consumer without creating a boundary inventory.

Use a small table or flow only when it makes several dependencies clearer. Do not
draw a graph merely to prove that the plan is “topological.”

## Form implementation blocks

An implementation block is a coherent outcome that one executor can finish and
verify without an arbitrary handoff. Boundaries should follow behavior, ownership,
and dependencies—not line count, file count, or equal effort.

A strong block usually answers the relevant parts of this list:

- What behavior or capability is complete after this block?
- Which current path, component, or contract is changing?
- Which files, modules, classes, functions, schemas, configuration keys, or
  generated outputs are likely to change?
- What logic, state transition, data transformation, error handling, or fallback
  should be implemented?
- What remains compatible, and what consumers must change together?
- What inputs or prior decisions does the block require?
- Which later blocks consume its result?
- What focused check proves it?
- Which independently runnable tests form its fast test suite?
- After a localized correction or changed input, which completed work and check
  results remain valid, which focused checks must rerun, and where does execution
  resume?
- If it touches data or live state, how does rollout, rollback, retry, or cleanup
  work?

Write each block as one canonical `STEP-*` file using the
[modular plan template](modular-plan-template.md). The stable headings make the
plan easy to navigate and edit; they do not require boilerplate or repeated shared
context. A heading variation is a local formatting repair, while a missing
implementation dependency or undecidable acceptance claim is a substantive plan
gap. Keep that distinction explicit.

Reference the governed `BEHAVIOR-*` outcomes in the block and the root step map.
Do not force one step per behavior: split and join work according to technical
cohesion and dependencies while keeping the full behavior coverage visible once.

### Granularity test

A plan is too vague when the executor must still discover the core design. Replace
steps such as:

- “update the backend”;
- “wire up the UI”;
- “add validation”;
- “handle errors”; or
- “write tests”

with the actual integration points and behavior. For example, identify the handler
and service boundary, the request and response change, where validation runs, how
errors map to the public contract, which UI state consumes it, and which test
scenario observes the result.

A plan is too granular when it dictates obvious keystrokes, repeats source code,
assigns a separate step to each file, or freezes local implementation choices that
do not affect a contract, dependency, risk, or acceptance claim. Leave ordinary
coding judgment to the executor inside the stated behavioral boundary.

### Design a fast lane, not a second topology

Every step includes one compact fast-lane instruction. It covers both a repair
owned by that step and re-entry when a verified upstream correction reaches the
furthest step already in progress: retain unaffected outputs, correct at the owning
surface, invalidate only direct consumers, rerun their focused checks, and resume
at the earliest affected action.

Keep the same owner, session, workspace, and still-valid evidence unless a concrete
need makes reuse unsafe or impossible. The fast lane is not a separate agent lane,
role map, worktree plan, review cycle, or artifact. If changed-input impact cannot
be bounded, retained state is untrustworthy, or required authority or isolation is
missing, use the normal route. If the normal route is already minimal, one sentence
saying so is sufficient.

The default recheck is the affected portion of the step's fast test suite plus any
direct-consumer or integration check whose input changed. The full repository suite
is not the default fast-lane action.

## Apply relevant domain detail

Use these prompts selectively.

### APIs and service boundaries

- Specify endpoint, command, event, or public function changes.
- Describe request/response or message shapes, validation order, error mapping,
  idempotency, authentication/authorization, and compatibility.
- Name producers and consumers that must change together.
- Cover versioning or deprecation only if existing clients require it.

### Data and migrations

- State schema, constraint, index, serialization, or state-machine changes.
- Define migration order, old/new version coexistence, backfill or transformation,
  failure recovery, and rollback limits.
- Explain how partial progress is detected and safely resumed when that risk exists.
- Do not add snapshots, receipts, or hashes unless rollback, integrity, or audit
  actually consumes them.

### UI and interaction

- Identify the route, component, state owner, data dependency, and user action.
- Cover loading, empty, error, success, disabled, and retry states that the feature
  can actually reach.
- Preserve accessibility, keyboard behavior, responsive layout, and localization
  where the project or requested behavior requires them.
- State how the UI reflects authoritative server or local state and avoids stale or
  conflicting updates.

### Concurrency and background work

- Name the unit of concurrency, ordering guarantee, ownership of shared state, and
  duplicate or retry behavior.
- Describe cancellation, timeouts, cleanup, and idempotency when failures can leave
  partial work.
- Add locking or serialization only around a demonstrated shared mutation.

### Security and privacy

- Apply the actual trust boundary and threat model.
- Identify authentication, authorization, input handling, secret, data exposure,
  retention, and audit implications that fall inside scope.
- Do not turn every plan into a general hardening campaign. A real issue outside the
  governing scope may be noted without becoming a prerequisite.

### Performance and reliability

- Identify the concrete hot path, scale assumption, latency or resource budget, and
  measurement needed.
- Add caching, batching, retry, fallback, circuit breaking, or load testing only
  when a known requirement or observed risk warrants it.
- Avoid speculative infrastructure whose operation is more complex than the risk it
  is meant to reduce.

### Build, configuration, and deployment

- Name relevant flags, environment variables, manifests, generated outputs, CI
  jobs, release steps, and runtime dependencies.
- Distinguish source changes from generated or deployed projections.
- Define rollout order, compatibility window, observation, rollback, and cleanup
  for changes that cross a release boundary.

### Documentation

- Update user, operator, API, migration, or architecture documentation when its
  readers need the changed behavior.
- Do not create a changelog, report, handoff, or duplicate reference document solely
  because the plan has multiple steps.

## Order the work by real dependencies

Derive the sequence from consumed outputs:

1. Resolve a prerequisite only if a later step cannot proceed without it.
2. Define or update shared contracts before independent consumers implement against
   them.
3. Prefer an early executable path through the highest-risk shared seam when it can
   expose architectural mistakes cheaply.
4. Run independent implementation or verification work concurrently only after its
   inputs are stable.
5. Integrate in the order needed to keep the combined project buildable and
   diagnosable.
6. Place broad regression, rollout, or live checks after the smallest relevant
   integrated unit exists.

Distinguish a dependency from a preferred ordering. If two blocks do not consume
each other’s output and have safe write boundaries, say they may run in parallel.
If they share a contract or generated output, assign one owner or make the shared
change a serial predecessor.

## Design requirement-fit validation

Start with claims, not test categories. For each material behavior or governing
acceptance scenario, determine the cheapest observation that can distinguish
success from failure. Reference the product oracle in the specification; keep test
setup, fixtures, assertions, commands, and environment detail in the plan.

Verification may include:

- existing unit, integration, end-to-end, contract, or snapshot tests;
- new focused tests for changed behavior and discovered regressions;
- type checking, linting, compilation, schema validation, or static analysis;
- manual or visual checks where automation cannot decide the claim;
- performance or load measurements tied to an explicit budget;
- migration dry runs, rollback checks, or data readback;
- security-specific checks tied to the actual trust boundary; and
- live-environment validation only for behavior that cannot be established
  elsewhere.

For each proposed new test, specify:

- the meaningful setup or precondition;
- the action or input;
- the important observable or assertion; and
- the regression or requirement it protects.

Before assigning product repair from a failed check, compare the exact governing
requirement or contract, the observed product behavior, and the assertion that
failed. Classify the mismatch as a product defect, an oracle or test that demands
behavior beyond the contract, or genuinely unresolved. Repair the product only for
the first case. Correct an overstrong or self-confirming oracle without weakening
valid dictated behavior, and investigate only the missing fact when the result is
unresolved.

Test evidence must be capable of failing when the governed behavior is broken. For
a consequential or easy-to-fake seam, ask whether known-broken behavior could still
pass. Tests of mocks, source text, reference implementations, or caller-shaped
fixtures prove only that narrower surface unless they exercise the actual claimed
boundary. Apply these questions while designing ordinary validation; do not create
a separate audit, disposition record, or mandatory reviewer.

Use exact commands only after confirming them in repository tooling or docs. Separate
commands that can run independently, but do not invent a scheduling framework for
ordinary checks.

Define sufficient evidence for each required behavior; do not make development
success depend on every available check, report, warning, or unrelated repository
surface being perfect. Apply the skill's
[requirement-fit classification](../SKILL.md#validate-requirement-fit-not-literal-perfection)
to adverse results and state which claim or consumer each result can actually
invalidate.

If a repository or release process requires an exhaustive gate, identify that gate
and its consumer separately from the behavioral evidence it consumes.

### Define the fast test suite

Every step must identify a fast test suite that exists by step completion. This is a
reusable execution subset, not another evidence report or acceptance gate. It must:

- name existing or planned test files, cases, selectors, targets, smoke checks, or
  confirmed commands rather than saying “run relevant tests”;
- be independently runnable without launching unrelated repository verification;
- detect failure of the step's material behavior and changed boundaries, including
  a focused integration check when a local unit check cannot observe the seam; and
- make the invalidation boundary usable: a reviewer can tell which suite entries
  and direct-consumer checks must rerun for a particular changed input.

A single focused test can be the suite for a small outcome. Do not impose a test
count or arbitrary runtime budget. “Fast” means scoped and independently selectable,
not shallow. Reuse repository-native test selection and reference shared tests from
multiple steps rather than copying them. If a suitable subset does not exist, plan
the smallest tests or target needed to create it; do not commission a generic
runner, matrix, dashboard, or separate suite artifact.

### Schedule substantial verification by dependencies and resources

Apply this only when verification contains multiple coordinates with meaningful
execution cost, stateful resources, dependencies, or repeated repair risk. An
ordinary focused check or small fast suite needs no matrix machinery.

- Run isolated deterministic local checks concurrently up to actual host capacity,
  considering CPU, memory, process fanout, and observed contention. Agent slots,
  writer count, and live-provider quotas are not their concurrency ceiling.
- Isolate stateful local checks by the files, ports, caches, fixture stores, and
  child processes they consume. Serialize only a demonstrated resource conflict or
  named prerequisite.
- Apply service, hardware, credential-home, or provider quotas only to checks that
  consume that live resource. A local fake does not consume a live-provider slot
  merely because it represents that provider.

Schedule graph-ready coordinates whenever both their prerequisites and resources
are available, refilling capacity as work finishes instead of waiting for a whole
wave. An ordinary coordinate failure ends that coordinate, not the entire matrix;
continue every independent feasible coordinate and collect the resulting failures
before repair. When an incompatible terminal state makes a success observation
unreachable, stop that wait and perform its bounded cleanup without cancelling
independent checks.

Use an existing runner's supported parallel mode or stable shards only when the
saved time exceeds startup and fixture cost. Confirm that the actual runner can
provide the promised isolation, scheduling, results, and cleanup. If it cannot,
state the limitation and plan the smallest prerequisite only when its payoff is
concrete. Do not create a scheduler framework, mandatory matrix artifact, timing
ledger, or new runner for ordinary checks; test count alone does not trigger this
guidance.

### Avoid duplicated evidence

One test result may support several consumers. Refer to it; do not copy it into
separate evidence packets. Run a check again only when:

- a consumed input changed;
- the earlier environment or setup does not cover the required boundary;
- nondeterminism requires a justified sampling strategy;
- a release or policy explicitly requires a fresh run; or
- the prior result is missing or not trustworthy.

Do not rerun unaffected checks after a documentation or report correction. Do not
require every platform/environment combination when representative coverage proves
the claim, and do not use representative coverage when the contract is genuinely
platform-specific or exhaustive.

## Plan realistic risk and recovery

Include risks that can change the implementation or execution route. For each,
state the trigger or observation, impact, prevention or mitigation, and recovery
action. Name a separate owner only when responsibility differs from the delivery
owner. Avoid generic risk lists.

Useful categories include:

- incompatible interface or schema changes;
- partial migrations or rollout/version skew;
- shared-file or generated-output conflicts;
- data loss, duplicate effects, or unrecoverable external actions;
- weak or unavailable acceptance evidence;
- scarce environment or hardware access;
- security or privacy boundary mistakes; and
- integration behavior that local checks cannot observe.

A failed step should block only consumers of its missing result. Preserve independent
work and passing evidence. When the current approach stalls, change the assumption,
ownership, seam, oracle, or implementation strategy before retrying; a renamed copy
of the same plan is not a recovery.
