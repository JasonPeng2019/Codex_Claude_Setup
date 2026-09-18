# Audit test scope before plan acceptance

This is a planning-time independent review of every proposed suite, matrix, and
step-end verification surface. It applies after a significant plan's evidence design
exists and before final acceptance; it does not execute the planned project.

## Establish functional coverage, then remove redundant work

Functional adequacy comes first; economy is a constraint on how to prove it, not
permission to lower the acceptance bar. The objective is reliable required
behavior, not the fewest tests or the fastest green run. No finite suite guarantees
all behavior; report what is established and what remains uncertain. Add or
strengthen checks when the existing evidence cannot decide a required claim.

Before trimming, trace each in-scope required behavior and material failure risk
to concrete assertions. Cover applicable normal operation, refusal/invalid input,
boundary conditions, state transitions, failure recovery and cleanup. Include
concurrency, persistence and cross-component interactions where the contract or
observed defects make them relevant; do not manufacture a universal Cartesian
matrix or a quota of cases. A family label or PASS cell is not an assertion map.
For a grouped case, distinguish its individually required observations so an
unexecuted recovery or failure path cannot disappear behind its happy-path PASS.

Audit evidence strength as well as presence. Does the assertion observe the actual
implementation and boundary claimed, with an independently derived expected
outcome? Could the known broken behavior still pass it? Helper mocks, source-string
checks and tests of reference models/oracles prove only those narrower things;
they do not alone prove the caller sequence, installed artifact, OS interaction
or provider integration. For changed high-risk seams, retain both the motivating
failure and the adjacent valid/recovery behavior, using real local boundaries
with controlled fault injection where practical. Existing trustworthy evidence
can satisfy these obligations; no blanket mutation-testing campaign is required.

Map each selected test or coherent test family to an accepted product requirement
or concrete material risk and its observation oracle. Group equivalent cases instead
of creating thousands of paperwork rows. Name matrix dimensions, their cardinalities,
applicability exclusions, interaction risks and resulting case count. Explain the
distinct confidence each dimension and each repeated suite adds. Include construction,
execution and repair cost, likely wall-clock range, external cost and estimate basis;
record uncertainty honestly when measurements do not exist.

Use the cheapest trustworthy evidence that decides the required behavior. Consider
existing checks, local deterministic failure injection, representative equivalence
classes, pairwise coverage and adapter-specific integration before a full Cartesian
product. Sampling requires an explicit equivalence/interaction argument tied to the actual
implementation path, state and environment, plus retained tests that would expose
the relevant faults; absence of a previously seen failure is not that argument.
When equivalence cannot be established, keep the affected cases.
Pairwise testing is not automatically sufficient. Preserve required security,
data-integrity, lifecycle, concurrency and compatibility coverage. Cheap broad suites
can be appropriate; a high test count alone does not establish waste.

An oracle must not silently require stronger behavior than the accepted contract.
Separate product correctness, provider compatibility and control validity. Correct
containment of a misbehaving provider can prove a harness invariant while leaving a
provider-specific capability undecided. Use live providers only for claims that need
their actual integration; use deterministic fixtures for prescribed malformed-output
sequences where that suffices. Do not mistake an unavailable observation for PASS.

Distinguish a binding exhaustive-test requirement from a planner's interpretation of
words such as "complete" or "comprehensive". A binding user/spec/repository requirement
stays unless its governing authority changes it. Recommend a change when justified,
but do not silently trim required cells. ROOT may resolve planning choices within its
authority; it cannot waive a user requirement. This audit neither removes the formal
package's fixed rules, gates or fast-lane paths nor permits weaker product acceptance.

## Independent review and disposition

For substantial matrices, also audit the complete
[matrix execution contract](matrix-execution.md), not only counts and assertions.
Require the coordinate dependency/resource graph, implemented runner controls,
terminal exits, complete collection, cause-group repair and affected-rerun rules,
and per-coordinate/total wall-clock budgets with their basis. Reject unnecessary
serialization, long waits after incompatible terminal states and per-test repair
loops. Use the same reviewer, bounded feedback and existing audit tables; include
schedule/control findings in their cost, findings and disposition fields.

1. The writer supplies the draft plan, authoritative acceptance sources, suite/family
   inventory with dimensions and cost, and the exact proposed verification boundaries.
   Reuse existing plan fields; do not commission another evidence database or scheduler.
2. Dispatch a separate read-only reviewer, independent of the draft writer. Give it all
   suites and step-end surfaces, the relevant source contracts, and a bounded question:
   which required behavior could still be broken while these checks pass, and which
   evidence is missing, stronger than required, duplicated or unnecessarily expensive?
   Inspect representative concrete assertions and callers when available, not just
   matrix counts. It may recommend adding tests or retaining everything. Never
   require a removal quota.
   Reuse an independent plan-review assignment when it can cover this scope explicitly.
   The reviewer may inspect artifacts but cannot edit, execute product tests, launch
   project workers, alter requirements, or make final acceptance decisions.
