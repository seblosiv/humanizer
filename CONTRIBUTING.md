# Contributing to ClearCraft

Thank you for your interest in contributing to ClearCraft! We welcome contributions that improve text clarity enhancement while maintaining our ethical standards.

---

## Code of Conduct

### Our Commitment

ClearCraft is designed for **ethical text improvement only**. We will not accept contributions that:

- Attempt to bypass AI detection systems
- Enable plagiarism or academic dishonesty
- Remove watermarks or signatures
- Facilitate deceptive practices
- Violate copyright or intellectual property

### Expected Behavior

- Be respectful and inclusive
- Focus on technical merit
- Provide constructive feedback
- Maintain ethical standards
- Document your work thoroughly

---

## How to Contribute

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/clearcraft.git
cd clearcraft
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies including dev tools
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio ruff mypy

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy environment template
cp .env.sample .env
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 4. Make Your Changes

Follow our coding standards:

#### Code Style

We use **Ruff** for linting and formatting:

```bash
# Check code
ruff check clearcraft/

# Auto-fix issues
ruff check --fix clearcraft/

# Format code
ruff format clearcraft/
```

#### Type Hints

We use **MyPy** for static type checking:

```bash
mypy clearcraft/
```

All new code should include proper type hints:

```python
def analyze_text(text: str, language: str = "en") -> AnalysisResult:
    """Analyze text for readability metrics."""
    ...
```

#### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings
- Include examples for complex functions

```python
def rewrite(
    self,
    text: str,
    tone: str = "neutral",
) -> RewriteResult:
    """
    Rewrite text for improved clarity.

    Args:
        text: Input text to rewrite.
        tone: Desired tone (neutral/academic/conversational).

    Returns:
        RewriteResult with original and rewritten text plus metrics.

    Raises:
        SimilarityViolationError: If similarity falls below threshold.
        ChangeRatioViolationError: If change ratio exceeds maximum.

    Example:
        >>> selector = TextSelector()
        >>> result = selector.rewrite("Complex text here.", tone="neutral")
        >>> print(result.rewritten_text)
    """
    ...
```

### 5. Add Tests

We maintain high test coverage. Add tests for all new features:

```bash
# Create test file
touch tests/test_your_feature.py
```

Example test:

```python
import pytest
from clearcraft.your_module import YourClass

class TestYourFeature:
    """Test your new feature."""

    def test_basic_functionality(self):
        """Test basic use case."""
        obj = YourClass()
        result = obj.method("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case."""
        obj = YourClass()
        with pytest.raises(ValueError):
            obj.method("")
```

Run tests:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=clearcraft --cov-report=html

# Run specific test file
pytest tests/test_your_feature.py -v
```

### 6. Update Documentation

If you add new features:

1. Update **README.md** with new features
2. Add examples to **USAGE.md**
3. Document methods in **METHODS.md** if adding new algorithms
4. Update **CHANGELOG.md** (create if needed)

### 7. Commit Your Changes

Follow conventional commit format:

```bash
# Feature
git commit -m "feat: add support for Spanish language lexicons"

# Bug fix
git commit -m "fix: correct passive voice detection in complex sentences"

# Documentation
git commit -m "docs: add examples for batch processing"

# Tests
git commit -m "test: add coverage for edge cases in similarity checking"

# Refactor
git commit -m "refactor: simplify chunking logic for better performance"
```

Commit message types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance tasks

### 8. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:

- **Clear title** describing the change
- **Description** explaining what and why
- **Tests** showing coverage
- **Screenshots** if UI changes
- **Breaking changes** if any

---

## Development Guidelines

### Project Structure

```
clearcraft/
├── clearcraft/          # Main package
│   ├── rewriters/      # Text transformation modules
│   ├── adapters/       # External service integrations
│   └── ...
├── rules/              # YAML configuration files
├── templates/          # Frontend templates
├── tests/              # Test suite
└── docs/               # Documentation
```

### Adding New Rewriters

To add a new rewriter module:

1. Create file in `clearcraft/rewriters/`
2. Implement base interface:

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class YourOperation:
    """Record of your operation."""
    original: str
    modified: str
    confidence: float
    reason: str

class YourRewriter:
    """Your rewriter description."""

    def __init__(self, param: str = "default"):
        """Initialize rewriter."""
        self.param = param

    def process(self, text: str) -> Tuple[str, List[YourOperation]]:
        """
        Process text and apply transformations.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, operations).
        """
        # Your implementation
        operations: List[YourOperation] = []
        # ... process text ...
        return processed_text, operations
```

