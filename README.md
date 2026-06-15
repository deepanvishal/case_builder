# case_builder — EB-1A RFE Final Merits pipeline

A one-time, human-in-the-loop pipeline that assembles the Final Merits section of an
EB-1A RFE response. Narrow subagents (agents/) draft, critique, synthesize, and check;
thin Python gates (gates/) enforce sourcing and consistency; the human orchestrates,
verifies every fact, and signs off. See RUNBOOK.md for phase order and CLAUDE.md for
operating rules.

## Four invariants
1. corpus/exhibits/ is read-only (chain of custody).
2. trace/run-log.jsonl is append-only (audit).
3. corpus/staging/ → corpus/ledger/ only after the human verifies against the primary source.
4. corpus/definitions.yml states the field, peer group, and key numbers once; everything else references them.
