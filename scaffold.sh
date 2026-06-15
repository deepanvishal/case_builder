#!/usr/bin/env bash
# scaffold.sh — idempotent repo skeleton for EB-1A Final Merits pipeline
# Safe to re-run: creates files only if absent.
set -euo pipefail

# Helper: create file only if it does not already exist
mkf() {
  local path="$1"; shift
  if [[ ! -e "$path" ]]; then
    mkdir -p "$(dirname "$path")"
    printf '%s' "$*" > "$path"
    echo "  created  $path"
  else
    echo "  exists   $path"
  fi
}

# Helper: create empty directory with .gitkeep only if absent
mkd() {
  local dir="$1"
  mkdir -p "$dir"
  mkf "$dir/.gitkeep" ""
}

echo "=== scaffolding repo ==="

# ── case/ ─────────────────────────────────────────────────────────────────────
mkdir -p case/prior_drafts
mkf case/rfe.md "# RFE Response Notes
<!-- Paste or summarise RFE text here. TODO: fill content. -->
"
mkf case/petition.md "# Petition Summary
<!-- High-level petition narrative stub. TODO: fill content. -->
"
mkf case/prior_drafts/.gitkeep ""

# ── corpus/ ───────────────────────────────────────────────────────────────────
mkd corpus/exhibits
mkd corpus/ledger
mkd corpus/staging
mkf corpus/definitions.yml "# corpus/definitions.yml
# Single responsibility: canonical source of truth for field name,
# peer comparators, and numerical claims used across all agents.
# TODO: populate field_name, peer_set, base_numbers sections.
"

# ── reference/ ────────────────────────────────────────────────────────────────
mkf reference/legal_framework.md "<!-- reference/legal_framework.md
Single responsibility: authoritative statement of EB-1A legal standards,
Kazarian two-step, and relevant AAO/court precedents.
TODO: fill legal content. -->
"
mkf reference/house_format.md "<!-- reference/house_format.md
Single responsibility: formatting conventions (headers, citation style,
exhibit labeling, table structure) applied by all drafting agents.
TODO: fill format rules. -->
"

# ── rules/ ────────────────────────────────────────────────────────────────────
mkf rules/banned_categorical.yml "# rules/banned_categorical.yml
# Single responsibility: list phrases and claim patterns that are
# categorically banned from any petition or RFE response draft.
# TODO: populate banned_patterns list.
"
mkf rules/completeness.yml "# rules/completeness.yml
# Single responsibility: checklist of required elements that every
# Final Merits section must contain before it may pass the gate.
# TODO: populate required_elements list.
"
mkf rules/rfe_noid_triggers.yml "# rules/rfe_noid_triggers.yml
# Single responsibility: catalog of known RFE / NOID trigger patterns
# to be flagged by officer_critic and legal_checker agents.
# TODO: populate trigger_patterns list.
"

# ── agents/ ───────────────────────────────────────────────────────────────────
mkf agents/hunter.md "# Agent: Hunter
**One job:** Locate and map all evidentiary exhibits in corpus/exhibits/
to the ten EB-1A criteria, producing a structured coverage matrix.

## INPUTS
- corpus/exhibits/ (read-only)
- corpus/definitions.yml

## OUTPUTS
- work/fm/components/evidence_matrix.md (coverage matrix)

## TODO
- Define exact output schema
- Write prompt body
"
mkf agents/drafter.md "# Agent: Drafter
**One job:** Compose the Final Merits narrative section-by-section from
the evidence matrix and legal framework, following house format rules.

## INPUTS
- work/fm/components/evidence_matrix.md
- reference/legal_framework.md
- reference/house_format.md
- corpus/definitions.yml

## OUTPUTS
- work/fm/components/draft_section_<criterion>.md per criterion
- work/drafts/fm_draft_v<N>.md (assembled draft)

## TODO
- Define section template
- Write prompt body
"
mkf agents/officer_critic.md "# Agent: Officer Critic
**One job:** Read each draft section as a skeptical USCIS officer and
flag weaknesses, missing evidence, and RFE/NOID risk patterns.

## INPUTS
- work/drafts/fm_draft_v<N>.md
- rules/rfe_noid_triggers.yml
- rules/completeness.yml

## OUTPUTS
- work/fm/critiques/officer_critique_v<N>.md
- defects appended to work/defects.jsonl

## TODO
- Define critique schema
- Write prompt body
"
mkf agents/synthesizer.md "# Agent: Synthesizer
**One job:** Merge accepted drafter output with addressed critique items
into a single revised draft, resolving conflicts under human oversight.

