# Level 2 — delegated investigation and review

Use this level to design how a later executor will gain independent evidence
without creating competing writers. The planned primary agent owns all future
implementation, integration, and final decisions. This reference defines the
plan; it does not launch investigators or perform the implementation.

## Build the topology

1. State the primary outcome and the decision the extra evidence will inform.
2. Split only read-only lanes that are genuinely independent: for example,
   repository mapping and focused test discovery; a failure reproduction and a
   read-only design review; or two separate external sources.
3. Give each lane a concrete, scope-bounded task card:

   ```text
   Objective:
   Scope and entrypoints:
   Write authority: none
   Deliverable: findings with file/line or command evidence
   Checks allowed:
   Completion: the question is answered or the uncertainty is named
   ```

4. Specify a native subagent when available. Otherwise specify the installed matching
   command-line worker—an unbounded `codex exec` or `claude -p` agent session—when that isolation is
   worth the startup cost. State that the future executor must never put the agent launch or session under the finite-command supervisor;
   only an explicitly manifest-selected finite command invoked inside it is bounded.
5. Define a single collection point where the planned primary agent compares
   evidence, resolves conflicts, and makes the implementation decision. Findings
   are inputs, not votes.
6. Route future implementation through one writer, followed by focused
   verification selected from the combined evidence.

## Useful shapes

| Need | Shape |
| --- | --- |
| Unfamiliar failure | One investigator maps reproduction/call path; primary agent implements. |
| Consequential local change | Primary agent drafts; one read-only reviewer critiques the diff or plan. |
| Independent questions | Two read-only investigators return evidence; primary agent reconciles and writes. |

## Do not add

- parallel writers or worktrees;
- a coordinator process, lane registry, or persistent state;
- a review merely because a review skill exists; or
- a second investigation after the first result is already decisive.

If the writer needs to be split, reassess at Level 3 rather than quietly adding a
second writer to Level 2.
