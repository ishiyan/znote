# Technical Articles

Principles for developer-facing content: blog posts, tutorials, guides, documentation.

## The Thesis Spine

Every technical article has one core argument stated in one sentence. Every section must reinforce or extend it. After writing each section, ask: "Does this serve the thesis?" Remove anything that drifts.

## Narrative Arc

Technical articles follow this arc:

```
Problem → Pressure → Root Cause → Old Model Failure → New Model → Why It Works → How to Adopt
```

If the conclusion doesn't feel inevitable, the arc is broken.

## Key Structural Concepts

### Directional Movement
Each section depends on the previous one and pushes forward.
- Wrong: three parallel facts with no progression.
- Right: each section creates the problem the next one solves.

### Earned Solutions
Establish, deepen, and clarify the problem fully before presenting the fix. Write the problem section first. Ask: "Have I shown why this is hard?" Only then introduce the solution.

### Signaled Level Shifts
Transitions between modes (story → theory, theory → product, problem → solution) must be explicitly signaled. Use: "This is why," "Here's how that translates," "In practice, this means."

### Introduced Abstractions
Every new concept must be set up. Readers need to know why it matters before being asked to understand it. Establish the problem a concept solves before explaining the concept.

### Continuous Context
Thread drops break orientation. After each paragraph, check: does the next connect? If a paragraph could be removed without affecting flow — that's a context break.

## Writing Process

1. **Clarify audience and purpose.**
2. **State thesis in one sentence.**
3. **Build outline with one job per section.**
4. **Start sections with proof, artifact, conflict, or example.** Explain after, not before.
5. **Cut anything templated, overexplained, or self-congratulatory.**

## Sentence-Level Rules

- **No filler:** Cut "It's important to note that", "In order to", "Simply", "Just", "Basically"
- **No speculation:** Replace "seems", "appears", "might" with what you observed or tested
- **No vague adjectives:** Replace "powerful", "robust", "seamless" with specifics
- **Annotate code:** Every non-obvious line gets a comment. No `hello-world` examples — use real filenames, ports, environments.
- **Active voice:** "Call the function" not "The function is called"
- **Parallel structure:** When comparing alternatives, use same verb form and sentence length.

## Anti-Patterns

| Pattern | Fix |
|---------|-----|
| "In this tutorial, we will..." | Start doing. Cut preamble. |
| "Simply" / "Just" / "Easily" | Remove — condescending to anyone struggling |
| Solutions before earned problem | Build problem fully first |
| Sections reorderable without loss | Rebuild so each depends on the last |
| Conclusions that summarize | Conclusions that extend |
| Wall-of-text code blocks | Annotate every non-obvious line |
| `hello-world` examples | Real filenames, ports, environment context |

## Application Checklist

Before delivering:
- [ ] One clear thesis stated
- [ ] Every section advances the thesis — no drift
- [ ] Narrative arc complete (problem → adoption)
- [ ] All transitions answer: why here? loop closed? natural next step?
- [ ] Opening leads with authority
- [ ] Code examples runnable and realistic
- [ ] No filler phrases remain
- [ ] The ending lands on insight, not summary
