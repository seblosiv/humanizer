# ClearCraft ✨

**Production-grade text clarity and readability enhancement tool with ethical guardrails.**

ClearCraft is a Python web application designed to improve text clarity, readability, and flow while preserving meaning, citations, and formatting. It employs deterministic text processing combined with optional LLM-based polishing, all under strict semantic similarity and change ratio constraints.

---

## 🎯 Purpose

ClearCraft **improves readability and clarity** for legitimate writing enhancement. It is **NOT** designed to:
- Bypass AI detectors
- Evade detection systems
- Remove watermarks
- Misrepresent authorship

All improvements focus on genuine clarity, coherence, and authentic human tone.

---

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Usage Examples](USAGE.md)** - Comprehensive CLI, API, and Python examples
- **[Research Methods](METHODS.md)** - Scientific basis with formulas and citations
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment for all platforms
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete project overview
- **[Changelog](CHANGELOG.md)** - Version history and release notes
- **[API Documentation](http://localhost:8000/docs)** - Interactive API reference (when server running)

---

## ✨ Features

### Core Capabilities
- **Readability Analysis**: Flesch-Kincaid, Gunning Fog, SMOG, MTLD, TTR, passive voice detection
- **Deterministic Rewriters**: Syntax optimization, voice activation, jargon simplification, repetition trimming
- **Semantic Guardrails**: Enforces minimum similarity (default 92%) and maximum change ratio (default 30%)
- **Citation Preservation**: Maintains references, links, code blocks, and formatting
- **Optional LLM Polish**: DeepInfra integration for premium editorial quality (off by default)

### Interface Options
- **Web UI**: Modern HTMX + Tailwind CSS interface with real-time analysis
- **REST API**: FastAPI backend with comprehensive endpoints
- **CLI**: Rich command-line interface with Typer

---

## 🏗️ Architecture

```
clearcraft/
├── clearcraft/              # Core package
│   ├── analysis.py         # Readability metrics (Flesch, MTLD, TTR, etc.)
│   ├── chunking.py         # Markdown/HTML-aware text segmentation
│   ├── similarity.py       # Sentence-transformers semantic similarity
│   ├── selector.py         # Orchestrator with guardrails
│   ├── rewriters/          # Deterministic transformation modules
│   │   ├── syntax_split.py
│   │   ├── syntax_merge.py
│   │   ├── voice_active.py
│   │   ├── jargon_plain.py
│   │   ├── repetition_trim.py
│   │   ├── grammar.py
│   │   └── formatting.py
│   ├── adapters/           # External integrations
│   │   └── deepinfra_llm.py  # DeepInfra LLM adapter (optional)
│   ├── server.py           # FastAPI application
│   └── cli.py              # Typer CLI
├── rules/                  # YAML lexicons
│   ├── jargon_en.yaml
│   └── fillers_en.yaml
├── templates/              # HTMX frontend
├── tests/                  # Comprehensive test suite
└── static/                 # CSS/JS assets
```

---

## 📊 Metrics & Algorithms (2025 Best Practices)

### Readability Scores
- **Flesch Reading Ease**: 0-100 scale; higher = easier
- **Flesch-Kincaid Grade Level**: U.S. grade level required
- **Gunning Fog Index**: Years of formal education needed
- **SMOG Index**: Simple Measure of Gobbledygook

### Lexical Diversity
- **MTLD (Measure of Textual Lexical Diversity)**: Sequential TTR method, threshold 0.72
- **Type-Token Ratio (TTR)**: Unique words / total words

### Style Metrics
- **Passive Voice Ratio**: Detected via dependency parsing patterns
- **Repetition Ratio**: N-gram (bigram/trigram) frequency analysis
- **Average Sentence Length**: Target range 14-22 tokens (configurable)

### Quality Guardrails
- **Semantic Similarity**: Sentence-transformers (`all-MiniLM-L6-v2`) with cosine similarity
- **Change Ratio**: Word-level diff metric
- **NER Preservation**: Ensures named entities remain intact (basic implementation)

---

## 🚀 Installation

### Requirements
- Python 3.10+
- 4GB RAM minimum (8GB recommended for LLM mode)

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourorg/clearcraft.git
cd clearcraft

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# (Optional) Configure DeepInfra
cp .env.sample .env
# Edit .env and add your DEEPINFRA_API_TOKEN
```

---

## 💻 Usage

### Web Interface

```bash
# Start the web server
clearcraft server

# Or with custom settings
clearcraft server --host 0.0.0.0 --port 8080 --reload
```

Visit `http://localhost:8000` in your browser.

### Command Line

#### Analyze Text
```bash
# From string
clearcraft analyze --text "Your text here"

# From file
clearcraft analyze --file document.txt
```

#### Rewrite Text
```bash
# Basic rewrite
clearcraft rewrite --file input.txt --output output.txt

# With options
clearcraft rewrite \
  --file input.txt \
  --output output.txt \
  --tone academic \
  --min-length 16 \
  --max-length 24 \
  --llm  # Enable LLM polish (requires API key)
```

### REST API

```bash
# Analyze text
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'

# Rewrite text
curl -X POST http://localhost:8000/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "tone": "neutral",
    "target_sentence_length_min": 14,
    "target_sentence_length_max": 22,
    "enable_llm": false,
    "enable_disclosure": true
  }'
```

### Python API

```python
from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector

# Analyze text
analyzer = TextAnalyzer()
result = analyzer.analyze("Your text here")
print(f"Flesch Score: {result.metrics.flesch_reading_ease}")

# Rewrite text
selector = TextSelector(
    target_avg_sentence_length=(14, 22),
    enable_llm=False,
)
result = selector.rewrite(
    text="Your text here",
    tone="neutral",
)
print(result.rewritten_text)
```

---

## 🔧 Configuration

All settings can be configured via environment variables or `.env` file:

```bash
# Core Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# DeepInfra (Optional)
DEEPINFRA_API_TOKEN=your_token_here
DEEPINFRA_MODEL=meta-llama/Llama-4-Maverick-17B

# Quality Guardrails
MAX_CHANGE_RATIO=0.30
SIMILARITY_MIN=0.92
PRESERVE_CITATIONS=true

# Readability Targets
TARGET_AVG_SENTENCE_LENGTH_MIN=14
TARGET_AVG_SENTENCE_LENGTH_MAX=22
MAX_PASSIVE_RATIO=0.15
MAX_REPETITION_RATIO=0.10
```

---

## 🤖 DeepInfra Integration (Optional)

ClearCraft supports optional LLM-based polishing via [DeepInfra](https://deepinfra.com)'s OpenAI-compatible API.

### Supported Models (2025)
- **Llama 4**: `meta-llama/Llama-4-Maverick-17B` (default)
- **Claude**: `anthropic/claude-3-7-sonnet`, `anthropic/claude-4-opus`
- **Qwen**: `Qwen/Qwen3-235B-Instruct`, `Qwen/Qwen3-30B-Instruct`
- **DeepSeek**: `microsoft/deepseek-v2`

### Setup
1. Get API key from [deepinfra.com](https://deepinfra.com)
2. Set `DEEPINFRA_API_TOKEN` in `.env`
3. Enable LLM mode in UI or via `--llm` flag in CLI

### Safety Features
- **Hard-fail on disallowed intents**: Blocks "bypass", "evade", "undetectable" keywords
- **Change ratio enforcement**: Max 30% changes by default
- **Similarity checking**: Ensures meaning preservation
- **Prompt transparency**: Non-evasive system prompts

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=clearcraft --cov-report=html

# Specific test file
pytest tests/test_analysis.py -v
```

---

## 📚 Research References

This tool is based on current (2025) best practices in text simplification and readability:

1. **EASSE (Easier Automatic Sentence Simplification Evaluation)**
   - Alva-Manchego et al., 2019
   - Standard framework for text simplification evaluation
   - https://github.com/feralvam/easse

2. **ReadCtrl: Readability-Controlled Instruction Learning**
   - 2024 research on controllable text generation with readability targets
   - Achieved 52.1% win rate vs GPT-4 in human evaluations
   - https://arxiv.org/abs/2406.09205

3. **Measure of Textual Lexical Diversity (MTLD)**
   - McCarthy & Jarvis, 2010
   - Sequential TTR method, threshold 0.72
   - More stable than traditional TTR for varying text lengths

4. **Sentence-Transformers for Semantic Similarity**
   - Reimers & Gurevych, 2019
   - Fast, accurate semantic similarity via embeddings
   - Using `all-MiniLM-L6-v2` model (384 dimensions)

5. **Readability Formulas**
   - Flesch Reading Ease (1948)
   - Flesch-Kincaid Grade Level (1975)
   - Gunning Fog Index (1952)
   - SMOG Index (1969)

6. **Controllable Text Generation Survey**
   - 2024 survey on controlling LLM outputs for specific attributes
   - https://arxiv.org/abs/2408.12599

---

## 🛡️ Ethics & Compliance

### What ClearCraft Does
✅ Improves clarity and readability
✅ Simplifies complex language
✅ Reduces passive voice and repetition
✅ Preserves citations and meaning
✅ Adds optional disclosure

### What ClearCraft Does NOT Do
❌ Attempt to bypass AI detectors
❌ Remove watermarks or signatures
❌ Alter facts or add false information
❌ Enable plagiarism or misrepresentation
❌ Process text with evasive intent

### Disclosure
When enabled (default), ClearCraft appends:
```
---
*Edited with AI assistance.*
```

---

## 🔄 CI/CD

```bash
# Lint with ruff
ruff check clearcraft/

# Type check with mypy
mypy clearcraft/

# Format code
ruff format clearcraft/
```

---

## 📈 Performance

- **Throughput**: Handles 50k character documents via chunking
- **Latency**: <1s for analysis (local), 2-5s for rewrite (local), +3-10s with LLM
- **Memory**: ~500MB baseline, +1-2GB with sentence transformers loaded

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `ruff` and `mypy` pass
5. Submit a pull request

---

## 📄 License

MIT License - see `LICENSE` file.

---

## 🙏 Acknowledgments

- EASSE framework for simplification evaluation
- Sentence-Transformers for semantic similarity
- DeepInfra for LLM infrastructure
- Open-source NLP community

---

## 📞 Support

- **Issues**: https://github.com/yourorg/clearcraft/issues
- **Discussions**: https://github.com/yourorg/clearcraft/discussions
- **Email**: support@clearcraft.example

---

**Note**: This tool is designed for ethical text improvement. Misuse for bypassing detection systems violates the intended purpose and terms of use.
