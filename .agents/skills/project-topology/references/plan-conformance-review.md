# Adversarial review of plan scope, simplicity and skill conformance

Apply this review to every admitted Level 1, 2, 3 or 4 plan, including compact
and no-harness plans and direct use of the formal compiler. Level 0 remains an
out-of-scope verdict, not a reason to launch a reviewer. This is the broader
mandate of the existing independent planning review: include the
[test-scope audit](test-scope-audit.md) and applicable
[matrix execution](matrix-execution.md) checks in that same assignment.
Do not add an execution lane, another review loop, or a higher execution tier
merely to review the plan.

## Freeze the actual assignment before designing the topology

Record the requested deliverable and acceptance claims in the user's terms,
explicit exclusions, any user-selected tier or constraints, and which execution
actions are already authorized. Distinguish implementation, verification,
launch/initial health, and completion of a live campaign. Permission for one does
not silently authorize the others. Cite the relevant request and governing
requirement rather than relying on the planner's paraphrase alone.

Inspect specifications and surrounding documents for constraints on that
deliverable. Their descriptions of a larger research program, deployment,
migration or operational campaign do not automatically become requested outcomes.
Keep a material stage only when it implements a requested outcome, satisfies a
binding requirement on that outcome, or is a necessary dependency with an explicit
causal justification. A document title, available resource, ambitious background
goal or preferred topology is not that justification.

Put plausible later work in existing non-goals/optional-operation text, with its
own activation and authority boundary. Do not make it an implementation acceptance
gate unless the requested claim actually requires it. Do not remove real safety,
compatibility, functional coverage or other binding requirements to make a plan
look smaller.

## Give the independent reviewer a concrete adversarial question

Supply the original request and relevant follow-ups/authorizations, applicable
repository and skill instructions, the draft plan, acceptance sources, selected
tier rationale, and verification/cost bindings. The reviewer must inspect these
sources, not only the plan writer's summary. It remains read-only: inspect the
plan and supporting artifacts, but do not implement, run product tests, allocate
live resources, launch the planned workers, or accept the project.

Ask: **Could this plan obey its own internal graph yet violate the user's request
or the skill's rules? What is the smallest complete correction?**

Review these dimensions together, using existing plan fields and references:

| Dimension | Required challenge and evidence |
| --- | --- |
| Outcome and stage traceability | Map every material stage, artifact, prerequisite and gate to the request or a necessary dependency. Reject a broader campaign substituted for a bounded delivery. Identify the exact unsupported scope rather than declaring the plan generally too complex. |
| Governing authority and skill rules | Distinguish binding constraints from background context and planner assumptions. Check applicable admission, ownership, tier, gate, recovery and no-execution rules against actual plan behavior. For formal plans, consume and challenge the existing R/S and V matrices; a claimed PASS is not proof. |
| Lowest sufficient tier and real lanes | Compare the chosen shape with the cheapest adequate alternative. At Tier 1, challenge unsafe solo assumptions; at Tier 2, bound the evidence lane; at Tier 3, prove disjoint implementation ownership; at Tier 4, justify durable coordination and any permitted sub-orchestrators. Agent availability and matrix size do not establish need. |
| Simplicity and coordination cost | Identify the risk or dependency each role, schema, harness, gate, handoff and repeated review removes. Compare startup, context, integration and maintenance costs with the benefit. Remove or defer only unjustified structure; do not impose a deletion quota or weaken required formal schemas. |
| Verification necessity and strength | Map each acceptance claim to concrete assertions and the boundary they observe. Distinguish local deterministic, integration/dry-run, hardware and live-environment evidence. Add or strengthen missing proof; reject stronger-than-required or duplicate campaigns. A mock cannot establish a property requiring real execution. |
| Time, resources and stopping | Review setup, execution, cleanup, concurrency and dependency costs for every material verification stage. Epoch/job counts alone are not wall-clock budgets. Require honest estimates or uncertainty, a bounded qualification when needed, finite-test stop conditions and the requested stopping point; never turn them into agent-session deadlines. |
| Execution authority and handoff | Trace implementation, expensive/live commands and external mutations to current authorization. Planning approval, a gate label or a printed command is not authorization. Make unapproved operations unreachable until their explicit activation condition is met; preserve existing authorization without asking for it again. |

A user-selected tier constrains topology, not product scope. Honor it where a
valid lean composition exists and state if a lower tier would otherwise suffice.
If its required structure cannot be justified within the requested work, report
that concrete conflict and offer the lower-tier alternative; do not silently
downgrade, manufacture lanes, widen the outcome, or label an invalid requested-tier
plan ready. The formal compiler's fixed-package requirements remain binding once
selected; simplify the actual work and optional choices without inventing a
reduced schema.

## Findings, dispositions and acceptance

