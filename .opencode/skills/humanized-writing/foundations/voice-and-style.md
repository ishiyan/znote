# Voice and Style

Merged from: beautiful-prose, human-writing, writing-style.

## Registers

Choose one register per piece. Default to `literary_modern` if unspecified.

| Register | Character |
|----------|-----------|
| **literary_modern** | Vivid, lean imagery. Controlled heat, sharp observation. Minimal ornament. |
| **founding_fathers** | Formal, spare, civic gravity. Balanced syntax without decoration. |
| **cold_steel** | Severe compression. Punchy, unsentimental. High signal, low warmth. |
| **journalistic** | Crisp, factual, narrative clarity. Clean momentum. No clickbait cadence. |
| **operator** | Concrete, unsentimental, useful. The default for technical/business writing. |

## Absolute Prohibitions

Treat violations as failures, not suggestions.

### 1. Em dashes
Ban `—` used as parenthetical or pivot. Use periods, commas, colons, semicolons, or line breaks instead. One or two per document maximum.

### 2. Correlative constructions
Kill the pattern and all variants:
- "It's not X — it's Y"
- "This isn't about X. It's about Y."
- "Not just X, but Y"

**Fix:** State the stronger claim directly. "It absorbs the rhythm." Not "It doesn't just understand — it absorbs the rhythm."

### 3. Filler transitions
Ban: "At its core", "In today's world", "That said", "Let's explore", "Ultimately", "What this means is", "It's important to note", "On the one hand", "When it comes to", "In order to" (→ "To"), "Without further ado"

### 4. Therapeutic/validating language
No: "I hear you", "That sounds hard", "Give yourself grace", "You're valid"

### 5. Meta commentary
No: "In this essay", "This piece explores", "We will discuss", "Here are the key takeaways"

### 6. Symmetry padding
No balancing sentences for the sake of balance. No three-part lists unless earned. No "X, Y, and Z" as decoration.

## Sentence Craft

- Prefer declarative sentences.
- Vary length aggressively. Short sentences as impact. Long when building.
- Prefer concrete nouns over abstractions.
- Prefer strong verbs over adverbs.
- Prefer Anglo-Saxon weight; use Latinate precision only when it buys accuracy.
- Keep related words together.
- Place emphatic words at the end.
- Beginning participial phrase must refer to the grammatical subject.

## Human Markers

These signal a real person wrote it:

- **Specificity** — Real names, numbers, places. Not "many people" but "twelve developers at a Tuesday standup."
- **Opinion** — State your take. "Honestly, most voice matching tools overcomplicate this."
- **Limitation** — Admit what you don't know. "This approach fails for highly technical content."
- **Rhythm variation** — Fragments. One-word paragraphs. Sentences under 5 words for punch. Start with "And" or "But." Parenthetical asides.
- **Contractions** — Always. "don't", "won't", "it's", "they're". Uncontracted forms are a tell.
- **Mess** — Conjunction starters, mid-sentence parentheticals, sentence fragments. These signal drafting, not generating.

## Word Replacements

| Kill | Use instead |
|------|-------------|
| delve, dive into | look at, examine |
| comprehensive, robust | thorough, complete |
| utilize | use |
| leverage (verb) | use, apply |
| crucial, vital, essential | important, key |
| unlock, unleash, supercharge | enable, improve |
| game-changer, revolutionary | significant, notable |
| landscape, navigate | environment, work through |
| tapestry, multifaceted, myriad | varied, many, diverse |
| foster, facilitate, enhance | support, help, improve |
| realm, paradigm, synergy | area, approach, combination |
| embark, journey (for processes) | start, begin, process |
| serves as, stands as, boasts | is, has |

## Lint Checklist (pass/fail gate)

Fail the output if any are true:
- [ ] Contains em dashes used as parentheticals (more than 2 in document)
- [ ] Contains a correlative pivot pattern ("not X, Y")
- [ ] Contains filler transitions from the banned list
- [ ] Contains therapeutic or validating language
- [ ] Contains meta writing talk ("this essay," "we will")
- [ ] Contains 5+ consecutive sentences of similar length
- [ ] Contains vocabulary from the kill-on-sight list
- [ ] Any sentence sounds like a press release or chatbot response

## Authority

- Write as if truth does not need permission.
- Avoid hedging unless uncertainty is essential and explicit.
- Do not posture. Do not moralize.
- Open with substance, not a hook.
- Close cleanly without summary. Do not restate the thesis.
