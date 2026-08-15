from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

HEADINGS = [
    "## 0. Plan contract and status",
    "## 1. Inputs, authority, and directive hierarchy",
    "## 2. Goal, exclusions, and acceptance outcomes",
    "## 3. Requirement coverage map",
    "## 4. Runtime and repository truth",
    "## 5. Deliverable, dependency, risk, and cost model",
    "## 6. Step and M-module library index",
    "## 7. Roles and role-agent mapping boundary",
    "## 8. Composed execution graph and critical path",
    "## 9. Global workflow policies and exceptions",
    "## 10. Lane, resource, result, and handoff manifest",
    "__AGGREGATED_MODULE_INSTANCES_FOR_VALIDATION__",
    "## 12. External and practical validation",
    "## 13. Integration, safeguard, promotion, rollback, and retirement",
    "## 14. Tolerances, unresolved decisions, and out-of-scope ledger",
    "## 15. Rule application matrix",
    "## 16. Structural validation result",
]

POLICY_HEADINGS = [
    "### P01 Ownership and decisions",
    "### P02 Context and thread lifetime",
    "### P03 Failure-case selection",
    "### P04 Check selection and green credit",
    "### P05 Review classes and invalidation",
    "### P06 Parallel checks and results",
    "### P07 Finding pooling and material repair",
    "### P08 Test-only correction",
    "### P09 Administrative recovery",
    "### P10 Semantic acceptance",
    "### P11 Full-safeguard scope",
    "### P12 External authorization and rehearsal",
    "### P13 Gate/loop sizing, health, and topology reassessment",
    "### P14 Exception classes",
    "### P15 Stop and live-harm containment",
]

INSTANCE_FIELDS = [
    "Purpose",
    "Coverage",
    "Selection basis",
    "Owner and roles",
    "Preconditions",
    "Inputs",
    "Local instructions",
    "Outputs and results",
    "Concurrency and isolation",
    "Resources and side effects",
    "Checks and acceptance",
    "Failure and exception routes",
    "Prior results and change effects",
    "Repeat, join, and terminal behavior",
    "Cost and critical-path effect",
]

TASK_FIELDS = [
    "schema/card_id/module_instance_id/deliverable_id/stage_cohort_id/gate_id/loop_id",
    "workflow_role",
    "objective",
    "why_now",
    "starting_state",
    "dependencies_and_predecessor_outputs",
    "working_scope",
    "required_behavior",
    "initial_entrypoints",
    "failure_case_brief",
    "ordered_actions",
    "allowed_tools_capabilities_resources",
    "forbidden_actions_and_boundaries",
    "verification",
    "deliverables_and_result_paths",
    "acceptance_criteria_and_tolerances",
    "completion_review_owner_and_handoff",
    "failure_classification_and_routes",
    "thread_resume_and_terminal_rule",
    "cited_global_policy_ids_and_exception_ids",
]

UNDISPATCHABLE_BARE_TASK_VALUES = {"", "N/A", "TBD", "TODO", "UNKNOWN"}

MODULE_IDS = [f"M{number:02d}" for number in range(1, 11)]
MODULE_ACTION_COUNTS = {
    "M01": 7,
    "M02": 8,
    "M03": 7,
    "M04": 8,
    "M05": 10,
    "M06": 8,
    "M07": 7,
    "M08": 6,
    "M09": 9,
    "M10": 5,
}
MODULE_ACTIONS = {
    module_id: [f"{module_id}-A{number}" for number in range(1, count + 1)]
    for module_id, count in MODULE_ACTION_COUNTS.items()
}
RULE_IDS = [f"R{number}" for number in range(1, 31)] + [f"S{number}" for number in range(1, 17)]
CHECK_IDS = [f"V{number:02d}" for number in range(1, 30)]
ALLOWED_CAPABILITY_STATES = {
    "RUNTIME_ENFORCED",
    "ORCHESTRATOR_ENFORCED",
    "TARGET_TOOL_INVOKED",
    "UNAVAILABLE",
}
ALLOWED_MODULE_DECISIONS = {"SELECTED", "OMITTED", "DEFERRED"}
ALLOWED_GATE_CLASSES = {"PRODUCT", "OPERATION_BOUNDARY"}
PLAN_CONTRACT_FIELDS = [
    "Plan ID",
    "Plan version",
    "Status",
    "Decision owner",
    "Orchestration topology",
    "Verification protocol",
    "Operative document boundary",
    "Change procedure",
    "Definition of valid",
]
PACKAGE_DEPENDENCY_TABLE = (
    "Dependency",
    "Authoritative path",
    "Owns",
    "Referenced by",
    "Compatible edit boundary",
)
PACKAGE_DEPENDENCIES = ["Global rules", "Gated steps", "M-module library", "Agent mapping", "Validation"]
ROLE_TABLE = (
    "Workflow role",
    "Authority class",
    "Reports to",
    "Directs",
    "Responsibilities",
    "Pool capacity",
    "Context class",
    "Write authority",
    "Resources",
    "Activation",
    "Lifetime",
)

REQUIRED_TABLES: dict[str, list[tuple[str, ...]]] = {
    HEADINGS[0]: [("Field", "Value"), PACKAGE_DEPENDENCY_TABLE],
    HEADINGS[1]: [
        (
            "Source",
            "Authority",
            "Path/reference",
            "Supplies",
            "Conflict rule",
        ),
        ("Layer", "Authority", "May define", "Must not override"),
    ],
    HEADINGS[2]: [
        (
            "Outcome ID",
            "Required behavior",
            "Acceptance method",
            "Decision owner",
            "Status",
        ),
        (
            "Boundary ID",
            "Type",
            "Included/excluded/authorization condition",
            "Reason",
            "Owner",
        ),
    ],
    HEADINGS[3]: [
        (
            "Requirement ID",
            "Source",
            "Deliverable ID",
            "Implementation owner",
            "Verification",
            "Acceptance owner",
            "Status",
        )
    ],
    HEADINGS[4]: [
        (
            "Capability/action",
            "State",
            "Source of truth",
            "Invocation owner",
            "Preconditions",
            "How confirmed",
            "Fallback",
        )
    ],
    HEADINGS[5]: [
        (
            "Deliverable ID",
            "Behavioral output",
            "Requirement IDs",
            "Dependencies",
            "Shared seams",
            "Release unit",
        ),
        (
            "Deliverable ID",
            "Realistic failure",
            "Impact",
            "Coupling",
            "Expected range",
            "Expensive operations",
            "Cheapest adequate topology",
            "Why",
        ),
    ],
    HEADINGS[6]: [
        (
            "Step ID",
            "Step file",
            "Public input",
            "Public output",
            "Gate/decision ID",
            "Acceptance owner",
        ),
        ("Module type", "Authoritative module file"),
    ],
    HEADINGS[7]: [
        ROLE_TABLE,
        ("Resolution rule", "Unknown-role behavior", "Mapping-update behavior"),
    ],
    HEADINGS[8]: [
        (
            "Edge ID",
            "From step/output",
            "To step/input",
            "Condition",
            "Serial/parallel",
            "Join ID",
            "Failure branch",
        ),
        (
            "Parallel group",
            "Shared input",
            "Member step IDs",
            "Writable-root isolation",
            "Launch rule",
            "Join ID",
            "Serial exception",
        ),
        (
            "Path ID",
            "Ordered step/edge IDs",
            "Expected range",
            "Overlap",
            "Expensive operations",
            "Why critical",
        ),
        (
            "Gate/loop ID",
            "Owning step",
            "Step file",
            "Gate class",
            "Public outcome/operation",
            "Default-forward edge",
            "Failure/return reference",
        ),
    ],
    HEADINGS[10]: [
        (
            "Lane ID",
            "Module instance",
            "Role",
            "Activation",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Claim/lock ID",
            "Resource",
            "Owner",
            "Activation",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Check",
            "Proves",
            "Dependencies",
            "Result owner",
            "Reuse condition",
            "Rerun route",
            "Result path if needed",
            "Failure route",
        ),
        (
            "Result/handoff ID",
            "Producer",
            "Consumer",
            "Path if durable",
            "Correlation needed",
            "Publication rule",
            "Completion condition",
            "Failure route",
        ),
        (
            "Source allocation ID",
            "Mode",
            "Source/worktree",
            "Writer",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Retirement ID",
            "Target",
            "Owner",
            "Activation",
            "What must be retained",
            "Completion condition",
            "Recovery visibility",
            "Failure route",
        ),
    ],
    HEADINGS[12]: [
        (
            "Decision ID",
            "Module type",
            "Decision",
            "Authority/resource",
            "Synthetic proof",
            "Real proof",
            "Owner",
            "Failure route",
        )
    ],
    HEADINGS[13]: [
        (
            "Decision ID",
            "Module type",
            "Decision",
            "Accepted input",
            "Action/order",
            "Checks",
            "Promotion/rollback/retirement",
            "Owner",
        )
    ],
    HEADINGS[14]: [
        (
            "Item ID",
            "Type",
            "Exact condition",
            "Consequence",
            "Owner",
            "Resolution boundary",
        )
    ],
    HEADINGS[15]: [("Rule ID", "Plan location", "Applied behavior or justified N/A")],
    HEADINGS[16]: [("Check ID", "Result", "Basis")],
}

