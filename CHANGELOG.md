# Changelog

All notable changes to ClearCraft will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-01-08

### 🎉 Initial Release

First production release of ClearCraft - ethical text clarity enhancement tool.

### Added

#### Core Features
- **Text Analysis Engine**
  - Flesch Reading Ease and Flesch-Kincaid Grade Level
  - Gunning Fog Index and SMOG Index
  - MTLD (Measure of Textual Lexical Diversity)
  - Type-Token Ratio (TTR)
  - Passive voice detection with pattern matching
  - Repetition analysis (bigrams and trigrams)
  - Sentence statistics and complex word counting

- **Deterministic Rewriters** (7 modules)
  - `syntax_split.py` - Split long sentences at safe boundaries
  - `syntax_merge.py` - Merge ultra-short sentences for flow
  - `voice_active.py` - Convert passive to active voice
  - `jargon_plain.py` - Simplify technical jargon
  - `repetition_trim.py` - Remove fillers and vary openings
  - `grammar.py` - Apply whitelisted grammar corrections
  - `formatting.py` - Normalize quotes, dashes, spacing

- **Quality Guardrails**
  - Semantic similarity checking (default 92% minimum)
  - Change ratio cap (default 30% maximum)
  - Citation preservation (links, code, footnotes)
  - Disallowed intent detection
  - Optional disclosure message

- **DeepInfra LLM Integration** (Optional)
  - OpenAI-compatible API adapter
  - Support for Llama 4, Claude 3.7/4, Qwen3, DeepSeek
  - Non-evasive system prompts
  - Safety checks for disallowed keywords
  - Change ratio and similarity enforcement

#### Interfaces
- **Web UI** (HTMX + Tailwind CSS)
  - Dual-tab interface (Analyze / Rewrite)
  - Real-time metrics display
  - Side-by-side comparison
  - Download functionality
  - Responsive mobile design

- **REST API** (FastAPI)
  - `POST /api/analyze` - Text analysis endpoint
  - `POST /api/rewrite` - Text rewriting endpoint
  - `GET /healthz` - Health check endpoint
  - `GET /docs` - API documentation page
  - OpenAPI schema at `/docs` (FastAPI auto-docs)

- **CLI** (Typer + Rich)
  - `clearcraft analyze` - Analyze text files or strings
  - `clearcraft rewrite` - Rewrite with configurable options
  - `clearcraft server` - Start web server
  - `clearcraft version` - Show version info
  - Rich terminal output with tables and colors

- **Python API**
  - Programmatic access to all features
  - Type-hinted interfaces
  - Pydantic models for validation

#### Documentation
- **README.md** - Comprehensive main documentation with research references
- **USAGE.md** - Detailed examples for CLI, API, and Python usage
- **METHODS.md** - Scientific basis with formulas and citations (2025 best practices)
- **CONTRIBUTING.md** - Contribution guidelines with code standards
- **API Documentation** - Interactive web-based API reference

#### Deployment
- **Docker Support**
  - Production-ready Dockerfile with security hardening
  - docker-compose.yml with volume management
  - Health checks and auto-restart
  - Non-root user (clearcraft)
  - Model caching optimization

- **Setup Automation**
  - `setup.sh` - Automated installation script
  - Environment validation
  - Dependency installation
  - spaCy model download
  - Configuration setup

#### Examples & Demos
- **Interactive Demo** (`examples/demo.py`)
  - 5 comprehensive demonstrations
  - Real-time metrics display
  - Before/after comparisons
- **Sample Texts**
  - Complex academic text for testing
  - Multiple use case examples

#### Monitoring & Health
- **Health Monitor** (`clearcraft/monitoring.py`)
  - System resource monitoring (CPU, memory, disk)
  - Model availability checks
  - Uptime tracking
  - Comprehensive health reports

#### Testing
- **Pytest Suite**
  - Unit tests for all modules
  - Integration tests for pipelines
  - Golden tests for known outputs
  - API endpoint tests
  - Coverage reporting

#### CI/CD
- **GitHub Actions**
  - Automated testing on Python 3.10, 3.11, 3.12
  - Ruff linting
  - MyPy type checking
  - Codecov integration

#### Configuration
- **Environment Variables**
  - Comprehensive `.env.sample` template
  - Pydantic-based validation
  - Runtime configuration without code changes
- **YAML Lexicons**
  - 50+ jargon mappings (`rules/jargon_en.yaml`)
  - Stock filler phrases (`rules/fillers_en.yaml`)
  - Discourse marker alternatives

### Research Foundation
- Based on EASSE framework (Alva-Manchego et al., 2019)
- ReadCtrl readability-controlled instruction learning (2024)
- MTLD lexical diversity (McCarthy & Jarvis, 2010)
- Sentence-BERT semantic similarity (Reimers & Gurevych, 2019)
- Standard readability formulas (Flesch 1948, Gunning 1952, SMOG 1969)

### Security
- MIT License with ethical use restrictions
- Input validation and sanitization
- PII redaction in logs (configurable)
- API key protection
- Hard-fail on disallowed intents

### Performance
- Handles 50K character documents via chunking
- <1s analysis latency (local processing)
- 2-5s deterministic rewrite latency
- +3-10s with optional LLM mode
- ~500MB baseline memory usage

### Dependencies
- Python 3.10+ required
- FastAPI 0.109.0+
- sentence-transformers 2.3.0+
- spaCy 3.7.0+
- textstat 0.7.3+
- See `requirements.txt` for complete list

---

## [Unreleased]

### Planned Features
- [ ] Multilingual support (German, Spanish, French)
- [ ] Enhanced NER preservation with spaCy integration
- [ ] SBERT fine-tuning for domain-specific similarity
- [ ] Batch processing API endpoint
- [ ] Export to multiple formats (DOCX, PDF, HTML)
- [ ] Real-time streaming for large documents
- [ ] User preference profiles
- [ ] A/B testing framework for rewriter evaluation

### Under Consideration
- [ ] Web browser extension
- [ ] VS Code extension
- [ ] Jupyter notebook integration
- [ ] Custom model training interface
- [ ] Analytics dashboard
- [ ] Rate limiting and API authentication

---

## Version History

### Versioning Scheme
- **Major.Minor.Patch** (Semantic Versioning)
- **Major**: Breaking API changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

### Release Notes
Each release includes:
- Feature additions
- Bug fixes
- Performance improvements
- Breaking changes (if any)
- Migration guides (for breaking changes)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on proposing changes.

---

## Links

- **Repository**: https://github.com/yourorg/clearcraft
- **Issues**: https://github.com/yourorg/clearcraft/issues
- **Discussions**: https://github.com/yourorg/clearcraft/discussions
- **Documentation**: See README.md, USAGE.md, METHODS.md

---

[1.0.0]: https://github.com/yourorg/clearcraft/releases/tag/v1.0.0
