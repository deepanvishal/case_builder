# Context Pack — FM
_Generated 2026-06-15. Curated inputs only — not the full corpus._

## Definitions (single source of truth — use VERBATIM)
```yaml
# definitions.yml â€” SINGLE SOURCE OF FACTUAL TRUTH
# Field, peer group, and every key number stated ONCE. Every agent loads this and
# uses these terms/figures VERBATIM. coherence_checker + gates.py enforce it.
# <...> = you fill. Pre-filled values are locked from prior work â€” confirm them.
# Never state any of these differently anywhere else in the package.

beneficiary:
  name: "<full legal name>"
  occupation_title: "Lead Data Scientist"
  soc_code: "15-2051"                 # Data Scientists (corrected from 15-2041 Statisticians)

field:
  # ONE favorable-but-defensible definition of "the field". Used identically everywhere.
  definition: "<one sentence, e.g. applied AI / data science for regulated healthcare decision systems>"
  scope_notes: "<what is in / out of scope, if needed>"

peer_group:
  # Who "top of field" is measured against. Correct occupation + senior tier only.
  definition: "Lead / Senior / Principal Data Scientists (SOC 15-2051)"
  tier: [lead, senior, principal]
  geography: "Tallahassee, FL MSA"    # worksite of record per payslips
  exclude: "general-population data scientists; job-ad ranges; crowdsourced data (levels.fyi/Glassdoor/Indeed)"

filing:
  receipt: "IOE0936623174"
  filing_date: "2026-04-27"
  at_filing_employer: "CVS Health (Aetna Resources LLC)"
  response_deadline: "2026-08-10"

# KEY NUMBERS â€” each stated ONCE with its ledger ID. The diff gate checks these.
numbers:
  total_comp_2025:
    value: "$193,043.61"              # confirm Box 1 vs Box 5; bump ledger version if revised
    ledger_id: "HS-01"
    note: "base only in record; bonus/RSU/equity is the open lever"
  peer_benchmark_p90:
    value: "<$ figure>"               # correct-peer top-decile: DOL LCA FY2025, SOC 15-2051, Level IV, Tallahassee MSA
    ledger_id: "HS-14"
    note: "STAGED until verified against primary source"
  percentile_position:
    value: "<percentile>"             # derived: total_comp vs peer_benchmark_p90
    ledger_id: "HS-D20"
  forward_citations_count:
    value: "<n>"                      # examiner-majority forward citations of US20230162844A1; set from VERIFIED count
    ledger_id: "<OC-xx>"
  # Add any other recurring figure here and ONLY here (e.g. org market rank,
  # customer-relationship count â€” pick ONE value and use it everywhere).

criteria_in_play:
  rfe_challenged: [OC, CR, HS]        # OCMS, Critical Role, High Salary
  accepted: [<fill codes>]           # originally-accepted criteria
  # FM = Final Merits (the section being built)

contribution:
  name: "Brighter Match"
  public_artifact: "US20230162844A1 (published patent application)"
  framing: "OCMS argued from the PUBLISHED patent + its forward citations â€” NOT the confidential deployment. Critical Role keeps the proprietary framing."
```

## RFE — governing language
# RFE Response Notes
<!-- Paste or summarise RFE text here. TODO: fill content. -->

## Evidence set (0 verified facts tagged FM)
_No verified FM-tagged facts in the ledger yet._
