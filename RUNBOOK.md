# RUNBOOK — Final Merits Phase Order

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