3. Require specific findings: affected suite/family/dimension, source requirement and
   assertion, redundant or missing evidence, suggested change, retained coverage and
   estimated cost effect with uncertainty. Inspect cross-step duplication as well as
   each individual matrix. Test authoring and later runtime selection remain separate
   from this planning review.
4. The writer validates every criticism. Record ACCEPT-ADD, ACCEPT-STRENGTHEN,
   ACCEPT-REMOVE, ACCEPT-MERGE,
   ACCEPT-SAMPLE, ACCEPT-REPLACE, ACCEPT-SCHEDULE, REJECT-REQUIRED, or UNRESOLVED with reasons. Rejection
   cites the required claim or concrete risk and why the proposed cheaper evidence is
   insufficient. Apply accepted changes to the owning plan fields/cards and update the
   requirement-to-evidence map, counts, costs and invalidation boundaries. Findings
   remain advice until adjudicated; do not trim automatically to obtain reviewer PASS.
5. Use one complete initial review and, when the draft or dispositions change, one
   focused follow-up covering those changes and retained coverage. Send remaining
   disagreement to ROOT for an explicit evidence-based decision, rather than restarting
   the review. ROOT may be the plan writer but cannot be the independent reviewer.
   A review-round limit ends automatic back-and-forth; it never waives a required claim.
   A materially new scope or risk can justify a newly bounded review of that delta.
6. ROOT accepts the final scope only after every finding has a disposition, every
   required claim has adequate evidence planned, and no material coverage hole is
   hidden by grouping, sampling or reused credit. Additions need the same specific
   claim, oracle, boundary and cost justification as removals. If review is unavailable
   or a material requirement remains
   unresolved, retain a draft and report planning validation incomplete. Do not invent
   a reviewer result or silently substitute self-review. No user confirmation is needed
   for ordinary within-authority trimming.

The runtime cards consume the accepted scope and may not silently expand or weaken
it. A new uncovered risk returns to ROOT. Preserve unaffected test credit and rerun
only evidence invalidated by changed inputs under the existing verification rules.
After concrete tests are authored, use the existing asset review/readiness stage to
check their actual assertions and execute realistic new/changed control branches
before expensive reuse. That targeted readiness work is planned here, not performed
by the planning reviewer, and does not repeat the full scope audit.

## Record and validate without another package

For compact plans, record the reviewer identity, reviewed surfaces, findings,
dispositions and final ROOT decision in the existing verification section. For formal
plans, retain evidence selections in their existing owning cards/manifests; add the
following two tables under `validation.md` Section 16. They are review results and
references, not a second definition of execution policy. Do not add a module, policy
ID, V-check ID, runtime role, or package file for this planning audit.

| Audit field | Value |
|---|---|
| Plan writer | Actual writer agent/session identity |
| Independent reviewer | Actual separate reviewer agent/session identity |
| Review evidence | Readable review response reference and follow-up reference, or explicit unchanged-scope reason why no follow-up was needed |
| ROOT acceptance | ROOT decision reference accepting the final revised scope and resolving every material disagreement |
| Audit status | ACCEPTED |

| Step | Evidence scope | Requirement and oracle | Dimension rationale | Cost basis | Review findings | Writer disposition | Final status |
|---|---|---|---|---|---|---|---|
| STEP-001 | References to every suite/family/card in all three entry paths of this step | References to governing claims and assertions | Counts, exclusions and distinct interaction risk, or concrete reason no cross-product applies | Runtime/external/build cost range and estimate basis, with uncertainty | Actual findings, or explicit no-material-findings result; include cross-step duplication | Disposition of every finding with coverage justification and final owning artifact references | ACCEPTED |

Emit exactly one coverage row per STEP; a row can reference the existing complete
family inventory instead of copying its cases. Include operation-only steps with
their readback/check scope. No hard field accepts an empty or N/A waiver. Use
PENDING while drafting and ACCEPTED only after adjudication on the final scope.

The formal validator checks table shape, separate declared writer/reviewer identities,
all indexed STEP rows, populated evidence/cost/disposition fields and accepted status.
It cannot authenticate a reviewer, prove coverage completeness, evaluate oracle
soundness or certify minimum cost. The plan writer and ROOT must inspect the actual
review and final artifacts; plausible table text is not evidence that an audit ran.
Existing formal plans require this audit on their next compilation/amendment before
claiming validation under the updated skill. Do not fabricate retrospective approval
or invalidate already accepted product evidence merely because the plan schema changed.
