# Strategy Research Mandate Template (practitioner intelligence — NOT evidence)
# Copy per task -> work/mandates/<mandate_id>.md, fill EVERY field, hand to the hunter.
# Output goes to reference/strategy_notes.md as ADVISORY observations.
# Strategy findings are NEVER cited, NEVER filed, NEVER promoted to staging/ or the ledger,
# and NEVER override reference/legal_framework.md. They inform HOW we argue, not WHAT we assert.

mandate_id:            # e.g. STRAT-ocms-01
serves_strategy:       # the framing/tactics question this informs
                       # e.g. "How are 2025-26 EB-1A OCMS RFEs being rebutted successfully?"
why:                   # what decision in our response this will shape

questions:             # 2-5 concrete questions about adjudication patterns / framing
  -                    # e.g. "What OCMS RFE language appears for industry (non-academic) profiles?"
  -                    # e.g. "What evidence/arguments answered it in reported approvals?"

source_bar:
  prefer:              # practitioner-intelligence sources (recency-weighted)
    - r/immigration, r/EB1, r/immigrationlaw, r/USCIS and similar practitioner forums
    - USCIS-tracker / petition-template GitHub repos
    - immigration-attorney and practitioner blogs / firm write-ups
    - AAO non-precedent decisions; USCIS Policy Manual updates
  treat_as_low_signal: # capture but mark low-confidence
    - single anonymous anecdote with no corroboration
    - marketing / mill content selling services
    - posts with no service center, date, or criterion specifics
  ignore:
    - spam, off-topic, unrelated visa categories

recency:               # REQUIRED window; default <12 months (e.g. "2025-06 to 2026-06")

# OUTPUT to reference/strategy_notes.md, per observation:
#   pattern        - the trend/tactic in one line
#   detail         - specifics (criterion, service center if known, what worked/failed)
#   sources        - links + dates (note how many INDEPENDENT reports support it)
#   confidence     - high (multi-source) | medium | low (single anecdote)
#   applies_to_us  - how it maps to THIS case + which section it informs
#   check_vs_law   - does it square with legal_framework.md? flag any conflict
# Plus dead_ends.
#
# CAVEAT baked in: reported approvals are self-reported, survivorship-biased, and
# service-center-specific. Treat every pattern as a HYPOTHESIS to weigh against the
# actual case law, never as a rule.