3. Add to `clearcraft/rewriters/__init__.py`
4. Integrate in `clearcraft/selector.py`
5. Add tests in `tests/test_your_rewriter.py`
6. Update documentation

### Adding New Languages

To add support for a new language:

1. Create lexicon files:
   - `rules/jargon_XX.yaml` (XX = language code)
   - `rules/fillers_XX.yaml`

2. Update language parameter handling in:
   - `clearcraft/config.py`
   - `clearcraft/rewriters/jargon_plain.py`
   - `clearcraft/rewriters/repetition_trim.py`

3. Add language-specific tests
4. Update documentation

### Adding New Metrics

To add a new readability metric:

1. Update `ReadabilityMetrics` dataclass in `clearcraft/analysis.py`
2. Implement calculation in `TextAnalyzer.analyze()`
3. Update API response models in `clearcraft/server.py`
4. Update frontend templates to display new metric
5. Add tests validating the metric
6. Document the metric in `METHODS.md` with citations

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_jargon_replacement():
    """Test jargon simplification."""
    simplifier = JargonSimplifier()
    result, replacements = simplifier.process("Utilize this methodology.")
    assert "use" in result.lower()
```

### Integration Tests

Test component interactions:

```python
def test_full_rewrite_pipeline():
    """Test complete rewrite with all passes."""
    selector = TextSelector(enable_llm=False)
    result = selector.rewrite("Complex text here.")
    assert result.overall_similarity > 0.90
    assert len(result.change_operations) > 0
```

### Golden Tests

Test expected outputs for known inputs:

```python
def test_golden_passive_to_active():
    """Test known passive voice conversion."""
    activator = VoiceActivator()
    original = "The report was written by Alice."
    result, _ = activator.process(original)
    assert "Alice wrote" in result
```

### API Tests

Test HTTP endpoints:

```python
from fastapi.testclient import TestClient
from clearcraft.server import app

client = TestClient(app)

def test_analyze_endpoint():
    """Test /api/analyze endpoint."""
    response = client.post(
        "/api/analyze",
        json={"text": "Test sentence."}
    )
    assert response.status_code == 200
    assert "metrics" in response.json()
```

---

## Performance Guidelines

- **Chunking**: For texts > 10K characters, ensure proper chunking
- **Caching**: Cache expensive operations (embeddings, model loading)
- **Streaming**: Consider streaming for large documents
- **Memory**: Profile memory usage for models
- **Benchmarks**: Add benchmarks for critical paths

Example benchmark:

```python
import time

def test_analysis_performance():
    """Ensure analysis completes in <1 second."""
    analyzer = TextAnalyzer()
    text = "Sample text." * 100

    start = time.time()
    analyzer.analyze(text)
    duration = time.time() - start

    assert duration < 1.0
```

---

## Security Considerations

### Input Validation

- Always validate user input
- Enforce max text length
- Sanitize file uploads
- Prevent code injection

### API Keys

- Never commit API keys
- Use environment variables
- Document key management

### Data Privacy

- Don't log user text content
- Implement PII redaction if enabled
- Document data retention policies

---

## Review Process

Pull requests will be reviewed for:

1. **Code Quality**
   - Follows style guidelines
   - Proper type hints
   - Clear variable names

2. **Tests**
   - Adequate coverage (aim for >80%)
   - Edge cases handled
   - No failing tests

3. **Documentation**
   - Docstrings present
   - README updated if needed
   - Examples provided

4. **Ethics**
   - No detector evasion code
   - Maintains transparency
   - Preserves meaning

5. **Performance**
   - No significant regressions
   - Benchmarks pass
   - Memory usage reasonable

---

## Getting Help

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Email**: contact@clearcraft.example (for security issues)

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make ClearCraft better! 🎉
