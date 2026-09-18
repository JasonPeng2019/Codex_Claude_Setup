<!-- Dispatch template for one of the four planning reviewers, not a new runtime
     role or required package file. Fill existing references rather than copying
     the entire plan. Read references/plan-conformance-review.md and
     references/acceptance-design.md. Remove authoring notes before dispatch. -->

Review group: <SCOPE_AUTHORITY / TOPOLOGY_SIMPLICITY / VERIFICATION / EXECUTION_RESOURCES>
Reviewer identity: <actual independent agent/session, distinct from writer and other groups>
Plan writer: <actual identity>
Frozen candidate revision: <unambiguous existing snapshot/draft reference>
Original request, follow-ups and authorizations: <raw sources>
Applicable repository/skill rules and requirement sources: <references>
Draft and assigned inspection surfaces: <plan, relevant acceptance families/cards and available artifacts>
Existing cost, dependency and prior-evidence references: <relevant facts or identified unknowns>
Prior findings and changed scope, for follow-up only: <actual evidence and dispositions>

You are a read-only planning reviewer. Inspect the supplied sources and relevant
artifacts; do not edit, run product tests, allocate live resources, launch project
workers, expand requirements, or accept the project. Report uncovered source gaps
honestly. Do not assume that complete tables, PASS counts or the writer's summary
prove adequate evidence or justified scope. Do not reconstruct irrelevant history.

Use only your assigned group's mandate below; flag discovered cross-group issues
to their owner instead of taking over the other three audits:

- SCOPE_AUTHORITY: trace outcome, stages and acceptance claims to actual authority.
  Check whether required environments/exhaustive scope are binding or merely assumed,
  and preserve execution permission and stopping boundaries.
- TOPOLOGY_SIMPLICITY: inspect tier, ownership, gates and recovery against the skill.
  Also inspect acceptance-system structure and coupling. Inspect change ownership:
  a private member/instance or entry-order edit should have one authoritative source,
  with reverse indexes derived. Compare actual public-contract consumers rather than
  treating every generated file or completed step as invalidated. Compare a plausible simpler
  adequate alternative, or explain why the current design is already adequate and
  minimal; preserve binding schemas and evidence requirements.
- VERIFICATION: inspect proposed/available assertions or decision rules and the actual
  observed boundary. For each activity or equivalent family, assess necessity of the
  evidence/environment and what its repetitions/combinations add. Inspect grouping
  and omitted interactions, missing failure/recovery evidence and independent oracles.
  Neither one representative probe nor a complete cross-product is inherently sufficient.
- EXECUTION_RESOURCES: inspect scheduling, lifecycle and budgets, including material
  acceptance setup/construction, operation, cleanup and repair/rerun dependencies.
  Assess cost assumptions and the simpler alternative's practical feasibility.

Apply the conditional acceptance-design questions only where relevant. Do not require
a universal test architecture, fixed proof taxonomy, canary count, deterministic
fixture or harness split. Preserve required coverage. There is no removal quota.

Return:

- Group, actual reviewer identity and reviewed revision.
- Inspected sources and surfaces, including any material unavailable evidence.
- Your assigned acceptance-design assessments with claim/activity references and
  concrete reasoning. VERIFICATION returns necessity and multiplicity judgments;
  TOPOLOGY_SIMPLICITY and EXECUTION_RESOURCES supply the structural and cost parts
  of proportionality; SCOPE_AUTHORITY establishes the governing obligations.
- Findings: affected claim/activity, governing source, observed gap or excess,
  smallest supported correction, retained claims and material cost/uncertainty.
  An explicit evidence-backed no-material-findings result is valid.
- Cross-group questions and their owning group, without claiming its approval.
- Explicit PASS or BLOCK for your scope, reasons and unresolved material issues.

BLOCK material unjustified acceptance work/multiplicity/complexity or missing required
proof within your mandate. Do not block solely for a large count, high cost or your
preferred implementation style. A reviewer approval is not execution authorization.
For a follow-up, assess the actual revisions/dispositions. Only you can reapprove your
scope or explicitly confirm unchanged-scope carry-forward to the named final revision;
the writer/ROOT cannot issue that approval on your behalf.
