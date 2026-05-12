# Scientific Writing

For research papers, reviews, perspectives, grant proposals. IMRAD structure.

## Two-Stage Process

1. **Outline first** — Complete structural outline with one claim per section before any prose.
2. **Prose second** — Fill in the outline. Never bullet points in final output (unless methods/protocol).

## IMRAD Structure

| Section | Job | Key rule |
|---------|-----|----------|
| Introduction | Sell the problem | Funnel: Broad → Narrow → Gap → Hypothesis |
| Methods | Enable replication | Enough detail to reproduce |
| Results | Show data | Question → Approach → Finding → Interpretation |
| Discussion | Interpret | Hypothesis status → Context → Limitations → Future |

## Field-Specific Terminology

Use standard nomenclature for the discipline:
- **Biomedical:** MeSH terms, HGVS notation for variants
- **Chemistry:** IUPAC nomenclature
- **Molecular biology:** Gene Ontology terms, italicized gene names
- **Statistics:** Report exact p-values, confidence intervals, effect sizes

## Hedging Calibration

| Evidence | Use |
|----------|-----|
| Direct mechanistic proof | "demonstrates", "establishes" |
| Strong correlational, replicated | "shows", "indicates" |
| Moderate, single study | "suggests", "supports" |
| Preliminary or limited | "may", "appears to" |
| Speculation beyond data | "we speculate", "conceivably" |

## Reporting Guidelines

Use the appropriate checklist:
- Randomized trials: CONSORT
- Observational studies: STROBE
- Systematic reviews: PRISMA
- Diagnostic accuracy: STARD
- Prediction models: TRIPOD
- Animal research: ARRIVE
- Case reports: CARE
- Quality improvement: SQUIRE

## Quantitative Precision

Never write vague quantifiers. Replace:
- "large increase" → "3.5-fold increase"
- "often occurs" → "occurs in 75% of cases"
- "higher than control" → "2.1× higher (p < 0.01)"
- "multiple experiments" → "n = 6 biological replicates"

## LaTeX Conventions

- Display equations: `\begin{equation}...\end{equation}` with `\label{}`
- Inline: `$...$`
- Units: `\SI{10}{\micro\molar}` (siunitx)
- P-values: `$p < 0.001$` (never "p = 0.000")
- Confidence intervals: `95\% CI [1.2, 3.4]`
