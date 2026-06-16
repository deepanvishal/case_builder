# Expert Letter Audit Template (RFE 5.4 compliance)
# Copy per letter -> work/letters/audits/<letter_id>.md. Score against the rubric, inventory every
# factual claim against the ledger, set a verdict. This is an AUDIT, not a filing.

letter_id:             # e.g. A(1)(a)
author:                # name as it appears in the letter
refetch_status:        # refetchable | non-refetchable (audit-only)
independence:          # independent (non-supervisor) | supervisor/employer | unclear

# RFE 5.4 rubric -- mark each: present | partial | absent, with a one-line note
rubric:
  identifies_contribution:         #
  explains_originality:            #
  describes_significance_to_field: #  to the FIELD as a whole, not just an employer
  connects_opinion_to_facts:       #
  author_credentials_qualified:    #
  how_author_knows_work:           #  + independent knowledge of use/impact?
  contribution_dates_context:      #
  why_not_routine_implementation:  #
  how_it_affected_the_field:       #  industry practice, adoption, outcomes, compliance, governance
  specific_metrics_corroboration:  #  metrics, adoption, citations, deployments, corroborating docs
  why_top_level_professional:      #

# Every factual claim in the letter, mapped to corroboration
claims_inventory:
  - claim:             # the literal assertion
    ledger_id:         # corroborating fact ID, or "GAP"
    do_not_rely:       # Y if uncorroborated / contradicted / unverifiable, else N
    action:            # keep | strip | route-to-hunter (mandate id)

questionable_specifics:  # claims to STRIP because unverifiable or internally inconsistent
  -

verdict:               # revise-to-spec (refetchable) | audit-only-flag (non-refetchable) | ok-as-is
notes:                 #
