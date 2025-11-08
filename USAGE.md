# ClearCraft Usage Examples

Comprehensive guide to using ClearCraft for text clarity enhancement.

---

## Table of Contents

1. [Command Line Interface](#command-line-interface)
2. [REST API](#rest-api)
3. [Python API](#python-api)
4. [Web Interface](#web-interface)
5. [Advanced Examples](#advanced-examples)

---

## Command Line Interface

### Analyze Text

#### Analyze from String
```bash
clearcraft analyze --text "The methodology was utilized by researchers to facilitate the implementation of sophisticated paradigms."
```

Output:
```
Readability Metrics
┌─────────────────────┬────────┬────────────────┐
│ Metric              │ Value  │ Interpretation │
├─────────────────────┼────────┼────────────────┤
│ Flesch Reading Ease │ 28.5   │ Difficult      │
│ Flesch-Kincaid Grade│ 16.2   │ Grade 16 level │
│ Gunning Fog Index   │ 18.4   │ 18 years edu   │
│ Avg Sentence Length │ 15.0   │ Good           │
│ Type-Token Ratio    │ 0.933  │ Good variety   │
│ Passive Voice Ratio │ 33.3%  │ High           │
│ Repetition Ratio    │ 0.0%   │ Good           │
└─────────────────────┴────────┴────────────────┘

Total words: 15
Unique words: 14
Sentences: 1
```

#### Analyze from File
```bash
clearcraft analyze --file paper.txt
```

### Rewrite Text

#### Basic Rewrite
```bash
clearcraft rewrite \
  --text "The researchers utilized sophisticated methodologies to facilitate implementation." \
  --output improved.txt
```

#### Academic Tone
```bash
clearcraft rewrite \
  --file scientific_paper.txt \
  --output paper_improved.txt \
  --tone academic \
  --min-length 16 \
  --max-length 24
```

#### Conversational Tone
```bash
clearcraft rewrite \
  --file blog_post.txt \
  --output blog_improved.txt \
  --tone conversational \
  --min-length 12 \
  --max-length 20
```

#### With LLM Polish (Premium)
```bash
# Requires DEEPINFRA_API_TOKEN in .env
clearcraft rewrite \
  --file document.txt \
  --output polished.txt \
  --llm \
  --tone neutral
```

#### Without Disclosure Message
```bash
clearcraft rewrite \
  --text "Your text here" \
  --no-disclosure
```

---

## REST API

### Analyze Endpoint

#### Request
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding."
  }'
```

#### Response
```json
{
  "metrics": {
    "flesch_reading_ease": 12.3,
    "flesch_kincaid_grade": 18.2,
    "gunning_fog": 20.1,
    "smog_index": 15.8,
    "sentence_count": 1,
    "avg_sentence_length": 10.0,
    "avg_word_length": 7.2,
    "mtld": null,
    "ttr": 1.0,
    "unique_words": 10,
    "total_words": 10,
    "passive_ratio": 0.0,
    "repetition_ratio": 0.0
  },
  "warnings": [
    "Average sentence length is within recommended range."
  ]
}
```

### Rewrite Endpoint

#### Request
```bash
curl -X POST http://localhost:8000/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The report was written by the team. The methodology was utilized to facilitate analysis.",
    "tone": "neutral",
    "target_sentence_length_min": 14,
    "target_sentence_length_max": 22,
    "max_change_ratio": 0.30,
    "similarity_min": 0.92,
    "enable_llm": false,
    "enable_disclosure": true
  }'
```

#### Response
```json
{
  "original_text": "The report was written by the team. The methodology was utilized to facilitate analysis.",
  "rewritten_text": "The team wrote the report. They used the method to help with analysis.\n\n---\n*Edited with AI assistance.*",
  "original_metrics": {
    "flesch_reading_ease": 45.2,
    "avg_sentence_length": 11.0,
    "passive_ratio": 0.5,
    "repetition_ratio": 0.0
  },
  "rewritten_metrics": {
    "flesch_reading_ease": 72.3,
    "avg_sentence_length": 9.0,
    "passive_ratio": 0.0,
    "repetition_ratio": 0.0
  },
  "changes": [
    {
      "pass_name": "voice_active",
      "tokens_changed": 4,
      "confidence": 0.75,
      "reason": "passive_by_agent",
      "similarity_score": 0.95
    }
  ],
  "overall_similarity": 0.94,
  "total_change_ratio": 0.18,
  "disclosure_added": true
}
```

### Health Check

```bash
curl http://localhost:8000/healthz
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## Python API

### Basic Analysis

```python
from clearcraft.analysis import TextAnalyzer

# Create analyzer
analyzer = TextAnalyzer()

# Analyze text
text = """
The implementation of sophisticated methodologies facilitates
the optimization of complex paradigms. Researchers utilize
these frameworks to enhance outcomes.
"""

result = analyzer.analyze(text)

# Access metrics
print(f"Flesch Reading Ease: {result.metrics.flesch_reading_ease:.1f}")
print(f"Grade Level: {result.metrics.flesch_kincaid_grade:.1f}")
print(f"Passive Voice: {result.metrics.passive_ratio:.1%}")
print(f"Avg Sentence Length: {result.metrics.avg_sentence_length:.1f}")

# Get passive sentences
for idx in result.passive_sentences:
    print(f"Passive: {result.sentences[idx]}")

# Get repetitive phrases
for phrase, count in result.repetitive_phrases.items():
    print(f"Repeated {count}x: {phrase}")
```

### Basic Rewriting

```python
from clearcraft.selector import TextSelector

# Create selector
selector = TextSelector(
    target_avg_sentence_length=(14, 22),
    max_change_ratio=0.30,
    similarity_min=0.92,
    enable_llm=False,
)

# Rewrite text
text = "The methodology was utilized to facilitate implementation."

result = selector.rewrite(
    text=text,
    tone="neutral",
    enable_disclosure=True,
)

# Access results
print("Original:", result.original_text)
print("Rewritten:", result.rewritten_text)
print(f"Similarity: {result.overall_similarity:.1%}")
print(f"Changes: {result.total_change_ratio:.1%}")

# View change operations
for op in result.change_operations:
    print(f"- {op.pass_name}: {op.reason} (confidence: {op.confidence:.0%})")
```

### With LLM Enhancement

```python
from clearcraft.selector import TextSelector

# Ensure DEEPINFRA_API_TOKEN is set in environment

selector = TextSelector(
    target_avg_sentence_length=(14, 22),
    enable_llm=True,  # Enable DeepInfra LLM
)

result = selector.rewrite(
    text="Your complex text here...",
    tone="conversational",
)

print(result.rewritten_text)
```

### Custom Configuration

```python
from clearcraft.selector import TextSelector
from clearcraft.config import Settings

# Create custom settings
settings = Settings(
    target_avg_sentence_length_min=16,
    target_avg_sentence_length_max=24,
    max_change_ratio=0.25,
    similarity_min=0.95,
    max_passive_ratio=0.10,
)

# Create selector with custom settings
selector = TextSelector(
    target_avg_sentence_length=(
        settings.target_avg_sentence_length_min,
        settings.target_avg_sentence_length_max,
    ),
    max_change_ratio=settings.max_change_ratio,
    similarity_min=settings.similarity_min,
)

result = selector.rewrite(text="Your text here")
```

### Similarity Checking

```python
from clearcraft.similarity import SimilarityChecker

checker = SimilarityChecker()

original = "The quick brown fox jumps over the lazy dog."
rewritten = "A fast brown fox leaps over a lazy dog."

# Check similarity
similarity = checker.compute_similarity(original, rewritten)
print(f"Similarity: {similarity:.1%}")

# Check against threshold
meets_threshold, score = checker.check_threshold(
    original,
    rewritten,
    threshold=0.92,
)

if meets_threshold:
    print(f"✓ Meets threshold: {score:.1%}")
else:
    print(f"✗ Below threshold: {score:.1%}")
```

---

## Web Interface

### Starting the Server

```bash
# Default (localhost:8000)
clearcraft server

# Custom host/port
clearcraft server --host 0.0.0.0 --port 8080

# Development mode (auto-reload)
clearcraft server --reload
```

### Using the Web UI

1. **Navigate** to `http://localhost:8000`
2. **Choose tab**:
   - **Analyze**: Get readability metrics
   - **Rewrite**: Improve text clarity
3. **Paste text** into the editor
4. **Configure options**:
   - Tone (neutral/academic/conversational)
   - Target sentence length
   - LLM enhancement (if API key configured)
   - Disclosure message
5. **Click button** to analyze or rewrite
6. **Review results**:
   - Metrics comparison
   - Rewritten text
   - Download button

---

## Advanced Examples

### Batch Processing

```python
from pathlib import Path
from clearcraft.selector import TextSelector

selector = TextSelector()

# Process multiple files
input_dir = Path("documents")
output_dir = Path("improved")
output_dir.mkdir(exist_ok=True)

for file in input_dir.glob("*.txt"):
    text = file.read_text()
    result = selector.rewrite(text)

    output_file = output_dir / file.name
    output_file.write_text(result.rewritten_text)

    print(f"✓ {file.name}: {result.overall_similarity:.1%} similarity")
```

### Custom Rewriter Pipeline

```python
from clearcraft.rewriters import (
    SyntaxSplitter,
    VoiceActivator,
    JargonSimplifier,
)

# Create custom pipeline
splitter = SyntaxSplitter(max_length=25)
voice_activator = VoiceActivator()
jargon_simplifier = JargonSimplifier()

text = "The methodology was utilized to facilitate implementation."

# Apply passes manually
text, split_ops = splitter.process(text)
text, voice_ops = voice_activator.process(text)
text, jargon_ops = jargon_simplifier.process(text)

print(f"Final: {text}")
print(f"Operations: {len(split_ops + voice_ops + jargon_ops)}")
```

### Metrics Tracking

```python
from clearcraft.analysis import TextAnalyzer

analyzer = TextAnalyzer()

documents = [
    "Document 1 text...",
    "Document 2 text...",
    "Document 3 text...",
]

metrics_history = []

for doc in documents:
    result = analyzer.analyze(doc)
    metrics_history.append({
        "flesch": result.metrics.flesch_reading_ease,
        "grade": result.metrics.flesch_kincaid_grade,
        "passive": result.metrics.passive_ratio,
    })

# Analyze trends
import statistics

avg_flesch = statistics.mean(m["flesch"] for m in metrics_history)
avg_passive = statistics.mean(m["passive"] for m in metrics_history)

print(f"Average Flesch: {avg_flesch:.1f}")
print(f"Average Passive: {avg_passive:.1%}")
```

---

## Environment Variables Reference

```bash
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# DeepInfra (Optional)
DEEPINFRA_API_TOKEN=your_token
DEEPINFRA_MODEL=meta-llama/Llama-4-Maverick-17B

# Processing
MAX_TEXT_LENGTH=50000
CHUNK_SIZE=1000

# Quality Guardrails
MAX_CHANGE_RATIO=0.30
SIMILARITY_MIN=0.92
PRESERVE_CITATIONS=true

# Readability Targets
TARGET_AVG_SENTENCE_LENGTH_MIN=14
TARGET_AVG_SENTENCE_LENGTH_MAX=22
MAX_PASSIVE_RATIO=0.15
MAX_REPETITION_RATIO=0.10

# Models
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
SPACY_MODEL=en_core_web_sm

# Privacy
ENABLE_DISCLOSURE=true
REDACT_PII_IN_LOGS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=clearcraft.log
```

---

## Troubleshooting

### Installation Issues

```bash
# If sentence-transformers fails to install
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers

# If spaCy model download fails
python -m spacy download en_core_web_sm --user
```

### Runtime Issues

```bash
# Check installation
clearcraft version

# Test configuration
python -c "from clearcraft.config import settings; print(settings)"

# Verify DeepInfra connection (if configured)
python -c "from clearcraft.adapters.deepinfra_llm import DeepInfraAdapter; adapter = DeepInfraAdapter(); print(adapter.test_connection())"
```

---

## Best Practices

1. **Start with analysis**: Always analyze first to understand baseline metrics
2. **Iterative improvement**: Make incremental changes rather than aggressive rewrites
3. **Preserve context**: Use appropriate chunk sizes for long documents
4. **Monitor similarity**: Keep similarity > 0.92 to ensure meaning preservation
5. **Test on samples**: Try different tones and settings on representative samples
6. **Review output**: Always review machine-edited text before publication
7. **Use disclosure**: Add the disclosure message for transparency

---

For more information, see [README.md](README.md).
