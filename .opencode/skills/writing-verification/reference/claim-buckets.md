# Five-Bucket Claim Taxonomy

Classification system for technical claims in written documents. Every atomic claim gets exactly one bucket.

## Buckets

### 1. simplified-correct

The claim omits detail for readability but remains factually sound. The simplification does not mislead.

**Example**: "TCP guarantees delivery" — omits edge cases (network partition, timeout) but is correct for the audience's purposes.

**Action**: Keep. No change needed.

### 2. simplified-boundary

The claim holds in the common case but breaks at a specific, identifiable boundary. The boundary case may be worth mentioning as a teaching opportunity.

**Example**: "Hash tables have O(1) lookup" — true amortized/average, breaks with pathological hash collisions.

**Action**: Consider folding the boundary into the text as enrichment ("...in the average case; pathological inputs degrade to O(n)"). Not a blocker.

### 3. wrong

The claim is factually incorrect. Not a simplification — it would mislead a reader who acts on it.

**Example**: "RSA encryption is quantum-resistant" — flatly wrong; Shor's algorithm breaks RSA.

**Action**: **BLOCKER.** Must fix before publication. No exceptions.

### 4. contested

The field actively debates this. Asserting it as settled misrepresents the state of knowledge.

**Example**: "Scaling laws guarantee continued LLM capability gains" — actively debated; not settled science.

**Action**: Add hedge language acknowledging the debate, or present both sides. Not a blocker, but must be flagged.

### 5. overclaim

The claim is true in a narrow context but is stated as if it applies broadly.

**Example**: "Rust eliminates memory bugs" — true for memory safety bugs Rust targets, but not for logic errors, unsafe blocks, or FFI.

**Action**: Scope the claim. Add qualifiers. Not a blocker, but should be fixed.

## Classification Rules

1. Default to `simplified-correct` unless there's a specific, identifiable problem
2. `simplified-boundary` requires you to name the boundary condition
3. `wrong` requires you to state what is actually true
4. `contested` requires you to identify both sides of the debate
5. `overclaim` requires you to state the correct, narrower scope
6. When in doubt between `simplified-boundary` and `wrong`: if a practitioner would not be misled in practice, it's `simplified-boundary`
