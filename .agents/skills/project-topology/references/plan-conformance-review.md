# Adversarial review of plan scope, simplicity and skill conformance

Apply this review to every admitted Level 1, 2, 3 or 4 plan, including compact
and no-harness plans and direct use of the formal compiler. Level 0 remains an
out-of-scope verdict, not a reason to launch reviewers. Use four focused,
independent reviewer agents, each responsible for a related group below. All four
must approve before the plan is ready; a single catch-all review is insufficient.
Include the [test-scope audit](test-scope-audit.md) and applicable
[matrix execution](matrix-execution.md) checks under their designated owners.
These are planning reviews, not execution lanes or a reason to raise the execution
tier. At small tiers keep each review short and specific; do not create new project
work, a matrix, a harness or a formal package just to occupy a reviewer.

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

## Give each independent reviewer a focused adversarial question

Supply the original request and relevant follow-ups/authorizations, applicable
repository and skill instructions, the draft plan, acceptance sources, selected
tier rationale, and verification/cost bindings. Each reviewer must inspect these
sources, not only the plan writer's summary. It remains read-only: inspect the
plan and supporting artifacts, but do not implement, run product tests, allocate
live resources, launch the planned workers, or accept the project.

Ask: **Could this plan obey its own internal graph yet violate the user's request
or the skill's rules? What is the smallest complete correction?**

Before dispatch, instantiate the [review assignment](../assets/plan-review-assignment.md)
with the raw sources, frozen candidate, assigned surfaces and expected return. Each
reviewer performs its assigned [acceptance-design](acceptance-design.md) decisions;
an instruction merely to "review the plan" or count checks is insufficient. Preserve
open findings and independent judgment; specify the questions, not their answers.

### Assign four related review groups

| Review group | Owned decision and required challenge |
| --- | --- |
| SCOPE_AUTHORITY | Outcome/stage traceability, binding versus background authority, non-goals, reachable execution permissions and executor stopping point. Does every material stage serve the actual request, and can anything run beyond its authorization? |
| TOPOLOGY_SIMPLICITY | Lowest sufficient tier, explicit tier constraints, genuine lane independence, ownership/delegation, gates and recovery structure, coordination cost, admission and structural skill conformance. Is this the smallest complete valid topology for that outcome? |
| VERIFICATION | Functional sufficiency, concrete assertions, independent oracles, failure/recovery coverage, evidence boundaries, necessary versus redundant test dimensions and retained credit. Could required behavior remain broken while this evidence passes? Own the functional portions of the test-scope audit. |
| EXECUTION_RESOURCES | Dependency/resource graph, actual runner capabilities, isolation and concurrency, terminal exits, collection before cause-group repair, affected reruns, setup/cleanup, wall-clock budgets and operational stop handling. Is the proposed schedule executable, bounded and economical while preserving the selected evidence? Own the matrix-execution contract and scheduling portions of the audit. |

Use four distinct agent/session identities, all different from the plan writer.
One agent reviewing four prompts is not four independent approvals. ROOT assigns
each group directly and receives its result; reviewers are terminal read-only
workers, do not supervise one another, and do not approve their own authored plan.
This flat planning panel applies in both workspaces. It does not remove the
multi-agent workspace's separately justified execution sub-orchestrators or permit
them in the generic workspace.

Give all groups the same frozen candidate revision and raw authority sources, plus
their focused mandate and relevant artifacts. A revision is an unambiguous existing
commit, snapshot or draft identifier; no new hashing/provenance system is required.
Run independent reviews concurrently where slots allow, otherwise in bounded waves
on that same snapshot. Slot limits do not permit merging reviewer identities or
waiving a group. Collect all feasible reviews before revising the draft; one BLOCK
does not cancel other independent reviews. No reviewer must perform the other
three full audits. Each still flags discovered cross-group contradictions and names
the owning group; ROOT routes the issue for that group's explicit disposition.

TOPOLOGY_SIMPLICITY must assess execution tier separately from plan organization.
A request for modular output, independent sections/files or `STEP-*` names alone
cannot justify Tier 4 or the formal package. Inspect the stated coordination need
or actual explicit/project-workflow framework selection. Accept proportionate
lane-owned Level 3 organization and normally compact Level 2 plans; do not force
extra roles or formal schemas to justify their file split. Once the full formal
framework is selected, preserve all its required paths, cards, recipes and checks.

TOPOLOGY_SIMPLICITY also applies [Change locality](change-locality.md). Inspect the
editable source and one concrete private-change boundary: identify the owning fact,
stable public interface and actual consumers. Reject independently maintained copies
that force unrelated edits, not the existence of automatically generated indexes.
VERIFICATION and EXECUTION_RESOURCES assess real evidence and resource consequences;
a generated-file diff alone does not establish that every contained unit changed.

