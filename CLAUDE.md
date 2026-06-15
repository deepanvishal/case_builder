# CLAUDE.md — EB-1A Final Merits pipeline

## What this repo is
One-time, human-in-the-loop pipeline to produce the Final Merits section.
The human is the orchestrator. You execute one scoped step at a time.

## INVARIANTS — never violate (rule · why · what breaking it looks like)
1. corpus/exhibits/ is READ-ONLY — chain of custody — never write a file there, even to fix a typo.
2. trace/run-log.jsonl is APPEND-ONLY — auditability — never edit or delete a prior line.
3. corpus/staging/ → corpus/ledger/ ONLY after the human verifies against the primary source — no fabrication — you never promote a fact yourself; nothing drafts off staging/.
4. Every factual claim resolves to a ledger ID; a citation you cannot verify is flagged, never asserted — overclaiming taints the whole petition.

## Single sources of truth — load, never restate
- facts → corpus/definitions.yml
- law → reference/legal_framework.md
- format → reference/house_format.md
- gate rules → rules/*.yml

## Folder contract
- case/ — read-only RFE + petition + prior drafts (framing)
- corpus/ — exhibits (raw, read-only), ledger (verified facts), staging (unverified), definitions.yml
- reference/ — legal + format single-sources
- rules/ — gate inputs
- agents/ — subagent prompts (one job each)
- gates/ — Python validators
- work/ — pipeline outputs (drafts, components, critiques, defects.jsonl, final_merits.md)
- trace/ — append-only run log

## Workflow (Final Merits)
curate → matrix → draft → critic+legal-flag → synthesize → gates → legal_checker → coherence → risk_register → adjudicate → sign off
Every step appends one line to trace/run-log.jsonl.

## House rules
- Do one step at a time; stop and report. Don't chain phases unprompted.
- Stubs/skeleton ≠ content. Don't write prompt bodies or gate logic unless asked.
- Ask before installing anything or touching files outside the named step.
