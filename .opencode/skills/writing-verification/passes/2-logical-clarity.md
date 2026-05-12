# Pass 2: Logical Clarity

Audit claim-evidence chains, reasoning soundness, quantitative precision, and hedging calibration.

## Checklist

- [ ] **All claims identified**: Every assertion the reader is asked to believe is listed
- [ ] **Evidence present for each claim**: No unsupported assertions
- [ ] **Logic flows without gaps**: Each conclusion follows from stated premises
- [ ] **Hedging calibrated**: Strength of language matches strength of evidence
- [ ] **Quantitative where possible**: Numbers replace vague quantifiers
- [ ] **No logical fallacies**: No circular reasoning, false equivalence, straw men
- [ ] **Mechanisms explained**: "How" is addressed, not just "what"

## Claim-Evidence Audit

For each major claim:

```
CLAIM: [what the author asserts]
EVIDENCE: [what supports it — data, citation, logic, authority]
STRENGTH: [strong / moderate / weak / missing]
HEDGE USED: [word used — "proves", "suggests", "may", etc.]
HEDGE APPROPRIATE: [yes / overclaimed / underclaimed]
ISSUES: [if any]
```

See [../reference/hedging-calibration.md](../reference/hedging-calibration.md) for the 5-level scale.

## Logic Flow Check

For key arguments, map the reasoning:

```
PREMISE 1 → PREMISE 2 → INFERENCE → CONCLUSION
Gap? [yes/no]  Leap? [yes/no]  Hidden assumption? [yes/no]
```

## Quantitative Precision

Flag any instance of:
- "significant" without a metric
- "many/most/some" when a number is available
- "increased/decreased" without magnitude
- Comparisons without baselines

## Output

```
PASS 2 RESULT: PASS / FAIL
Claims audited: [count]
Overclaimed: [count]
Logical gaps: [count]
Vague quantifiers: [count]
Blockers: [list, or "none"]
Warnings: [list, or "none"]
```

A logical gap that undermines the core argument is a blocker.