## INPUTS
- work/drafts/fm_draft_v<N>.md
- work/fm/critiques/officer_critique_v<N>.md
- Human verification sign-off

## OUTPUTS
- work/drafts/fm_draft_v<N+1>.md

## TODO
- Define merge rules
- Write prompt body
"
mkf agents/legal_checker.md "# Agent: Legal Checker
**One job:** Verify every legal citation and statutory reference in the
draft against reference/legal_framework.md and flag discrepancies.

## INPUTS
- work/drafts/fm_draft_v<N>.md
- reference/legal_framework.md

## OUTPUTS
- work/fm/critiques/legal_check_v<N>.md
- risk entries appended to work/risk_register.md

## TODO
- Define citation-check logic
- Write prompt body
"
mkf agents/coherence_checker.md "# Agent: Coherence Checker
**One job:** Confirm that all numerical claims, peer comparators, and
field definitions in the draft exactly match corpus/definitions.yml.

## INPUTS
- work/drafts/fm_draft_v<N>.md
- corpus/definitions.yml

## OUTPUTS
- work/fm/critiques/coherence_check_v<N>.md

## TODO
- Define consistency-check rules
- Write prompt body
"

# ── gates/ ────────────────────────────────────────────────────────────────────
mkf gates/gates.py '"""
gates/gates.py
Purpose: Enforce go/no-go criteria between pipeline phases.
         Each gate function returns (passed: bool, failures: list[str]).
TODO: implement gate logic per completeness.yml and ledger_schema.py.
"""

# TODO: implement gates
'
mkf gates/ledger_schema.py '"""
gates/ledger_schema.py
Purpose: Define and validate the schema for corpus/ledger/ entries,
         ensuring every promoted exhibit is fully catalogued.
TODO: implement schema class and validate() function.
"""

# TODO: implement schema
'
mkf gates/risk_register.py '"""
gates/risk_register.py
Purpose: Parse and aggregate risk entries from work/risk_register.md
         and surface blockers before final sign-off.
TODO: implement parse() and summarise() functions.
"""

# TODO: implement risk register logic
'

# ── work/ ─────────────────────────────────────────────────────────────────────
mkd work/fm/components
mkd work/fm/critiques
mkd work/drafts
mkf work/final_merits.md ""
mkf work/defects.jsonl ""
mkf work/risk_register.md ""

# ── trace/ ────────────────────────────────────────────────────────────────────
mkf trace/run-log.jsonl ""

# ── top-level ─────────────────────────────────────────────────────────────────
mkf README.md 'This repository implements a human-in-the-loop pipeline for drafting the
Final Merits section of an EB-1A extraordinary-ability petition. Agents
curate evidence, draft criterion-by-criterion, critique from an officer
perspective, check legal citations, and verify internal consistency —
each phase gated by human verification before promotion. Four invariants
govern every run: (1) corpus/exhibits/ is read-only; no agent may modify
source evidence. (2) trace/run-log.jsonl is append-only; completed runs
are never edited or deleted. (3) Staging artifacts in corpus/staging/ are
promoted to corpus/ledger/ only after explicit human sign-off. (4)
corpus/definitions.yml is the single source of truth for all field names,
peer comparators, and numerical claims; agents must not restate or
redefine these values independently.
'
mkf RUNBOOK.md '# RUNBOOK — Final Merits Phase Order

Human-in-the-loop checklist. Complete each step before advancing.

1. **Curate** — verify all exhibits in corpus/exhibits/; confirm read-only.
2. **Matrix** — run hunter agent; review evidence_matrix.md; human sign-off.
3. **Draft** — run drafter agent per criterion; review each section draft.
4. **Critic + Legal Flag** — run officer_critic and legal_checker in parallel;
   review critiques; triage defects.jsonl; human sign-off on each defect.
5. **Synthesize** — run synthesizer to incorporate accepted critique items;
   human reviews merged draft.
6. **Gates** — run gates.py; all gate checks must pass before continuing.
7. **Legal Checker** — re-run legal_checker on synthesized draft; resolve
   any remaining citation flags.
8. **Coherence** — run coherence_checker; confirm all numbers match
   corpus/definitions.yml; human sign-off.
9. **Risk Register** — run risk_register.py; review work/risk_register.md;
   resolve or accept each flagged risk.
10. **Adjudicate** — final human review of work/final_merits.md; confirm
    all defects closed and all gates green.
11. **Sign Off** — human approves; append final entry to trace/run-log.jsonl.
'
mkf requirements.txt 'pyyaml
'

echo ""
echo "=== scaffold complete ==="