All groups apply the relevant skill rules within their boundary. TOPOLOGY_SIMPLICITY
checks that the ownership map covers every applicable planning rule, including the
formal R/S and V matrices, without becoming a second reviewer of every detail.
Cross-group changes require all affected owners: for example, removing live
calibration needs SCOPE_AUTHORITY to establish necessity, VERIFICATION to retain
required proof, and EXECUTION_RESOURCES to revise resource/cost bindings.

For ordinary short verification with no matrix, EXECUTION_RESOURCES can approve a
brief assessment of the actual commands, dependencies, cost and stopping boundary,
explaining why matrix controls are inapplicable. This is an evidenced PASS, not an
N/A waiver. The other groups likewise scale depth to the actual plan.

The following detailed obligations remain binding under those group assignments:

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

For each group, record its actual reviewer identity, reviewed revision, inspected
surfaces, findings/dispositions, evidence location and explicit PASS or BLOCK.
PENDING denotes an absent or unfinished review, never approval. Each finding names
the affected stage/field, governing request or rule, concrete violation or
uncertainty, smallest correction, acceptance claims preserved, and cost effect when
relevant. A blocker includes unsupported scope, unjustified topology, missing
required evidence, reachable unauthorized execution or unresolved material cost.
Preserve actual reviewer responses and dissent; do not rewrite them into agreement.
Include each group's assigned necessity, multiplicity or proportionality assessment
with claim/activity references and concrete reasoning. The panel must cover all
three questions. BLOCK material unsupported acceptance work, multiplication or
machinery even when the plan is structurally valid; also BLOCK missing required proof.
High count/cost alone is not a defect, and a cheaper choice must preserve required claims.

The writer assesses each finding and changes the owning artifacts. Retain existing
test dispositions and ACCEPT-SIMPLIFY, ACCEPT-DEFER and REJECT-EVIDENCE for other
findings. A rejection cites source evidence, not preference. ROOT resolves factual
conflicts and chooses within-authority corrections, but cannot turn a reviewer's
BLOCK into PASS. The owning reviewer must assess the response and explicitly
approve the resolved result. No majority vote, merged summary, structural-validator
PASS, ROOT acceptance or missing response substitutes for any group's approval.
Do not replace a dissenting reviewer to shop for approval. If a reviewer becomes
unavailable, a replacement independent agent must inspect its scope, prior findings
and their dispositions; report the replacement and its actual assessment.

Use one complete initial review per group and at most one focused follow-up per
group for the collected revisions/dispositions. If material disagreement remains,
retain BLOCK and report the concrete unresolved issue instead of looping until
approval. A genuinely new scope/risk may justify a newly bounded delta review;
the round limit never waives a blocker or an approval. Reuse prior independent
reviews only if their identities, group coverage, revision and actual approvals
satisfy this contract; a former catch-all review supplies at most one group.

Bind every group's approval to the final candidate revision. After changes, obtain
focused reapproval from affected groups. Unaffected groups may give a short explicit
carry-forward confirmation naming the final revision and unchanged reviewed scope;
they need not repeat the full audit. A carry-forward-only confirmation is bookkeeping
within that review, not another substantive follow-up. If the reviewer finds changed
assumptions, use the affected-group review route and its existing round limit. The
writer cannot issue the confirmation for them. Harmless wording does not require another full review, but neither a stale
revision nor an unconfirmed writer claim counts as final approval. Cross-group
contradictions or changes to outcomes, authority, lanes, gates, resources, costs or
evidence invalidate all approvals whose reviewed assumptions changed.

Record Plan review verdict PASS and ROOT acceptance only after all four distinct
reviewers approve the final revision, every material finding is resolved, and ROOT
checks that the results are mutually consistent. ROOT can withhold acceptance for
an unresolved seam even when all groups say PASS; route the seam to its owners.
Any BLOCK leaves the plan blocked; any missing, stale or PENDING group leaves it
incomplete. Never substitute self-review or fabricate evidence when agents are
unavailable. Plan approval remains separate from permission to execute.

For compact Levels 1-4, record the four group results concisely in the existing
verification section, with writer/reviewer identities, final revision, evidence,
dispositions, outcome/non-goals, scope/authority, topology/simplicity,
verification/budget assessments and execution boundary. No extra file is needed.
For formal output, use the metadata, group-approval and per-STEP tables in
[test-scope audit](test-scope-audit.md#record-and-validate-without-another-package)
under validation.md Section 16. Keep authoritative facts in their existing owning
artifacts. The structural validator checks declarations, not reviewer authenticity,
semantic adequacy or live authorization.

## Keep plan acceptance separate from execution

This skill ends at the reviewed planning artifact. Its sole agent-dispatch
exception is the four independent planning reviews described above; splitting the review
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
  planning panel with four short scoped approvals, without inventing execution lanes or promoting it.
- A user requests Tier 3 but the writes overlap one shared contract: BLOCK the claimed
  lane independence; stage the shared work and prove any remaining independent lanes,
  or report that a lower-tier alternative fits. Never add unrelated work to fill lanes.
- A formal Tier 4 plan is overbuilt: simplify justified optional choices and scope,
  while preserving mandatory package, gate and fast-lane contracts.
