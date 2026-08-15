# Incremental verification and batch repair

Use this reference when a plan contains a multi-check gate, a costly safeguard, a practical/hardware
attempt, or `FAST_LANE_V2`.

For a newly compiled or amended plan that selects an expensive multi-check gate, accumulated
safeguard, stateful practical/hardware validation, or `FAST_LANE_V2`, put
`CHECKPOINTED_VERIFICATION_V1` in Section 0. It is a plan-level protocol selector for the validator,
not a runtime ID, hash, or evidence requirement. Legacy plans remain subject to their accepted
contract until explicitly amended.

## Checkpointed verification contract

Compile a selected expensive gate as an ordered set of the smallest independently runnable check units
that saves more rerun time than it adds in setup. Do not make one process per individual test merely
to claim resumability. When an existing runner cannot resume at a useful unit boundary, select the
smallest prerequisite or verification-asset work needed to expose that boundary before promising
incremental execution.

For each unit, the task card must state:

1. the command/operation and result owner;
2. source, configuration, runner, environment, fixture, and external-state inputs that can affect it;
3. prerequisites and dependent units;
4. the exact pass-reuse condition;
5. the result location only when a later consumer needs it; and
6. the failure action: continue, dependency-skip with reason, or R23 containment.

The executor writes progress after each completed unit: passed, failed, skipped, or unresolved; the
first unresolved unit; the repository revision when source identity is needed; and any actual external
attempt/target state needed for a practical run. Do not hash ordinary inputs or create a receipt just
for a checkpoint.

An ordinary failure records a failure and does not stop the remaining runnable units. A unit may be
skipped only when a named prerequisite failed or R23 requires containment. The terminal result is a
complete pool, not the first failure.

On a new tip or resumed attempt, ROOT calculates the changed inputs before dispatch. A prior PASS is
reusable only when its source and non-source inputs are declared unchanged and none of its prerequisites
are invalidated. A FAIL is never reusable as a PASS. If the map, input comparison, or runner state is
uncertain, rerun the unit. Form the required execution set from every failed, unresolved,
change-affected, or uncertain unit, then execute it in declared order beginning with its earliest
member. The checkpoint still records the first unresolved unit; that unit is the resume point when no
earlier unit was invalidated. Do not replay unaffected passes. A complete restart is valid only with
no usable progress record or a change that reaches every selected unit.

For a stateful practical/hardware operation, compare the target identity and the state that the unit
actually consumed. Reuse a PASS only when it was non-mutating or the relevant state still holds. A
new fixture, lease, image, server behavior, or target state invalidates the units that consume it.

## FAST_LANE_V2

`FAST_LANE_V2` is a product-repair route; it does not replace the strict test-only fast lane.

ROOT may select it only after the originating checking tranche completes every feasible unit and its
complete pool contains one scoped compatible material correction objective. ROOT then writes a card
containing all of the following:

- one observed material defect and one exact deterministic motivating test;
- the bounded production surface, intended correction, and no-change behavior;
- compile checks for changed production source plus the motivating test as the required smoke;
- the review class/scope for the repaired frozen tip; and
- the integration destination and the incremental gate units that remain required afterward.

The producer runs only that minimal smoke. Its changed-source compile and motivating-test PASS become
checkpoint credit. M04 retains independent review but omits the normal broad affected deterministic
campaign. M06 reads back the integration and does not duplicate green smoke when the fast-forward
leaves the bytes unchanged. The checkpointed gate reuses that smoke credit when its declared inputs
remain unchanged and runs only failed, unresolved, change-affected, uncertain, or otherwise
uncredited units.

Do not select this route for an uncertain impact, no deterministic motivating test, changed test or
runner selection/configuration, external/hardware state, a change that alters a shared/public
protocol, security boundary, broad lifecycle owner, or multiple unrelated mechanisms, or a pool whose
compatible findings require a broader repair batch. Use the normal M02 -> M04 route instead.

## Batch rule

The final safeguard, M04 campaign, and practical observation each return all feasible findings once.
ROOT deduplicates them and groups only compatible material findings into a writer tranche. A tranche
is compatible when one writer can state one correction objective, own the same source context, and
prove the repairs together. The writer receives the complete compatible group, makes one reviewable
tip, and ends at ROOT. It does not receive one card per failure.

Keep independent groups separate when they require different writers, authority, source context,
external state, or acceptance criteria. Do not rerun final assurance until every admitted compatible
group for the current pool has reached an accepted integrated coordinate. Then resume the safeguarded
units according to their checkpoint and input map.
