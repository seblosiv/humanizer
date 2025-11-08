# ClearCraft: Methods & Research Basis (November 2025)

This document explains the scientific and technical foundation for ClearCraft's approach to text clarity enhancement.

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [Readability Metrics](#readability-metrics)
3. [Lexical Diversity Measures](#lexical-diversity-measures)
4. [Semantic Similarity](#semantic-similarity)
5. [Text Transformation Methods](#text-transformation-methods)
6. [Quality Guardrails](#quality-guardrails)
7. [LLM Integration](#llm-integration)
8. [References](#references)

---

## Core Philosophy

ClearCraft is built on the principle that **clarity enhancement should preserve meaning**. Unlike tools designed to evade detection, ClearCraft focuses on legitimate readability improvements backed by linguistic research.

### Key Principles
1. **Transparency**: All transformations are logged and reversible
2. **Preservation**: Citations, code, and formatting are protected
3. **Measurable**: Every change is quantified via similarity and change ratio metrics
4. **Evidence-based**: Methods are grounded in published research

---

## Readability Metrics

### 1. Flesch Reading Ease (1948)

**Formula:**
```
FRE = 206.835 - 1.015(total words / total sentences) - 84.6(total syllables / total words)
```

**Scale:**
- 90-100: Very Easy (5th grade)
- 60-70: Standard (8th-9th grade)
- 30-50: Difficult (College level)
- 0-30: Very Difficult (Graduate level)

**Reference:** Flesch, R. (1948). *A new readability yardstick*. Journal of Applied Psychology, 32(3), 221.

### 2. Flesch-Kincaid Grade Level (1975)

**Formula:**
```
FKGL = 0.39(total words / total sentences) + 11.8(total syllables / total words) - 15.59
```

**Output:** U.S. grade level required to understand the text.

**Reference:** Kincaid, J. P., et al. (1975). *Derivation of new readability formulas for Navy enlisted personnel*.

### 3. Gunning Fog Index (1952)

**Formula:**
```
Fog = 0.4[(words / sentences) + 100(complex words / words)]
```

Where *complex words* = words with 3+ syllables.

**Reference:** Gunning, R. (1952). *The Technique of Clear Writing*.

### 4. SMOG Index (1969)

**Formula:**
```
SMOG = 1.0430 * sqrt(polysyllables * (30 / sentences)) + 3.1291
```

**Reference:** McLaughlin, G. H. (1969). *SMOG grading: A new readability formula*. Journal of Reading, 12(8), 639-646.

---

## Lexical Diversity Measures

### Type-Token Ratio (TTR)

**Formula:**
```
TTR = unique_words / total_words
```

**Issues:** Sensitive to text length; longer texts tend to have lower TTR.

**Reference:** Johnson, W. (1944). *Studies in language behavior*.

### Measure of Textual Lexical Diversity (MTLD)

**Method:**
MTLD calculates the mean length of sequential word strings that maintain a TTR ≥ 0.72.

**Process:**
1. Move through text sequentially
2. Track running TTR
3. When TTR drops below 0.72, record string length
4. Compute mean of all string lengths
5. Repeat forward and backward, then average

**Advantages:**
- Less sensitive to text length than simple TTR
- More stable across varying document sizes
- Correlates well with human judgments of lexical variety

**Reference:** McCarthy, P. M., & Jarvis, S. (2010). *MTLD, vocd-D, and HD-D: A validation study of sophisticated approaches to lexical diversity assessment*. Behavior Research Methods, 42(2), 381-392.

**ClearCraft Implementation:**
```python
from lexicalrichness import LexicalRichness

if total_words >= 50:
    lex = LexicalRichness(text)
    mtld_value = lex.mtld(threshold=0.72)
```

---

## Semantic Similarity

### Sentence-Transformers Approach

**Model:** `all-MiniLM-L6-v2`
- 384-dimensional embeddings
- Trained on 1B+ sentence pairs
- ~5s to encode 10K sentences (vs 65 hours with BERT)

**Method:**
1. Encode both texts into dense vectors
2. Compute cosine similarity:
   ```
   similarity = (A · B) / (||A|| ||B||)
   ```

**Threshold:** Default 0.92 (92% similarity required)

**Reference:**
- Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019.
- https://www.sbert.net/

**Why Sentence-Transformers?**
- Fast inference (~0.01s vs minutes for full BERT)
- High correlation with human similarity judgments
- Works well for paraphrase detection
- Lightweight deployment (no GPU required)

### Fallback: Jaccard Similarity

When sentence-transformers unavailable:
```
Jaccard(A, B) = |A ∩ B| / |A ∪ B|
```

Used as rough approximation; less accurate than embeddings.

---

## Text Transformation Methods

### 1. Syntax Optimization

**Sentence Splitting:**
- Target: 14-22 tokens per sentence
- Split points: semicolons, coordinating conjunctions, em dashes
- Preserve clause integrity

**Sentence Merging:**
- Merge ultra-short sentences (<5 tokens)
- Check subject/tense continuity
- Use discourse markers for cohesion

**Reference:** Inspired by controllable text simplification research (Nisioi et al., 2017).

### 2. Voice Activation (Passive → Active)

**Detection Patterns:**
```regex
(is|was|are|were) + [PAST_PARTICIPLE] + by + [AGENT]
```

**Transformation:**
```
"The report was written by Alice" → "Alice wrote the report"
```

**Confidence Scoring:**
- 0.80: Clear agent identified
- 0.70: Verb conjugation confident
- 0.60: Complex tense handling

**Reference:** Standard linguistic transformations; validated against voice detection tools.

### 3. Jargon Simplification

**Method:**
1. Load curated YAML lexicon (jargon → plain language)
2. Check word frequency (wordfreq library)
3. Replace only if plain alternative is more common
4. Preserve capitalization

**Example:**
```yaml
utilize:
  replacement: "use"
  pos: "verb"
  context: "general"
```

**Confidence:**
- 0.85: Replacement more frequent in corpus
- 0.75: Similar frequency
- 0.60: Replacement less frequent (skip)

**Reference:** Based on plain language guidelines (PlainLanguage.gov).

### 4. Repetition Trimming

**Detection:**
- Bigrams and trigrams with frequency ≥ 3
- Stock filler phrases ("basically", "actually", etc.)

**Ratio Calculation:**
```
repetition_ratio = (repetitive_tokens - unique_tokens) / total_tokens
```

**Reference:** N-gram analysis standard in computational linguistics.

### 5. Grammar Correction

**Tool:** language-tool-python (LanguageTool wrapper)

**Whitelisted Categories:**
- GRAMMAR
- TYPOS
- PUNCTUATION
- CAPITALIZATION
- CONFUSED_WORDS

**Blacklisted:**
- Style-only rules (subjective)
- Quote preference (straight vs curly)

**Reference:** LanguageTool open-source grammar checker.

### 6. Formatting Normalization

**Transformations:**
- Smart quotes → straight quotes
- Multiple spaces → single space
- Em dash spacing normalization
- Ellipsis standardization (3 dots)

**Rationale:** Consistency improves parsing and readability metrics.

---

## Quality Guardrails

### 1. Semantic Similarity Floor

**Metric:** Cosine similarity of sentence embeddings
**Threshold:** 0.92 (default)
**Action:** Reject output if similarity < threshold

**Rationale:**
- 0.90-0.95 range indicates paraphrase quality
- Below 0.90 suggests meaning drift
- Above 0.95 ensures strong semantic preservation

**Validation:** Tested on paraphrase datasets (MRPC, STS-B).

### 2. Change Ratio Cap

**Metric:** Word-level Levenshtein-style diff
**Formula:**
```
change_ratio = differences / max(len(original), len(rewritten))
```

**Threshold:** 0.30 (30% max changes)

**Rationale:**
- Prevents over-rewriting
- Maintains authorial voice
- Ensures recognizable output

### 3. Citation Preservation

**Protected Elements:**
- Markdown links: `[text](url)`
- Reference links: `[text][ref]`
- Footnotes: `[^1]`
- Academic citations: `(Author, Year)`
- Code blocks: ` ```language ... ``` `

**Implementation:** Protected spans marked during chunking; transformations skip these regions.

---

## LLM Integration

### DeepInfra OpenAI-Compatible API

**Purpose:** Optional final polish for premium quality

**Models Used (2025):**
- Llama 4 Maverick (17B parameters)
- Claude 3.7 Sonnet, Claude 4 Opus
- Qwen3-235B-Instruct
- DeepSeek V2

**Prompt Design:**

**System Prompt:**
```
You are an expert editor focused on improving text clarity, flow, and authentic human tone.

Your role:
- Enhance readability and coherence
- Preserve original meaning exactly
- Maintain all citations, links, and formatting
- Use natural, authentic language

Critical constraints:
- Do NOT attempt to bypass AI detectors
- Do NOT try to make text "undetectable"
- Do NOT alter facts or add information
- Preserve all citations and references exactly
```

**Safety Checks:**
1. **Input screening:** Reject if disallowed keywords present
2. **Output screening:** Verify no evasive language added
3. **Similarity check:** Ensure LLM output meets threshold
4. **Change ratio:** Verify within limits

**Reference:**
- ReadCtrl (2024): Readability-controlled instruction tuning showed 52.1% win rate vs GPT-4
- https://arxiv.org/abs/2406.09205

---

## Evaluation Metrics

### SARI (System output, references, Input)

**Formula:**
```
SARI = (F_add + F_keep + F_del) / 3
```

Where:
- F_add: N-gram precision for additions
- F_keep: N-gram precision for kept words
- F_del: N-gram precision for deletions

**Reference:**
- Xu et al. (2016). *Optimizing Statistical Machine Translation for Text Simplification*. TACL.
- Used via EASSE library: https://github.com/feralvam/easse

**ClearCraft Usage:**
Optional evaluation metric when reference texts provided.

---

## Current Best Practices (2025)

### 1. Controllable Generation

**State-of-the-art:** Instruction tuning with explicit readability targets
- ReadCtrl demonstrated superior performance over GPT-4
- Key: Explicit constraints in prompt + post-hoc verification

**ClearCraft Implementation:**
- Deterministic passes ensure controllability
- LLM mode adds optional polish under strict constraints
- All outputs verified against similarity + change ratio

### 2. Document-Level Simplification

**Challenge:** Maintaining coherence across paragraphs

**Approaches:**
- Anaphora preservation (pronouns, referents)
- Discourse marker tracking
- Chunk-level processing with overlap

**Reference:** CLEF 2025 SimpleText Task addresses document-level simplification.

### 3. Semantic Preservation

**Gold Standard:** Sentence-transformers with cosine similarity

**Alternative Methods:**
- BERT-Score (slower but more accurate)
- BERTSimilarity (contextual embeddings)
- BLEURT (learned metric)

**ClearCraft Choice:** Sentence-transformers for speed + accuracy balance.

---

## Why These Methods?

### Readability Formulas
✅ **Pros:** Fast, interpretable, correlated with human judgments
❌ **Cons:** Don't capture meaning or context
📊 **Validation:** 70+ years of use in education, publishing

### Lexical Diversity (MTLD)
✅ **Pros:** Stable across text lengths, better than simple TTR
❌ **Cons:** Requires 50+ tokens for reliability
📊 **Validation:** Psychometric studies show reliability (Jarvis, 2013)

### Sentence-Transformers
✅ **Pros:** Fast, accurate semantic similarity
❌ **Cons:** Requires ~500MB model download
📊 **Validation:** State-of-the-art on STS benchmarks

### Deterministic Rewriters
✅ **Pros:** Explainable, consistent, fast
❌ **Cons:** Limited to pattern-based transformations
📊 **Validation:** Linguistics-based transformations

### Optional LLM
✅ **Pros:** Handles complex rewording, natural flow
❌ **Cons:** Requires API key, less predictable
📊 **Validation:** ReadCtrl (2024) shows benefits under constraints

---

## Limitations & Future Work

### Current Limitations
1. **English-only:** Metrics and rewriters optimized for English
2. **Pattern-based voice detection:** May miss complex passive constructions
3. **No content generation:** Only rewrites existing content
4. **Computational cost:** Sentence-transformers require ~500MB RAM

### Future Enhancements
1. **Multilingual support:** German, Spanish, French lexicons (in progress)
2. **spaCy integration:** Better NER, dependency parsing for voice detection
3. **SBERT fine-tuning:** Domain-specific similarity models
4. **Caching:** Pre-compute embeddings for common phrases

---

## References

### Readability
- Flesch, R. (1948). A new readability yardstick. *Journal of Applied Psychology*, 32(3), 221.
- Kincaid, J. P., et al. (1975). Derivation of new readability formulas.
- Gunning, R. (1952). *The Technique of Clear Writing*.
- McLaughlin, G. H. (1969). SMOG grading. *Journal of Reading*, 12(8), 639-646.

### Lexical Diversity
- McCarthy, P. M., & Jarvis, S. (2010). MTLD, vocd-D, and HD-D. *Behavior Research Methods*, 42(2), 381-392.
- Jarvis, S. (2013). Capturing the diversity in lexical diversity. *Language Learning*, 63, 87-106.

### Text Simplification
- Alva-Manchego, F., et al. (2019). EASSE: Easier automatic sentence simplification evaluation. *EMNLP*.
- Xu, W., et al. (2016). Optimizing statistical machine translation for text simplification. *TACL*, 4, 401-415.
- Nisioi, S., et al. (2017). Exploring neural text simplification models. *ACL*.

### Semantic Similarity
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT. *EMNLP*.
- Cer, D., et al. (2018). Universal sentence encoder. *arXiv:1803.11175*.

### Controllable Generation
- ReadCtrl (2024). Readability-controlled instruction learning. *arXiv:2406.09205*.
- Zhang, H., et al. (2024). Controllable text generation: A survey. *arXiv:2408.12599*.

### Document-Level Simplification
- CLEF 2025 SimpleText Task: https://simpletext-project.com/

---

## Conclusion

ClearCraft combines established readability metrics with modern NLP techniques to provide transparent, measurable text improvement. By prioritizing semantic preservation and explainability over aggressive transformation, it serves as an ethical alternative to detection-evasion tools.

**Core Innovation:** Orchestrated pipeline of deterministic + optional LLM passes, all constrained by semantic similarity and change ratio guardrails.

For implementation details, see source code in `clearcraft/` directory.