POLICY_TABLE = (
    "Owner",
    "Trigger",
    "Required action",
    "Exit",
    "Result/record if needed",
    "Module IDs",
)
EXCEPTION_TABLE = (
    "Exception ID",
    "Affected policy",
    "Exact trigger",
    "Decision owner",
    "Allowed alternate action",
    "Required confirmation",
    "Preserved results",
    "Invalidated results",
    "Scope",
    "Expiry",
)
STEP_HEADINGS = [
    "## Step contract",
    "## Activation, inputs, and protected boundaries",
    "## Ordered M-module composition",
    "## Public outputs and successors",
    "## Gate, completion, and return boundary",
    "## Failure, continuation, and preserved results",
    "## Concurrency, isolation, resources, and lifecycle",
    "## Cost and critical-path effect",
]
STEP_CONTRACT_FIELDS = [
    "Step ID",
    "Objective and independently decidable outcome",
    "Acceptance owner",
    "Deliverable and requirement coverage",
    "Global policy and exception references",
    "Public compatibility boundary",
]
STEP_COMPOSITION_TABLE = (
    "Order",
    "Instance ID",
    "Module type",
    "Consumes",
    "Produces",
    "Activation/condition",
)
STEP_GATE_TABLE = (
    "Gate/loop ID",
    "Gate class",
    "Shared input",
    "Decided behavioral outcome",
    "Checking module instances",
    "Shared failure family/invariants",
    "Blocking scope",
    "Continuation/loop eligibility",
    "Default-forward edge",
    "Failure return target",
    "Aggregation payoff",
    "Manageability proof",
    "Prior-result boundary",
    "Split/merge trigger",
)
MODULE_HEADINGS = [
    "## Module contract and selection",
    "## Public interface and compatibility boundary",
    "## Rules, process, recipe actions, and allowed variations",
    "## Configured module instances",
]
MODULE_SELECTION_TABLE = (
    "Module type",
    "Decision",
    "Instance IDs",
    "Reason",
    "Prerequisite/owner if deferred",
)
MODULE_ACTION_TABLE = (
    "Order",
    "Recipe action ID",
    "Project-specific action/process",
    "Allowed parameterization",
    "Decision owner",
)
INSTANCE_RE = re.compile(r"(?m)^###\s+(MI-[A-Z0-9][A-Z0-9_-]*)\s+-\s+(M\d{2}):\s+(.+?)\s*$")
MI_RE = re.compile(r"\bMI-[A-Z0-9][A-Z0-9_-]*\b")
STEP_RE = re.compile(r"\bSTEP-[A-Z0-9][A-Z0-9_-]*\b")
TASK_CARD_RE = re.compile(
    r"(?m)^#####\s+(Governing|Member) task card:\s+(CARD-[A-Z0-9][A-Z0-9_-]*)\s*$"
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`"))


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [normalize(cell) for cell in stripped[1:-1].split("|")]


def is_separator(cells: list[str] | None) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def extract_table(body: str, header: tuple[str, ...]) -> list[list[str]] | None:
    lines = body.splitlines()
    expected = list(header)
    for index, line in enumerate(lines):
        if table_cells(line) != expected:
            continue
        if index + 1 >= len(lines) or not is_separator(table_cells(lines[index + 1])):
            return []
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            cells = table_cells(row_line)
            if cells is None:
                if rows or row_line.strip():
                    break
                continue
            if len(cells) != len(expected):
                rows.append(cells)
                continue
            rows.append(cells)
        return rows
    return None


def task_card_blocks(body: str) -> list[tuple[str, str, str]]:
    matches = list(TASK_CARD_RE.finditer(body))
    return [
        (
            match.group(1),
            match.group(2),
            body[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(body)],
        )
        for index, match in enumerate(matches)
    ]


def section(text: str, heading: str, next_heading: str | None) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start) if next_heading else len(text)
    return text[start:end]


def sections(text: str) -> dict[str, str]:
    return {
        heading: section(text, heading, HEADINGS[index + 1] if index + 1 < len(HEADINGS) else None)
        for index, heading in enumerate(HEADINGS)
    }


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def id_column(rows: list[list[str]], pattern: str) -> list[str]:
    return [row[0] for row in rows if row and re.fullmatch(pattern, row[0])]


def validate_required_tables(by_section: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for heading, headers in REQUIRED_TABLES.items():
        body = by_section[heading]
        for header in headers:
            rows = extract_table(body, header)
            if rows is None:
                errors.append(f"{heading} is missing table: {' | '.join(header)}")
            elif not rows:
                errors.append(f"{heading} table has no data rows: {' | '.join(header)}")
            elif any(len(row) != len(header) for row in rows):
                errors.append(f"{heading} table has a row with the wrong column count: {' | '.join(header)}")
    return errors


def validate_instances(body: str, instance_types: dict[str, str]) -> list[str]:
    errors: list[str] = []
    card_ids: list[str] = []
    matches = list(INSTANCE_RE.finditer(body))
    found_ids = [match.group(1) for match in matches]
    if duplicates(found_ids):
        errors.append(f"module files contain duplicate instance blocks: {', '.join(duplicates(found_ids))}")
    missing = sorted(set(instance_types) - set(found_ids))
    extra = sorted(set(found_ids) - set(instance_types))
    if missing:
        errors.append(f"selected module instances missing from their owning M files: {', '.join(missing)}")
    if extra:
        errors.append(f"M files contain undeclared module instances: {', '.join(extra)}")

    for index, match in enumerate(matches):
        instance_id, module_type = match.group(1), match.group(2)
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : block_end]
        if instance_types.get(instance_id) != module_type:
            errors.append(
                f"{instance_id} block type {module_type} does not match its M-file selection type "
                f"{instance_types.get(instance_id, 'UNDECLARED')}"
            )
        fields = re.findall(r"(?m)^####\s+(.+?)\s*$", block)
        if fields != INSTANCE_FIELDS:
            errors.append(
                f"{instance_id} does not use the exact 15 H4 subheadings in order "
                "(16 required schema headings including its MI H3)"
            )
        local_start = block.find("#### Local instructions")
        local_end = block.find("#### Outputs and results", local_start + 1)
        local_body = block[local_start:local_end] if local_start >= 0 and local_end >= 0 else ""
        cards = task_card_blocks(local_body)
        h5_headings = re.findall(r"(?m)^#####\s+.+?$", local_body)
        if len(h5_headings) != len(cards):
            errors.append(f"{instance_id} has an H5 that is not an exact governing/member task-card label")
        governing_cards = [card for card in cards if card[0] == "Governing"]
        if len(governing_cards) != 1:
            errors.append(f"{instance_id} must contain exactly one governing task card")
        for card_kind, card_id, card_body in cards:
            card_ids.append(card_id)
            task_rows = extract_table(card_body, ("Field", "Value"))
            if task_rows is None:
                errors.append(f"{instance_id} {card_id} has no Field | Value task-card table")
                continue
            valid_task_rows = [row for row in task_rows if len(row) == 2]
            if [row[0] for row in valid_task_rows] != TASK_FIELDS:
                errors.append(f"{instance_id} {card_id} does not use all 20 task-card fields in order")
            task_values = {row[0]: row[1] for row in valid_task_rows}
            identity_value = task_values.get(TASK_FIELDS[0], "")
            if card_id not in identity_value or instance_id not in identity_value:
                errors.append(f"{instance_id} {card_id} identity row must contain both IDs")
            for task_field in TASK_FIELDS:
                task_value = normalize(task_values.get(task_field, "")).upper()
                if task_value in UNDISPATCHABLE_BARE_TASK_VALUES:
                    errors.append(
                        f"{instance_id} {card_id} task field {task_field} has a bare placeholder; "
                        "ROOT must supply a concrete dispatch-contract value or a reasoned N/A "
                        "explicitly permitted by the selected recipe"
                    )
            found_actions = re.findall(r"\bM\d{2}-A\d+\b", task_values.get("ordered_actions", ""))
            expected_actions = MODULE_ACTIONS.get(module_type, [])
            if card_kind == "Governing" and found_actions != expected_actions:
                errors.append(
                    f"{instance_id} governing card {card_id} ordered_actions must contain "
                    f"{', '.join(MODULE_ACTIONS.get(module_type, []))} exactly once and in order"
                )
            if card_kind == "Member":
                positions = [expected_actions.index(action) for action in found_actions if action in expected_actions]
                if (
                    not found_actions
                    or len(positions) != len(found_actions)
                    or duplicates(found_actions)
                    or positions != sorted(positions)
                ):
                    errors.append(
                        f"{instance_id} member card {card_id} ordered_actions must be a nonempty, "
                        f"duplicate-free ordered subsequence of {', '.join(expected_actions)}"
                    )
    if duplicates(card_ids):
        errors.append(f"task-card IDs are declared more than once: {', '.join(duplicates(card_ids))}")
    return errors


def validate_policies(body: str) -> list[str]:
    errors: list[str] = []
    found = re.findall(r"(?m)^###\s+P\d{2}.+?$", body)
    if found != POLICY_HEADINGS:
        errors.append("Section 9 does not contain exact P01-P15 policy headings in order")
        return errors
    for index, heading in enumerate(POLICY_HEADINGS):
        start = body.index(heading) + len(heading)
        end = body.index(POLICY_HEADINGS[index + 1], start) if index + 1 < len(POLICY_HEADINGS) else len(body)
        policy_body = body[start:end]
        rows = extract_table(policy_body, POLICY_TABLE)
        if rows is None or not rows:
            errors.append(f"{heading} has no populated policy table")
        if heading.startswith("### P14"):
            exception_rows = extract_table(policy_body, EXCEPTION_TABLE)
            if exception_rows is None or not exception_rows:
                errors.append("P14 has no exception-class table or reasoned N/A row")
    return errors


def validate_verification_economy(
    plan_contract: str,
    global_policies: str,
    text: str,
) -> list[str]:
    """Validate the optional checkpointed-gate protocol for newly amended plans."""

    checkpointed = "checkpointed_verification_v1" in text.lower()
    fast_lane_v2 = "fast_lane_v2" in text.lower()
    if fast_lane_v2 and not checkpointed:
        return ["FAST_LANE_V2 requires CHECKPOINTED_VERIFICATION_V1"]
    if not checkpointed:
        return []

    errors: list[str] = []
    if "checkpointed_verification_v1" not in plan_contract.lower():
        errors.append("CHECKPOINTED_VERIFICATION_V1 must appear in Section 0")
    policy_text = global_policies.lower()
    for term in ("checkpoint", "input map", "first unresolved", "earliest required", "ordinary failure"):
        if term not in policy_text:
            errors.append(f"CHECKPOINTED_VERIFICATION_V1 requires policy text for {term!r}")
    if fast_lane_v2:
        for term in (
            "complete pool",
            "motivating test",
            "compile",
            "review",
            "integration",
            "smoke credit",
        ):
            if term not in policy_text:
                errors.append(f"FAST_LANE_V2 requires policy text for {term!r}")
    return errors


def validate_gates(body: str) -> list[str]:
    errors: list[str] = []
    header = STEP_GATE_TABLE
    rows = extract_table(body, header) or []
    gate_ids = [row[0] for row in rows if len(row) == len(header) and row[0] != "N/A"]
    if duplicates(gate_ids):
        errors.append(f"gate manifest contains duplicates: {', '.join(duplicates(gate_ids))}")

    for row in rows:
        if len(row) != len(header) or row[0] == "N/A":
            continue
        gate_id, gate_class = row[0], row[1]
        if not gate_id.startswith("GATE-"):
            errors.append(f"gate row has invalid ID {gate_id!r}")
        if gate_class not in ALLOWED_GATE_CLASSES:
            errors.append(f"{gate_id} has invalid gate class {gate_class!r}")
        required_fields = (
            (6, "blocking scope"),
            (7, "continuation/loop eligibility"),
            (8, "default-forward edge"),
            (9, "failure return target"),
        )
        for index, label in required_fields:
            if row[index].lower() in {"", "n/a", "none", "not applicable"}:
                errors.append(f"{gate_id} has no {label}")
        blocking_scope = row[6].lower()
        continuation = row[7].lower()
        default_forward = row[8].lower()
        failure_target = row[9].lower()

        if not any(
            token in default_forward
            for token in (
                "edge",
                "advance",
                "continue",
                "accept",
                "success",
                "terminal",
            )
        ):
            errors.append(f"{gate_id} default-forward edge must name an advancing successor or terminal action")

        if gate_class == "PRODUCT":
            decided_outcome = row[3].lower()
            strong_product_terms = (
                "behavior",
                "contract",
                "satisf",
                "capability",
                "agree",
                "prove",
            )
            operation_terms = (
                "allocat",
                "integrat",
                "join",
                "deploy",
                "promot",
                "read back",
                "readback",
                "cleanup",
                "retire",
            )
            names_product_outcome = any(token in decided_outcome for token in strong_product_terms) or (
                "correct" in decided_outcome and not any(token in decided_outcome for token in operation_terms)
            )
            if not names_product_outcome:
                errors.append(
                    f"{gate_id} PRODUCT decided outcome must name observable behavior, "
                    "contract, capability, correctness, satisfaction, agreement, or proof; "
                    "a pure required operation belongs to OPERATION_BOUNDARY"
                )
            required_terms = ("only", "required", "product")
            if not all(term in continuation for term in required_terms) or not any(
                term in continuation for term in ("fail", "undecidable")
            ):
                errors.append(
                    f"{gate_id} PRODUCT continuation eligibility must say that only a failed/"
                    "undecidable required product criterion permits continuation"
                )
            if "only" not in blocking_scope:
                errors.append(f"{gate_id} PRODUCT blocking scope must be explicitly limited with 'only'")

        if gate_class == "OPERATION_BOUNDARY":
            if "only" not in blocking_scope or "never product" not in blocking_scope:
                errors.append(
                    f"{gate_id} OPERATION_BOUNDARY blocking scope must say it holds only the "
                    "exact operation and never product work/credit"
                )
            if "no product loop" not in continuation:
                errors.append(f"{gate_id} OPERATION_BOUNDARY continuation must explicitly say 'No product loop'")
            if any(
                token in failure_target
                for token in (
                    "m02",
                    "material repair",
                    "material return",
                    "product repair",
                )
            ):
                errors.append(f"{gate_id} OPERATION_BOUNDARY failure target must not enter product repair")
    return errors


def validate_cross_references(by_section: dict[str, str], instance_types: dict[str, str]) -> list[str]:
    errors: list[str] = []
    req_header = REQUIRED_TABLES[HEADINGS[3]][0]
    deliverable_header = REQUIRED_TABLES[HEADINGS[5]][0]
    req_rows = extract_table(by_section[HEADINGS[3]], req_header) or []
    deliverable_rows = extract_table(by_section[HEADINGS[5]], deliverable_header) or []
    req_ids = id_column(req_rows, r"REQ-[A-Z0-9][A-Z0-9._-]*")
    deliverable_ids = id_column(deliverable_rows, r"DEL-[A-Z0-9][A-Z0-9._-]*")
    if not req_ids:
        errors.append("requirement coverage map has no REQ-* rows")
    if not deliverable_ids:
        errors.append("deliverable model has no DEL-* rows")
    if duplicates(req_ids):
        errors.append(f"duplicate requirement IDs: {', '.join(duplicates(req_ids))}")
    if duplicates(deliverable_ids):
        errors.append(f"duplicate deliverable IDs: {', '.join(duplicates(deliverable_ids))}")
    known_deliverables = set(deliverable_ids)
    for row in req_rows:
        if len(row) == len(req_header) and row[0].startswith("REQ-") and row[2] not in known_deliverables:
            errors.append(f"{row[0]} references unknown deliverable {row[2]}")

    capability_rows = extract_table(by_section[HEADINGS[4]], REQUIRED_TABLES[HEADINGS[4]][0]) or []
    for row in capability_rows:
        if len(row) == 7 and row[0] != "N/A" and row[1] not in ALLOWED_CAPABILITY_STATES:
            errors.append(f"capability {row[0]!r} has invalid state {row[1]!r}")

    selected_ids = set(instance_types)
    for header in REQUIRED_TABLES[HEADINGS[8]]:
        rows = extract_table(by_section[HEADINGS[8]], header) or []
        for row in rows:
            for instance_id in MI_RE.findall(" ".join(row)):
                if instance_id not in selected_ids:
                    errors.append(f"Section 8 references undeclared module instance {instance_id}")
    return errors


def split_role_keys(value: str) -> list[str]:
    if normalize(value).upper() == "N/A":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_plan_contract(
    body: str,
    mapping_name: str,
    mapping_path: Path | None = None,
    plan_path: Path | None = None,
) -> tuple[list[str], str]:
    errors: list[str] = []
    contract_rows = extract_table(body, ("Field", "Value")) or []
    valid_contract_rows = [row for row in contract_rows if len(row) == 2]
    if [row[0] for row in valid_contract_rows] != PLAN_CONTRACT_FIELDS:
        errors.append("Section 0 must contain the exact plan-contract fields once and in order")
    contract = {row[0]: normalize(row[1]) for row in valid_contract_rows}
    for field in PLAN_CONTRACT_FIELDS:
        if field == "Verification protocol" and contract.get(field, "").upper() == "N/A":
            continue
        if contract.get(field, "").upper() in UNDISPATCHABLE_BARE_TASK_VALUES:
            errors.append(f"Section 0 plan-contract field {field} is empty or a bare placeholder")
    topology = contract.get("Orchestration topology", "")
    if topology != "ROOT_DIRECT_WORKERS":
        errors.append("Generic topology must declare Orchestration topology as ROOT_DIRECT_WORKERS")

    dependency_rows = extract_table(body, PACKAGE_DEPENDENCY_TABLE) or []
    valid_dependencies = [row for row in dependency_rows if len(row) == len(PACKAGE_DEPENDENCY_TABLE)]
    if [row[0] for row in valid_dependencies] != PACKAGE_DEPENDENCIES:
        errors.append("Section 0 package dependencies must list the five authoritative artifacts once and in order")
    else:
        expected_paths = {
            "Global rules": "global-rules.md",
            "Gated steps": "steps/",
            "M-module library": "modules/M01.md through modules/M10.md",
            "Validation": "validation.md",
        }
        for row in valid_dependencies:
            if row[0] == "Agent mapping":
                declared_path = Path(normalize(row[1]))
                if mapping_path is not None and plan_path is not None:
                    declared_target = declared_path if declared_path.is_absolute() else plan_path / declared_path
                    if declared_target.resolve() != mapping_path.resolve():
                        errors.append("Section 0 Agent mapping path does not resolve to the canonical --mapping path")
                elif declared_path.name != mapping_name:
                    errors.append(f"Section 0 Agent mapping path must name {mapping_name!r}")
            elif row[0] != "Agent mapping" and normalize(row[1]) != expected_paths[row[0]]:
                errors.append(f"Section 0 dependency {row[0]} must use authoritative path {expected_paths[row[0]]!r}")
            if any(normalize(value).upper() in UNDISPATCHABLE_BARE_TASK_VALUES for value in row[2:]):
                errors.append(f"Section 0 dependency {row[0]} has an empty or bare ownership/edit-boundary value")
    return errors, topology


def validate_roles(
    body: str,
    mapping_roles: set[str],
    mapping_name: str,
    text: str,
    topology: str,
) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(body, ROLE_TABLE) or []
    valid_role_rows = [row for row in role_rows if len(row) == len(ROLE_TABLE) and row[0] != "N/A"]
    plan_roles = [row[0] for row in valid_role_rows]
    if not plan_roles:
        errors.append("role table contains no workflow roles")
    if duplicates(plan_roles):
        errors.append(f"role table contains duplicate roles: {', '.join(duplicates(plan_roles))}")
    if set(plan_roles) != mapping_roles:
        missing = sorted(set(plan_roles) - mapping_roles)
        extra = sorted(mapping_roles - set(plan_roles))
        if missing:
            errors.append(f"mapping is missing plan roles: {', '.join(missing)}")
        if extra:
            errors.append(f"mapping has roles absent from the plan: {', '.join(extra)}")
    row_by_role = {row[0]: row for row in valid_role_rows}
    root_roles = [row[0] for row in valid_role_rows if normalize(row[1]).upper() == "ROOT"]
    if len(root_roles) != 1:
        errors.append("authority graph must declare exactly one ROOT role")
        root_role = ""
    else:
        root_role = root_roles[0]

    allowed_classes = {"ROOT", "WORKER"}
    for row in valid_role_rows:
        role, authority_class, reports_to, directs = row[0], normalize(row[1]).upper(), normalize(row[2]), row[3]
        if authority_class not in allowed_classes:
            errors.append(f"Generic role {role} has forbidden authority class {authority_class!r}")
        parent = "" if reports_to.upper() == "N/A" else reports_to
        children = split_role_keys(directs)
        if authority_class == "ROOT":
            if parent:
                errors.append(f"ROOT role {role} must report to N/A")
        else:
            if parent != root_role:
                errors.append(f"Generic worker role {role} must report directly to ROOT role {root_role!r}")
            if children:
                errors.append(f"Generic worker role {role} may not direct another role")
        for child in children:
            if child not in row_by_role:
                errors.append(f"role {role} directs unknown role {child!r}")
            elif normalize(row_by_role[child][2]) != role:
                errors.append(f"role {role} directs {child}, but {child} does not report to {role}")
        pool_match = re.search(r"\b(\d+)\b", row[5])
        if pool_match is None or int(pool_match.group(1)) < 1:
            errors.append(f"role {row[0]} has no positive pool capacity")
    for role, row in row_by_role.items():
        parent = "" if normalize(row[2]).upper() == "N/A" else normalize(row[2])
        if parent and (parent not in row_by_role or role not in split_role_keys(row_by_role[parent][3])):
            errors.append(f"role {role} reports to {parent!r}, but that parent does not direct it")
    if text.lower().count(mapping_name.lower()) != 1:
        errors.append(f"plan must mention mapping filename {mapping_name!r} exactly once")
    return errors


def validate_root_acceptance_ownership(root_sections: dict[str, str]) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(root_sections[HEADINGS[7]], ROLE_TABLE) or []
    root_roles = [row[0] for row in role_rows if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "ROOT"]
    if len(root_roles) != 1:
        return errors
    root_role = root_roles[0]
    contract_rows = extract_table(root_sections[HEADINGS[0]], ("Field", "Value")) or []
    contract = {row[0]: normalize(row[1]) for row in contract_rows if len(row) == 2}
    if contract.get("Decision owner") != root_role:
        errors.append(f"Section 0 Decision owner must be the ROOT role {root_role!r}")
    outcome_rows = extract_table(root_sections[HEADINGS[2]], REQUIRED_TABLES[HEADINGS[2]][0]) or []
    for row in outcome_rows:
        if len(row) == 5 and row[0] != "N/A" and row[3] != root_role:
            errors.append(f"outcome {row[0]} Decision owner must be the ROOT role {root_role!r}")
    requirement_rows = extract_table(root_sections[HEADINGS[3]], REQUIRED_TABLES[HEADINGS[3]][0]) or []
    for row in requirement_rows:
        if len(row) == 7 and row[0] != "N/A" and row[5] != root_role:
            errors.append(f"requirement {row[0]} Acceptance owner must be the ROOT role {root_role!r}")
    return errors


def validate_rule_and_check_matrices(by_section: dict[str, str]) -> list[str]:
    errors: list[str] = []
    rule_rows = extract_table(by_section[HEADINGS[15]], REQUIRED_TABLES[HEADINGS[15]][0]) or []
    rule_ids = [row[0] for row in rule_rows if len(row) == 3]
    if rule_ids != RULE_IDS:
        errors.append("Section 15 must map R1-R30 then S1-S16 exactly once and in order")

    check_rows = extract_table(by_section[HEADINGS[16]], REQUIRED_TABLES[HEADINGS[16]][0]) or []
    check_ids = [row[0] for row in check_rows if len(row) == 3]
    if check_ids != CHECK_IDS:
        errors.append("Section 16 must contain V01-V29 exactly once and in order")
    for row in check_rows:
        if len(row) == 3 and row[1] != "PASS":
            errors.append(f"{row[0]} is not PASS")
        if len(row) == 3 and not row[2].strip():
            errors.append(f"{row[0]} has no basis")
    marker_count = by_section[HEADINGS[16]].count("PLAN_STRUCTURE=VALID")
    if marker_count != 1:
        errors.append(f"expected one PLAN_STRUCTURE=VALID marker, found {marker_count}")
    if "PLAN_STRUCTURE=INVALID" in by_section[HEADINGS[16]]:
        errors.append("Section 16 still contains PLAN_STRUCTURE=INVALID")
    return errors


def validate_module_policy_and_role_references(
    global_body: str,
    step_texts: dict[str, str],
    module_texts: dict[str, str],
    mapping_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    known_refs = {heading.split()[1] for heading in POLICY_HEADINGS}
    exception_rows = extract_table(global_body, EXCEPTION_TABLE) or []
    known_refs.update(
        row[0] for row in exception_rows
        if len(row) == len(EXCEPTION_TABLE) and re.fullmatch(r"EXC-[A-Z0-9][A-Z0-9._-]*", row[0])
    )
    reference_pattern = r"\bP\d{2}\b|\bEXC-[A-Z0-9][A-Z0-9._-]*"
    for filename, text in {**step_texts, **module_texts}.items():
        unknown = sorted(set(re.findall(reference_pattern, text)) - known_refs)
        if unknown:
            errors.append(f"{filename} cites unknown global policy/exception IDs: {', '.join(unknown)}")
    for filename, text in module_texts.items():
        action_rows = extract_table(text, MODULE_ACTION_TABLE) or []
        for row in action_rows:
            if len(row) == len(MODULE_ACTION_TABLE) and row[4] not in mapping_roles:
                errors.append(f"{filename} action {row[1]} uses decision owner absent from mapping: {row[4]}")
    return errors


def validate_unbounded_agent_sessions(text: str, mapping_roles: set[str]) -> list[str]:
    errors: list[str] = []
    named_roles = "|".join(
        sorted((re.escape(role) for role in mapping_roles if role.strip()), key=len, reverse=True)
    )
    role_prefix = (
        r"agent(?:\s+and\s+subagent)?|subagent|root|lane\s+sub-orchestrator|"
        r"workers?|reviewers?|testers?|observers?|auditors?|implementers?|planners?|researchers?"
    )
    if named_roles:
        role_prefix += f"|{named_roles}"
    session_pattern = re.compile(
        rf"\b(?:{role_prefix})\s+"
        r"(?:launch(?:es)?|session(?:s)?|invocation(?:s)?|launch wrappers?)\b|"
        r"\bcodex exec\b|\bclaude -p\b",
        re.IGNORECASE,
    )
    finite_bound_pattern = re.compile(
        r"\b(?:timeout|deadline|maximum\s+(?:lifetime|runtime)|"
        r"max(?:imum)?\s+of\s+\d+\s*(?:seconds?|minutes?|hours?)|"
        r"(?:must|shall|required\s+to)\s+(?:finish|terminate|end|complete|stop)\s+within|"
        r"within\s+\d+\s*(?:seconds?|minutes?|hours?))\b",
        re.IGNORECASE,
    )
    exemption_pattern = re.compile(
        r"\b(?:unbounded|exempt|no\s+(?:timeout|deadline|maximum)|not\s+(?:time-?)?bounded|"
        r"not\s+subject|outside.{0,30}(?:bound|supervis)|never.{0,20}(?:bound|wrap)|"
        r"must\s+not.{0,20}(?:bound|wrap|timeout))\b",
        re.IGNORECASE,
    )
    clause_split_pattern = re.compile(
        r"(?<=[.;!?])\s+|,\s*(?=(?:but|however|except|whereas)\b)|"
        r"\b(?:but|however|except|whereas)\b",
        re.IGNORECASE,
    )
    for line_number, line in enumerate(text.splitlines(), 1):
        for clause in clause_split_pattern.split(line):
            if (
                session_pattern.search(clause)
                and finite_bound_pattern.search(clause)
                and not exemption_pattern.search(clause)
            ):
                errors.append(
                    f"line {line_number} assigns a finite timeout/deadline to an agent session or launch; "
                    "agent and subagent sessions must remain unbounded"
                )
                break
    return errors


def split_owned_sections(text: str, headings: list[str], label: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    found = re.findall(r"(?m)^##\s+.+?$", text)
    if found != headings:
        errors.append(f"{label} does not contain its exact H2 headings once and in order")
        return {}, errors
    result: dict[str, str] = {}
    for index, heading in enumerate(headings):
        start = text.index(heading) + len(heading)
        end = text.index(headings[index + 1], start) if index + 1 < len(headings) else len(text)
        result[heading] = text[start:end]
    return result, errors


def validate_module_files(module_texts: dict[str, str]) -> tuple[list[str], dict[str, str], str]:
    errors: list[str] = []
    instance_types: dict[str, str] = {}
    instance_bodies: list[str] = []
    expected_files = {f"{module_id}.md" for module_id in MODULE_IDS}
    if set(module_texts) != expected_files:
        missing = sorted(expected_files - set(module_texts))
        extra = sorted(set(module_texts) - expected_files)
        if missing:
            errors.append(f"modules directory is missing: {', '.join(missing)}")
        if extra:
            errors.append(f"modules directory has unexpected files: {', '.join(extra)}")

    for module_id in MODULE_IDS:
        filename = f"{module_id}.md"
        text = module_texts.get(filename, "")
        if not text:
            continue
        titles = re.findall(r"(?m)^#\s+(.+?)\s*$", text)
        if len(titles) != 1 or not titles[0].startswith(f"{module_id} - "):
            errors.append(f"{filename} must have exactly one '# {module_id} - <name>' title")
        owned, heading_errors = split_owned_sections(text, MODULE_HEADINGS, filename)
        errors.extend(heading_errors)
        if heading_errors:
            continue

        selection_rows = extract_table(owned[MODULE_HEADINGS[0]], MODULE_SELECTION_TABLE) or []
        if len(selection_rows) != 1 or len(selection_rows[0]) != len(MODULE_SELECTION_TABLE):
            errors.append(f"{filename} must contain exactly one valid module selection row")
            continue
        row = selection_rows[0]
        if row[0] != module_id:
            errors.append(f"{filename} selection row declares {row[0]!r}, expected {module_id}")
        decision = row[1].upper()
        declared_ids = MI_RE.findall(row[2])
        if decision not in ALLOWED_MODULE_DECISIONS:
            errors.append(f"{module_id} has invalid decision {row[1]!r}")
        if decision == "SELECTED" and not declared_ids:
            errors.append(f"{module_id} is SELECTED but has no MI-* instance ID")
        if decision != "SELECTED" and declared_ids:
            errors.append(f"{module_id} is {decision} but declares instance IDs")
        if normalize(row[3]).upper() in UNDISPATCHABLE_BARE_TASK_VALUES:
            errors.append(f"{module_id} selection has no concrete reason")
        if decision == "DEFERRED" and normalize(row[4]).upper() in UNDISPATCHABLE_BARE_TASK_VALUES:
            errors.append(f"{module_id} is DEFERRED without a prerequisite and owner")

        action_rows = extract_table(owned[MODULE_HEADINGS[2]], MODULE_ACTION_TABLE) or []
        valid_action_rows = [item for item in action_rows if len(item) == len(MODULE_ACTION_TABLE)]
        action_ids = [item[1] for item in valid_action_rows]
        if action_ids != MODULE_ACTIONS[module_id]:
            errors.append(
                f"{filename} action table must contain {', '.join(MODULE_ACTIONS[module_id])} "
                "exactly once and in order"
            )
        expected_order = [str(index) for index in range(1, len(valid_action_rows) + 1)]
        if [item[0] for item in valid_action_rows] != expected_order:
            errors.append(f"{filename} action-table Order values must be consecutive from 1")
        for item in valid_action_rows:
            if any(normalize(value).upper() in UNDISPATCHABLE_BARE_TASK_VALUES for value in item[2:]):
                errors.append(f"{filename} action {item[1]} has an empty or bare process/parameter/owner value")

        configured = owned[MODULE_HEADINGS[3]]
        matches = list(INSTANCE_RE.finditer(configured))
        found_ids = [match.group(1) for match in matches]
        all_h3 = re.findall(r"(?m)^###\s+.+?$", configured)
        if len(all_h3) != len(matches):
            errors.append(f"{filename} contains a malformed or non-instance H3 heading")
        if found_ids != declared_ids:
            errors.append(
                f"{filename} declared instance IDs do not exactly match configured instance blocks in order"
            )
        for match in matches:
            instance_id, declared_type = match.group(1), match.group(2)
            if declared_type != module_id:
                errors.append(f"{instance_id} is in {filename} but declares type {declared_type}")
            if instance_id in instance_types:
                errors.append(f"module instance ID is declared more than once: {instance_id}")
            instance_types[instance_id] = module_id
        instance_bodies.append(configured)

    joined_instances = "\n\n".join(instance_bodies)
    errors.extend(validate_instances(joined_instances, instance_types))
    return errors, instance_types, joined_instances


def validate_step_files(
    root_sections: dict[str, str],
    step_texts: dict[str, str],
    instance_types: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    index_body = root_sections[HEADINGS[6]]
    step_rows = extract_table(index_body, REQUIRED_TABLES[HEADINGS[6]][0]) or []
    module_rows = extract_table(index_body, REQUIRED_TABLES[HEADINGS[6]][1]) or []

    indexed_steps: dict[str, str] = {}
    for row in step_rows:
        if len(row) != 6 or row[0] == "N/A":
            continue
        step_id, step_file = row[0], row[1]
        if not re.fullmatch(r"STEP-[A-Z0-9][A-Z0-9_-]*", step_id):
            errors.append(f"step index has invalid ID {step_id!r}")
        if step_id in indexed_steps:
            errors.append(f"step index contains duplicate ID {step_id}")
        indexed_steps[step_id] = step_file
        if step_file != f"steps/{step_id}.md":
            errors.append(f"{step_id} must use step file steps/{step_id}.md")
    if not indexed_steps:
        errors.append("step index contains no STEP-* rows")

    expected_module_rows = [[module_id, f"modules/{module_id}.md"] for module_id in MODULE_IDS]
    if module_rows != expected_module_rows:
        errors.append("Section 6 module index must list M01.md through M10.md exactly once and in order")

    expected_step_files = {f"{step_id}.md" for step_id in indexed_steps}
    if set(step_texts) != expected_step_files:
        missing = sorted(expected_step_files - set(step_texts))
        extra = sorted(set(step_texts) - expected_step_files)
        if missing:
            errors.append(f"steps directory is missing indexed files: {', '.join(missing)}")
        if extra:
            errors.append(f"steps directory has unindexed files: {', '.join(extra)}")

    consumed_instances: list[str] = []
    gate_owners: dict[str, tuple[str, str]] = {}
    for step_id, indexed_path in indexed_steps.items():
        filename = f"{step_id}.md"
        text = step_texts.get(filename, "")
        if not text:
            continue
        titles = re.findall(r"(?m)^#\s+(.+?)\s*$", text)
        if len(titles) != 1 or not titles[0].startswith(f"{step_id} - "):
            errors.append(f"{filename} must have exactly one '# {step_id} - <name>' title")
        owned, heading_errors = split_owned_sections(text, STEP_HEADINGS, filename)
        errors.extend(heading_errors)
        if heading_errors:
            continue

        contract_rows = extract_table(owned[STEP_HEADINGS[0]], ("Field", "Value")) or []
        valid_contract_rows = [row for row in contract_rows if len(row) == 2]
        if [row[0] for row in valid_contract_rows] != STEP_CONTRACT_FIELDS:
            errors.append(f"{filename} does not use the exact step-contract fields in order")
        contract_values = {row[0]: row[1] for row in valid_contract_rows}
        if contract_values.get("Step ID") != step_id:
            errors.append(f"{filename} Step ID field does not match its filename")
        for field in STEP_CONTRACT_FIELDS:
            if normalize(contract_values.get(field, "")).upper() in UNDISPATCHABLE_BARE_TASK_VALUES:
                errors.append(f"{filename} step-contract field {field} is empty or a bare placeholder")

        composition_rows = extract_table(owned[STEP_HEADINGS[2]], STEP_COMPOSITION_TABLE) or []
        valid_composition = [row for row in composition_rows if len(row) == len(STEP_COMPOSITION_TABLE)]
        if not valid_composition:
            errors.append(f"{filename} has no configured M-module composition rows")
        if [row[0] for row in valid_composition] != [str(i) for i in range(1, len(valid_composition) + 1)]:
            errors.append(f"{filename} composition Order values must be consecutive from 1")
        for row in valid_composition:
            instance_id, module_type = row[1], row[2]
            if instance_id not in instance_types:
                errors.append(f"{filename} composes undeclared instance {instance_id}")
            elif instance_types[instance_id] != module_type:
                errors.append(
                    f"{filename} composes {instance_id} as {module_type}, expected {instance_types[instance_id]}"
                )
            consumed_instances.append(instance_id)
            if any(normalize(value).upper() in UNDISPATCHABLE_BARE_TASK_VALUES for value in row[3:]):
                errors.append(f"{filename} composition for {instance_id} has a bare interface/activation value")

        gate_rows = extract_table(owned[STEP_HEADINGS[4]], STEP_GATE_TABLE) or []
        if not gate_rows:
            errors.append(f"{filename} has no populated gate/completion row")
        errors.extend(validate_gates(owned[STEP_HEADINGS[4]]))
        for row in gate_rows:
            if len(row) != len(STEP_GATE_TABLE) or row[0] == "N/A":
                continue
            gate_match = re.search(r"\bGATE-[A-Z0-9][A-Z0-9_-]*\b", row[0])
            if not gate_match:
                continue
            gate_id = gate_match.group(0)
            if gate_id in gate_owners:
                errors.append(f"gate ID is defined by more than one step: {gate_id}")
            gate_owners[gate_id] = (step_id, row[1])

        if re.search(r"\bM\d{2}-A\d+\b", text):
            errors.append(f"{filename} copies M-module recipe actions instead of referencing MI-* interfaces")
        if re.search(r"(?m)^\|\s*workflow_role\s*\|", text):
            errors.append(f"{filename} contains a copied task card")
        if re.search(r"(?m)^###\s+P\d{2}", text):
            errors.append(f"{filename} contains copied global policy definitions")

    if duplicates(consumed_instances):
        errors.append(
            "configured module instances must belong to exactly one step; duplicates: "
            + ", ".join(duplicates(consumed_instances))
        )
    missing_instances = sorted(set(instance_types) - set(consumed_instances))
    extra_instances = sorted(set(consumed_instances) - set(instance_types))
    if missing_instances:
        errors.append(f"selected module instances are not composed by a step: {', '.join(missing_instances)}")
    if extra_instances:
        errors.append(f"steps compose unknown module instances: {', '.join(extra_instances)}")

    graph_body = root_sections[HEADINGS[8]]
    known_steps = set(indexed_steps)
    for header in REQUIRED_TABLES[HEADINGS[8]]:
        for row in extract_table(graph_body, header) or []:
            for referenced_step in STEP_RE.findall(" ".join(row)):
                if referenced_step not in known_steps:
                    errors.append(f"Section 8 references unknown step {referenced_step}")

    gate_index_rows = extract_table(graph_body, REQUIRED_TABLES[HEADINGS[8]][3]) or []
    indexed_gates: dict[str, tuple[str, str, str]] = {}
    for row in gate_index_rows:
        if len(row) != 7 or row[0] == "N/A":
            continue
        indexed_gates[row[0]] = (row[1], row[2], row[3])
    if set(indexed_gates) != set(gate_owners):
        errors.append("Section 8 gate index must match the gates defined in STEP-* files exactly")
    for gate_id, (step_id, gate_class) in gate_owners.items():
        indexed = indexed_gates.get(gate_id)
        if indexed and indexed != (step_id, f"steps/{step_id}.md", gate_class):
            errors.append(f"Section 8 gate index disagrees with {step_id} for {gate_id}")
    return errors


def validate_package_texts(
    root_text: str,
    global_text: str,
    validation_text: str,
    step_texts: dict[str, str],
    module_texts: dict[str, str],
    mapping_roles: set[str],
    mapping_name: str,
    mapping_path: Path | None = None,
    plan_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    root_headings = HEADINGS[:9] + [HEADINGS[10], HEADINGS[12], HEADINGS[13], HEADINGS[14]]
    root_sections, root_heading_errors = split_owned_sections(root_text, root_headings, "plan-workflow.md")
    global_sections, global_heading_errors = split_owned_sections(global_text, [HEADINGS[9]], "global-rules.md")
    validation_sections, validation_heading_errors = split_owned_sections(
        validation_text, [HEADINGS[15], HEADINGS[16]], "validation.md"
    )
    errors.extend(root_heading_errors + global_heading_errors + validation_heading_errors)

    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Modular Execution Plan\s*$", root_text)) != 1:
        errors.append("plan-workflow.md must have exactly one modular execution plan title")
    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Global Workflow Rules\s*$", global_text)) != 1:
        errors.append("global-rules.md must have exactly one global workflow rules title")
    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Plan Validation\s*$", validation_text)) != 1:
        errors.append("validation.md must have exactly one plan validation title")
    if errors:
        return errors

    combined_markdown = "\n\n".join(
        [root_text, global_text, validation_text, *step_texts.values(), *module_texts.values()]
    )
    unresolved = sorted(set(re.findall(r"\{\{[^}\n]+\}\}", combined_markdown)))
    if unresolved:
        errors.append(f"unresolved template tokens remain: {', '.join(unresolved[:5])}")
    if "TEMPLATE NOTE:" in combined_markdown:
        errors.append("TEMPLATE NOTE lines remain in the execution package")
    angle_placeholders = sorted(set(re.findall(r"<[^>\n]+>", combined_markdown)))
    if angle_placeholders:
        errors.append(f"angle-bracket placeholders remain: {', '.join(angle_placeholders[:5])}")

    by_section = {**root_sections, **global_sections, **validation_sections, HEADINGS[11]: ""}
    errors.extend(validate_required_tables(by_section))
    contract_errors, topology = validate_plan_contract(
        root_sections[HEADINGS[0]], mapping_name, mapping_path, plan_path
    )
    errors.extend(contract_errors)
    module_errors, instance_types, joined_instances = validate_module_files(module_texts)
    errors.extend(module_errors)
    by_section[HEADINGS[11]] = joined_instances
    errors.extend(validate_step_files(root_sections, step_texts, instance_types))
    errors.extend(validate_policies(global_sections[HEADINGS[9]]))
    errors.extend(validate_verification_economy(
        root_sections[HEADINGS[0]], global_sections[HEADINGS[9]], combined_markdown
    ))
    errors.extend(validate_cross_references(by_section, instance_types))
    errors.extend(validate_roles(root_sections[HEADINGS[7]], mapping_roles, mapping_name, combined_markdown, topology))
    errors.extend(validate_root_acceptance_ownership(root_sections))
    errors.extend(validate_module_policy_and_role_references(
        global_sections[HEADINGS[9]], step_texts, module_texts, mapping_roles
    ))
    errors.extend(validate_unbounded_agent_sessions(combined_markdown, mapping_roles))
    errors.extend(validate_rule_and_check_matrices(by_section))

    task_roles: set[str] = set()
    for _, _, card_body in task_card_blocks(joined_instances):
        rows = extract_table(card_body, ("Field", "Value")) or []
        values = {row[0]: row[1] for row in rows if len(row) == 2}
        if role := values.get("workflow_role"):
            task_roles.add(role)
    unknown_task_roles = sorted(task_roles - mapping_roles)
    if unknown_task_roles:
        errors.append(f"module cards use roles absent from the mapping: {', '.join(unknown_task_roles)}")

    for phrase in ("as needed", "if useful", "best practice"):
        if phrase in joined_instances.lower():
            errors.append(f"module local instructions contain banned vague phrase: {phrase!r}")
    if re.search(r"(?m)^###\s+P\d{2}", root_text + "\n" + validation_text + "\n" + "\n".join(step_texts.values())):
        errors.append("global policy definitions appear outside global-rules.md")
    if re.search(r"\bM\d{2}-A\d+\b", root_text + "\n" + global_text + "\n" + validation_text):
        errors.append("M-module recipe action definitions appear outside modules/Mxx.md")
    return errors


def markdown_table(header: tuple[str, ...], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def build_self_test_package() -> tuple[str, str, str, dict[str, str], dict[str, str]]:
    root_parts = ["# Validator Self Test - Modular Execution Plan"]
    root_parts += [
        HEADINGS[0],
        markdown_table(("Field", "Value"), [
            ["Plan ID", "SELF-TEST"],
            ["Plan version", "1"],
            ["Status", "VALIDATED"],
            ["Decision owner", "orchestrator"],
            ["Orchestration topology", "ROOT_DIRECT_WORKERS"],
            ["Verification protocol", "N/A"],
            ["Operative document boundary", "self-test package"],
            ["Change procedure", "edit the owning artifact"],
            ["Definition of valid", "semantic and deterministic checks pass"],
        ]),
        markdown_table(PACKAGE_DEPENDENCY_TABLE, [
            ["Global rules", "global-rules.md", "policies", "steps and modules", "compatible policy edits"],
            ["Gated steps", "steps/", "step composition", "composition root", "compatible step edits"],
            ["M-module library", "modules/M01.md through modules/M10.md", "module process", "steps", "compatible module edits"],
            ["Agent mapping", "mapping.json", "agent selection", "runtime resolver", "mapping-only edits"],
            ["Validation", "validation.md", "validation results", "delivery", "observes only"],
        ]),
    ]
    root_parts += [
        HEADINGS[1],
        markdown_table(REQUIRED_TABLES[HEADINGS[1]][0], [["SRC-001", "goal", "goal.md", "requirements", "user wins"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[1]][1], [["1", "user", "goal", "N/A"]]),
        HEADINGS[2],
        "Goal: validate the modular package validator.",
        markdown_table(REQUIRED_TABLES[HEADINGS[2]][0], [["OUT-001", "valid plan behavior", "validator pass", "orchestrator", "covered"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[2]][1], [["BOUND-001", "in scope", "validation", "self test", "orchestrator"]]),
        HEADINGS[3],
        markdown_table(REQUIRED_TABLES[HEADINGS[3]][0], [["REQ-001", "SRC-001", "DEL-001", "orchestrator", "CHECK-001", "orchestrator", "covered"]]),
        HEADINGS[4],
        markdown_table(REQUIRED_TABLES[HEADINGS[4]][0], [["validation", "ORCHESTRATOR_ENFORCED", "script", "orchestrator", "plan", "exit 0", "fix"]]),
        HEADINGS[5],
        markdown_table(REQUIRED_TABLES[HEADINGS[5]][0], [["DEL-001", "valid plan", "REQ-001", "none", "schema", "plan"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[5]][1], [["DEL-001", "shape error", "invalid", "low", "short", "none", "M05", "accept"]]),
        HEADINGS[6],
        markdown_table(REQUIRED_TABLES[HEADINGS[6]][0], [["STEP-001", "steps/STEP-001.md", "candidate", "accepted result", "GATE-001", "orchestrator"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[6]][1], [[module_id, f"modules/{module_id}.md"] for module_id in MODULE_IDS]),
        HEADINGS[7],
        markdown_table(ROLE_TABLE, [
            ["orchestrator", "ROOT", "N/A", "worker", "accept", "1", "bounded", "none", "none", "plan ready", "plan"],
            ["worker", "WORKER", "orchestrator", "N/A", "execute", "1", "bounded", "source", "workspace", "dispatched", "task"],
        ]),
        markdown_table(REQUIRED_TABLES[HEADINGS[7]][1], [["resolve at launch", "reject", "no plan edit"]]),
        HEADINGS[8],
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][0], [["EDGE-001", "STEP-001.accepted result", "terminal", "accepted", "serial", "N/A", "incomplete"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][1], [["N/A", "N/A", "N/A", "no parallel work", "N/A", "N/A", "N/A"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][2], [["PATH-001", "STEP-001 EDGE-001", "short", "none", "none", "only path"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][3], [["GATE-001", "STEP-001", "steps/STEP-001.md", "PRODUCT", "required plan behavior", "EDGE-001 terminal", "STEP-001 return route"]]),
        HEADINGS[10],
    ]
    for header in REQUIRED_TABLES[HEADINGS[10]]:
        root_parts.append(markdown_table(header, [["N/A"] * len(header)]))
    root_parts += [
        HEADINGS[12],
        markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [["N/A"] * 8]),
        HEADINGS[13],
        markdown_table(REQUIRED_TABLES[HEADINGS[13]][0], [["N/A"] * 8]),
        HEADINGS[14],
        markdown_table(REQUIRED_TABLES[HEADINGS[14]][0], [["N/A", "OUT_OF_SCOPE", "none", "none", "orchestrator", "terminal"]]),
    ]

    global_parts = ["# Validator Self Test - Global Workflow Rules", HEADINGS[9]]
    for policy in POLICY_HEADINGS:
        global_parts += [policy, markdown_table(POLICY_TABLE, [["orchestrator", "plan", "decide", "recorded", "plan", "MI-001"]])]
        if policy.startswith("### P14"):
            global_parts.append(markdown_table(EXCEPTION_TABLE, [["N/A"] * len(EXCEPTION_TABLE)]))

    validation_parts = [
        "# Validator Self Test - Plan Validation",
        HEADINGS[15],
        markdown_table(REQUIRED_TABLES[HEADINGS[15]][0], [[rule_id, "self test", "applied"] for rule_id in RULE_IDS]),
        HEADINGS[16],
        markdown_table(REQUIRED_TABLES[HEADINGS[16]][0], [[check_id, "PASS", "self test"] for check_id in CHECK_IDS]),
        "PLAN_STRUCTURE=VALID",
    ]

    module_texts: dict[str, str] = {}
    for module_id in MODULE_IDS:
        selected = module_id == "M05"
        module_parts = [
            f"# {module_id} - Self Test Module",
            MODULE_HEADINGS[0],
            markdown_table(MODULE_SELECTION_TABLE, [[module_id, "SELECTED" if selected else "OMITTED", "MI-001" if selected else "N/A", "self-test selection", "N/A"]]),
            MODULE_HEADINGS[1],
            "Stable typed input and output; internal process changes preserve this public contract.",
            MODULE_HEADINGS[2],
            "Concrete module rules cite P01-P15 and preserve the catalog recipe.",
            markdown_table(MODULE_ACTION_TABLE, [[str(index), action_id, f"execute {action_id}", "fixed self-test parameter", "orchestrator"] for index, action_id in enumerate(MODULE_ACTIONS[module_id], 1)]),
            MODULE_HEADINGS[3],
        ]
        if selected:
            module_parts.append("### MI-001 - M05: Acceptance")
            for field in INSTANCE_FIELDS:
                module_parts.append(f"#### {field}")
                if field == "Local instructions":
                    for card_kind, card_id, actions in (
                        ("Governing", "CARD-001", MODULE_ACTIONS["M05"]),
                        ("Member", "CARD-002", ["M05-A1"]),
                    ):
                        module_parts.append(f"##### {card_kind} task card: {card_id}")
                        task_rows = [[task_field, f"self-test concrete {task_field}"] for task_field in TASK_FIELDS]
                        task_rows[0][1] = f"schema=self-test; card_id={card_id}; module_instance_id=MI-001"
                        task_rows[TASK_FIELDS.index("workflow_role")][1] = "orchestrator"
                        task_rows[TASK_FIELDS.index("ordered_actions")][1] = "; ".join(actions)
                        module_parts.append(markdown_table(("Field", "Value"), task_rows))
                else:
                    module_parts.append("Self-test concrete value.")
        module_texts[f"{module_id}.md"] = "\n\n".join(module_parts) + "\n"

    valid_product_gate = [
        "GATE-001 / LOOP-001", "PRODUCT", "revision",
        "Does the required product plan behavior satisfy its acceptance contract?", "MI-001",
        "plan semantics", "DEL-001 product acceptance only",
        "only when a required product criterion fails or is genuinely undecidable",
        "EDGE-001 advances to terminal", "same MI-001 task", "one decision", "one owner",
        "unrelated credit preserved", "split on independent criterion",
    ]
    step_parts = [
        "# STEP-001 - Acceptance Step",
        STEP_HEADINGS[0],
        markdown_table(("Field", "Value"), [[field, "STEP-001" if field == "Step ID" else f"concrete {field}"] for field in STEP_CONTRACT_FIELDS]),
        STEP_HEADINGS[1], "Candidate input is ready and protected boundaries are fixed.",
        STEP_HEADINGS[2], markdown_table(STEP_COMPOSITION_TABLE, [["1", "MI-001", "M05", "candidate", "accepted result", "candidate ready"]]),
        STEP_HEADINGS[3], "Accepted result advances through EDGE-001 to terminal.",
        STEP_HEADINGS[4], markdown_table(STEP_GATE_TABLE, [valid_product_gate]),
        STEP_HEADINGS[5], "Classified failure returns to MI-001 at its first unresolved action; unrelated credit is preserved.",
        STEP_HEADINGS[6], "One isolated lane; runtime IDs, cleanup, and terminal state are concrete.",
        STEP_HEADINGS[7], "Short expected range with one gate and no avoidable serial cost.",
    ]
    return (
        "\n\n".join(root_parts) + "\n",
        "\n\n".join(global_parts) + "\n",
        "\n\n".join(validation_parts) + "\n",
        {"STEP-001.md": "\n\n".join(step_parts) + "\n"},
        module_texts,
    )


def run_self_test() -> list[str]:
    root, global_rules, validation_doc, steps, modules = build_self_test_package()
    failures: list[str] = []

    def check(root_text: str = root, global_text: str = global_rules, validation_text: str = validation_doc,
              step_texts: dict[str, str] | None = None, module_texts: dict[str, str] | None = None,
              roles: set[str] | None = None) -> list[str]:
        self_test_plan_path = (Path.cwd() / "__validator_self_test__" / "package").resolve()
        self_test_mapping_path = self_test_plan_path / "mapping.json"
        return validate_package_texts(
            root_text, global_text, validation_text,
            steps if step_texts is None else step_texts,
            modules if module_texts is None else module_texts,
            {"orchestrator", "worker"} if roles is None else roles, "mapping.json",
            self_test_mapping_path, self_test_plan_path,
        )

    if errors := check():
        failures.append("valid fixture failed: " + "; ".join(errors))
    checkpoint_root = root.replace(
        "| Verification protocol | N/A |",
        "| Verification protocol | CHECKPOINTED_VERIFICATION_V1 |",
        1,
    )
    checkpoint_global = global_rules.replace(
        "| orchestrator | plan | decide | recorded | plan | MI-001 |",
        "| orchestrator | checkpoint | input map; first unresolved; earliest required; "
        "ordinary failure continuation | recorded | plan | MI-001 |",
        1,
    )
    if errors := check(root_text=checkpoint_root, global_text=checkpoint_global):
        failures.append("valid checkpoint protocol failed: " + "; ".join(errors))
    fast_lane_global = checkpoint_global + (
        "\nFAST_LANE_V2 complete pool motivating test compile review integration smoke credit\n"
    )
    if errors := check(root_text=checkpoint_root, global_text=fast_lane_global):
        failures.append("valid FAST_LANE_V2 protocol failed: " + "; ".join(errors))

    corruptions: dict[str, list[str]] = {
        "placeholder": check(root_text=root + "\n{{UNFILLED}}\n"),
        "checkpoint marker without policy": check(root_text=checkpoint_root),
        "checkpoint marker outside Section 0": check(
            root_text=root + "\nCHECKPOINTED_VERIFICATION_V1\n"
        ),
        "FAST_LANE_V2 without checkpoint protocol": check(
            global_text=global_rules + "\nFAST_LANE_V2\n"
        ),
        "checkpoint protocol without earliest required route": check(
            root_text=checkpoint_root,
            global_text=checkpoint_global.replace("earliest required", "resume point", 1),
        ),
        "FAST_LANE_V2 without complete pool": check(
            root_text=checkpoint_root,
            global_text=fast_lane_global.replace("complete pool", "partial result", 1),
        ),
    }
    missing_module = dict(modules); missing_module.pop("M10.md")
    corruptions["missing M file"] = check(module_texts=missing_module)
    corruptions["missing indexed step"] = check(step_texts={})
    bad_action = dict(modules)
    bad_action["M05.md"] = bad_action["M05.md"].replace("| 10 | M05-A10 |", "| 10 | M05-A9 |", 1)
    corruptions["module action inventory"] = check(module_texts=bad_action)
    copied_action_step = dict(steps); copied_action_step["STEP-001.md"] += "\nM05-A1\n"
    corruptions["step copies module process"] = check(step_texts=copied_action_step)
    bad_gate = dict(steps)
    bad_gate["STEP-001.md"] = bad_gate["STEP-001.md"].replace("| GATE-001 / LOOP-001 | PRODUCT |", "| GATE-001 / LOOP-001 | ADVISORY |", 1)
    corruptions["gate class"] = check(step_texts=bad_gate)
    bare_card = dict(modules)
    bare_card["M05.md"] = bare_card["M05.md"].replace("| objective | self-test concrete objective |", "| objective | N/A |", 1)
    corruptions["bare dispatch field"] = check(module_texts=bare_card)
    missing_card = dict(modules)
    missing_card["M05.md"] = missing_card["M05.md"].replace("##### Governing task card: CARD-001", "##### Member task card: CARD-001", 1)
    corruptions["missing governing card"] = check(module_texts=missing_card)
    bad_member_actions = dict(modules)
    bad_member_actions["M05.md"] = bad_member_actions["M05.md"].replace("| ordered_actions | M05-A1 |", "| ordered_actions | M05-A2; M05-A1 |", 1)
    corruptions["member action order"] = check(module_texts=bad_member_actions)
    duplicate_card = dict(modules)
    duplicate_card["M05.md"] = duplicate_card["M05.md"].replace("##### Member task card: CARD-002", "##### Member task card: CARD-001", 1)
    corruptions["duplicate task-card ID"] = check(module_texts=duplicate_card)
    corruptions["mapping-role mismatch"] = check(roles={"different-role"})
    bad_authority = root.replace("| worker | WORKER | orchestrator |", "| worker | LANE_SUB_ORCHESTRATOR | orchestrator |", 1)
    corruptions["forbidden sub-orchestrator tier"] = check(root_text=bad_authority)
    corruptions["duplicate mapping path"] = check(root_text=root + "\nmapping.json\n")
    corruptions["wrong mapping location"] = check(
        root_text=root.replace("| Agent mapping | mapping.json |", "| Agent mapping | wrong/mapping.json |", 1)
    )
    corruptions["worker as global decision owner"] = check(
        root_text=root.replace("| Decision owner | orchestrator |", "| Decision owner | worker |", 1)
    )
    corruptions["worker as requirement acceptance owner"] = check(
        root_text=root.replace("| CHECK-001 | orchestrator | covered |", "| CHECK-001 | worker | covered |", 1)
    )
    bad_policy = dict(modules)
    bad_policy["M05.md"] = bad_policy["M05.md"].replace("P01-P15", "P98", 1)
    corruptions["unknown module policy"] = check(module_texts=bad_policy)
    bad_owner = dict(modules)
    bad_owner["M05.md"] = bad_owner["M05.md"].replace("| orchestrator |", "| unknown-owner |", 1)
    corruptions["unknown module decision owner"] = check(module_texts=bad_owner)
    corruptions["bounded agent session"] = check(
        global_text=global_rules + "\nAgent and subagent sessions have a 30-second maximum lifetime.\n"
    )
    corruptions["mixed bounded agent session exception"] = check(
        global_text=global_rules
        + "\nAgent sessions are unbounded, but review agent sessions have a 30-second deadline.\n"
    )
    corruptions["role-named bounded invocation"] = check(
        global_text=global_rules + "\nReviewer invocations have a 30-second deadline.\n"
    )
    corruptions["bounded session within duration"] = check(
        global_text=global_rules + "\nAgent sessions must finish within 30 seconds.\n"
    )
    for label, errors in corruptions.items():
        if not errors:
            failures.append(f"{label} corruption was not detected")
    with tempfile.TemporaryDirectory() as temp_dir:
        package = Path(temp_dir)
        for filename in ("plan-workflow.md", "global-rules.md", "validation.md"):
            (package / filename).write_text("self-test\n", encoding="utf-8")
        (package / "steps").mkdir()
        (package / "modules").mkdir()
        (package / "unexpected.bin").write_bytes(b"unexpected")
        package_errors = load_package(package)[-1]
        if "unexpected root package file: unexpected.bin" not in package_errors:
            failures.append("extra non-Markdown package file was not detected")
    return failures


def load_mapping(path: Path) -> tuple[set[str], list[str]]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return set(), [f"cannot read role-agent mapping {path}: {exc}"]
    if not isinstance(data, dict) or not isinstance(data.get("roles"), dict):
        return set(), ["role-agent mapping must be a JSON object containing a roles object"]
    roles = data["roles"]
    errors = [
        f"mapping role {role!r} must contain a nonempty agent-selection object"
        for role, value in roles.items()
        if not isinstance(value, dict) or not value
    ]
    if not roles:
        errors.append("role-agent mapping contains no roles")
    return set(roles), errors


def load_package(path: Path) -> tuple[str, str, str, dict[str, str], dict[str, str], list[str]]:
    errors: list[str] = []
    if not path.is_dir():
        return "", "", "", {}, {}, [f"execution plan path must be a package directory: {path}"]
    required_files = ("plan-workflow.md", "global-rules.md", "validation.md")
    texts: dict[str, str] = {}
    for filename in required_files:
        file_path = path / filename
        try:
            texts[filename] = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read required package file {file_path}: {exc}")

    for entry in path.iterdir():
        if entry.is_dir() and entry.name not in {"steps", "modules"}:
            errors.append(f"unexpected package directory: {entry.name}")
        if entry.is_file() and entry.name not in required_files:
            errors.append(f"unexpected root package file: {entry.name}")

    child_texts: dict[str, dict[str, str]] = {"steps": {}, "modules": {}}
    for dirname in ("steps", "modules"):
        directory = path / dirname
        if not directory.is_dir():
            errors.append(f"missing required package directory: {dirname}/")
            continue
        for entry in directory.iterdir():
            if not entry.is_file() or entry.suffix.lower() != ".md":
                errors.append(f"unexpected item in {dirname}/: {entry.name}")
                continue
            try:
                child_texts[dirname][entry.name] = entry.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read {entry}: {exc}")
    return (
        texts.get("plan-workflow.md", ""),
        texts.get("global-rules.md", ""),
        texts.get("validation.md", ""),
        child_texts["steps"],
        child_texts["modules"],
        errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a modular execution-plan package's deterministic structure.")
    parser.add_argument("plan", nargs="?", help="generated execution-plan package directory")
    parser.add_argument("--mapping", help="canonical role-agent mapping JSON path")
    parser.add_argument("--self-test", action="store_true", help="run validator contract tests")
    args = parser.parse_args()

    if args.self_test:
        failures = run_self_test()
        if failures:
            for failure in failures:
                print(f"SELF-TEST ERROR: {failure}", file=sys.stderr)
            return 1
        print("execution plan validator self-test: PASS")
        return 0

    if args.plan is None or args.mapping is None:
        parser.error("plan and --mapping are required unless --self-test is used")
    mapping_path = Path(args.mapping)
    mapping_roles, mapping_errors = load_mapping(mapping_path)
    if mapping_errors:
        for error in mapping_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    root_text, global_text, validation_text, step_texts, module_texts, package_errors = load_package(Path(args.plan))
    errors = package_errors
    if not errors:
        errors = validate_package_texts(
            root_text,
            global_text,
            validation_text,
            step_texts,
            module_texts,
            mapping_roles,
            mapping_path.name,
            mapping_path,
            Path(args.plan),
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("execution plan validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