Use the existing reviewer identity, evidence location and bounded feedback:
one complete initial review, then one focused follow-up when the plan or
dispositions materially change. Reuse an already independent review only when it
actually covered these dimensions. A review of test counts alone is insufficient.

Each finding names the affected stage/field, governing request or rule, concrete
violation or uncertainty, smallest correction, acceptance claims preserved, and
cost effect when relevant. Return an explicit reviewer verdict: PASS or BLOCK,
with reasons. A blocker includes unsupported scope, an unjustified topology,
missing required evidence, reachable unauthorized execution, or a material
unresolved authority/cost constraint. Preserve the actual reviewer verdict and
findings in the review evidence; do not rewrite them to manufacture agreement.

The writer adjudicates each finding and changes the owning artifacts. Use the
existing dispositions, plus ACCEPT-SIMPLIFY, ACCEPT-DEFER and REJECT-EVIDENCE when
needed for non-test findings. A rejection requires source/evidence showing why
the finding does not apply; preference or a desire to proceed is not enough.
ROOT resolves remaining disagreements within its authority, including a specific
reason for rejecting a reviewer finding. It cannot waive a binding requirement,
invent execution permission, or accept a valid unresolved blocker.

Record the final adjudicated Plan review verdict as PASS only when the final
artifact conforms, every material finding has a disposition, and required scope,
coverage and authority boundaries are established. Otherwise use BLOCK or PENDING
and report the plan incomplete. Final adjudication is not a claim that the reviewer
changed its verdict. If an independent reviewer is unavailable, retain the draft
and disclose the missing review rather than substitute self-review or fabricated
evidence. The review-round limit does not waive a blocker.

For compact Levels 1-4, put the concise review result in the existing verification
section: requested outcome/non-goals, scope/authority assessment, topology/simplicity
assessment, verification/budget assessment, execution authorization boundary,
reviewer evidence, dispositions and final verdict. No new file or table is needed.
For formal output, populate the expanded audit metadata in
[test-scope audit](test-scope-audit.md#record-and-validate-without-another-package)
under validation.md Section 16. Keep detailed truth, stages, costs and permissions
in their existing authoritative artifacts and reference them from the audit.
A structural validator checks declarations, not semantic alignment or permission.

Reopen only the affected review dimensions when later changes expand outcomes,
change authority, invalidate lane independence, add material gates/resources/cost,
or weaken required evidence. Do not repeat a full plan audit for harmless wording
or unchanged accepted work.

## Keep plan acceptance separate from execution

This skill ends at the reviewed planning artifact. Its sole agent-dispatch
exception is the independent planning review described above; extending the review
does not authorize project execution.

The plan's executor handoff must state: accepted deliverable and non-goals, final
review verdict, already-authorized actions and their source, conditional operations
and their missing trigger/authority, and the point at which execution must stop.
A later executor reconciles these against the current user request before acting.
When implementation/execution is already authorized, continue within that authority
using the ordinary execution workflow; do not demand redundant confirmation.
When only planning was authorized, do not start implementation. Authorization to
implement does not by itself authorize an experimental campaign, deployment or
other distinct live operation. Ask only for genuinely missing authority immediately
before dependent work; continue independently authorized work.

A conditional future operation may remain in a sound plan without present launch
authority if it is explicitly gated and cannot block or expand the separately
accepted implementation outcome. It is not executed merely because it appears in
the plan. If live evidence is actually required for an acceptance claim, keep that
claim unverified until the authorized operation establishes it; never relabel CPU
or synthetic evidence as a live pass.

## Semantic checks for this review

- A request to correct a trainer and implement a safe two-device queue gains a
  comparator study, long calibration, live smoke campaign and full research screen:
  BLOCK the scope expansion unless each addition is required by the request or a
  demonstrated dependency. Preserve focused trainer/queue/cleanup tests. Consider
  a lower tier if sufficient; do not override an explicit tier without resolving it.
- A request includes launching two queue lanes and checking initial worker health:
  bind that authorized launch and stopping point; do not wait for training completion
  unless requested. A planning-only invocation still hands off rather than launching.
- A request requires a measured device-performance result: do not remove the real
  measurement as unnecessary merely because local tests are cheaper. Plan its
  resources, cost and authorization honestly.
- A small Tier 1 plan has an adequate single execution owner: use the independent
  planning reviewer without inventing a second implementation lane or promoting it.
- A user requests Tier 3 but the writes overlap one shared contract: BLOCK the claimed
  lane independence; stage the shared work and prove any remaining independent lanes,
  or report that a lower-tier alternative fits. Never add unrelated work to fill lanes.
- A formal Tier 4 plan is overbuilt: simplify justified optional choices and scope,
  while preserving mandatory package, gate and fast-lane contracts.
