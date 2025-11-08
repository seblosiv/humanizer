# ClearCraft Troubleshooting Guide

Common issues and their solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Issues](#performance-issues)
4. [API Issues](#api-issues)
5. [Docker Issues](#docker-issues)
6. [Configuration Issues](#configuration-issues)
7. [Model Issues](#model-issues)
8. [Text Processing Issues](#text-processing-issues)

---

## Installation Issues

### Q: `python3: command not found`

**Problem:** Python 3 is not installed or not in PATH.

**Solution:**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-venv python3-pip

# macOS
brew install python@3.11

# Check installation
python3 --version
```

---

### Q: `ModuleNotFoundError: No module named 'clearcraft'`

**Problem:** Virtual environment not activated or package not installed.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Verify activation (should show venv path)
which python

# Reinstall if needed
pip install -e .
```

---

### Q: `ERROR: Could not install packages due to an OSError`

**Problem:** Permission denied or disk space issues.

**Solution:**
```bash
# Check disk space
df -h

# Install in user directory
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

---

### Q: `torch` installation fails or takes forever

**Problem:** PyTorch is large and platform-specific.

**Solution:**
```bash
# Install CPU-only version (faster, smaller)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install remaining requirements
pip install -r requirements.txt
```

---

## Runtime Errors

### Q: `OSError: [E050] Can't find model 'en_core_web_sm'`

**Problem:** spaCy model not downloaded.

**Solution:**
```bash
# Download the model
python -m spacy download en_core_web_sm

# Verify
python -c "import spacy; spacy.load('en_core_web_sm')"
```

---

### Q: `RuntimeError: sentence-transformers requires PyTorch`

**Problem:** PyTorch not installed or incompatible version.

**Solution:**
```bash
# Install/reinstall PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Reinstall sentence-transformers
pip install --force-reinstall sentence-transformers
```

---

### Q: `ImportError: cannot import name 'TextAnalyzer'`

**Problem:** Module structure changed or corrupted installation.

**Solution:**
```bash
# Clean and reinstall
make clean
pip install -e . --force-reinstall

# Or manually
pip uninstall clearcraft
pip install -e .
```

---

### Q: `Memory Error` or system crashes

**Problem:** Not enough RAM for models.

**Solution:**
```bash
# Check memory usage
free -h  # Linux
top      # macOS

# Solutions:
# 1. Close other applications
# 2. Use swap space
# 3. Reduce batch size in config
# 4. Use smaller models
```

---

## Performance Issues

### Q: Analysis/rewriting is very slow

**Problem:** Large text, slow hardware, or inefficient configuration.

**Solution:**

1. **Check text length:**
```python
len(your_text)  # Should be < 50,000 chars
```

2. **Enable model caching:**
```bash
# Set in .env
TRANSFORMERS_CACHE=.cache/huggingface
SENTENCE_TRANSFORMERS_HOME=.cache/sentence-transformers
```

3. **Use smaller chunks:**
```bash
# In .env
CHUNK_SIZE=500  # Default is 1000
```

4. **Disable LLM mode** if not needed:
```python
selector = TextSelector(enable_llm=False)
```

---

### Q: First request is slow, subsequent requests are fast

**Problem:** Model loading (normal behavior).

**Solution:**
This is expected. Models are loaded on first use and cached. Consider:
- Pre-warming the server
- Using a startup script
- Accepting the initial latency

```python
# Pre-warm script
from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector

analyzer = TextAnalyzer()
selector = TextSelector()

# Force model loading
analyzer.analyze("warmup text")
selector.rewrite("warmup text")
```

---

### Q: High CPU usage

**Problem:** NLP models are CPU-intensive.

**Solution:**
```bash
# Limit threads
export OMP_NUM_THREADS=2
export MKL_NUM_THREADS=2

# Run server with fewer workers
uvicorn clearcraft.server:app --workers 2
```

---

## API Issues

### Q: `Connection refused` when calling API

**Problem:** Server not running or wrong port.

**Solution:**
```bash
# Check if server is running
curl http://localhost:8000/healthz

# If not running, start it
clearcraft server

# Check correct port
clearcraft server --port 8080  # Custom port
```

---

### Q: `422 Unprocessable Entity` error

**Problem:** Invalid request format or missing required fields.

**Solution:**
```bash
# Ensure correct JSON format
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'  # Note the quotes

# Check API docs
open http://localhost:8000/docs
```

---

### Q: `400 Bad Request: Text too long`

**Problem:** Text exceeds maximum length.

**Solution:**
```bash
# Check max length
grep MAX_TEXT_LENGTH .env

# Increase limit (in .env)
MAX_TEXT_LENGTH=100000

# Or chunk your text
```

---

### Q: `403 Forbidden: Disallowed intent detected`

**Problem:** Text contains blocked keywords (bypass, evade, etc.).

**Solution:**
This is intentional. ClearCraft blocks attempts to evade AI detection. Either:
- Remove the problematic keywords
- Rephrase your text
- Understand this is an ethical safeguard

---

### Q: API returns `500 Internal Server Error`

**Problem:** Server-side error.

**Solution:**
```bash
# Check server logs
clearcraft server  # Look at terminal output

# Enable debug mode
DEBUG=true clearcraft server

# Check log file
tail -f clearcraft.log
```

---

## Docker Issues

### Q: `docker: command not found`

**Problem:** Docker not installed.

**Solution:**
```bash
# Install Docker
# Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install --cask docker

# Verify
docker --version
```

---

### Q: `permission denied while trying to connect to Docker daemon`

**Problem:** User not in docker group.

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or:
newgrp docker

# Verify
docker ps
```

---

### Q: Docker build fails with "no space left on device"

**Problem:** Insufficient disk space.

**Solution:**
```bash
# Clean up Docker
docker system prune -a

# Check space
df -h

# Remove unused images
docker rmi $(docker images -q -f dangling=true)
```

---

### Q: Container exits immediately

**Problem:** Error in startup or configuration.

**Solution:**
```bash
# Check container logs
docker logs clearcraft

# Run in foreground to see errors
docker run -it clearcraft

# Check health
docker inspect clearcraft | grep Health
```

---

## Configuration Issues

### Q: Environment variables not being read

**Problem:** `.env` file not loaded or in wrong location.

**Solution:**
```bash
# Ensure .env exists
ls -la .env

# Check it's in project root
pwd
ls .env

# Manually export (testing)
export DEEPINFRA_API_TOKEN=your_token
clearcraft server
```

---

### Q: DeepInfra LLM not working

**Problem:** API token not set or invalid.

**Solution:**
```bash
# Check token is set
grep DEEPINFRA_API_TOKEN .env

# Verify token format (should be long string)
echo $DEEPINFRA_API_TOKEN

# Test token
python -c "
from clearcraft.adapters.deepinfra_llm import DeepInfraAdapter
adapter = DeepInfraAdapter()
print('Token OK' if adapter.test_connection() else 'Token invalid')
"
```

---

### Q: Changes to `.env` not taking effect

**Problem:** Server needs restart or caching.

**Solution:**
```bash
# Restart server
# Stop current server (Ctrl+C)
clearcraft server

# Or for Docker
docker-compose down && docker-compose up -d
```

---

## Model Issues

### Q: Models re-download every time

**Problem:** Cache directory not persistent.

**Solution:**
```bash
# Set cache directories in .env
TRANSFORMERS_CACHE=/path/to/persistent/cache
SENTENCE_TRANSFORMERS_HOME=/path/to/persistent/cache

# For Docker, use volumes
# In docker-compose.yml, ensure volume is mounted
```

---

### Q: `OSError: Disk quota exceeded` when downloading models

**Problem:** Not enough disk space.

**Solution:**
```bash
# Check space
df -h

# Clean up
make clean-cache

# Use smaller models
# In config.py, change:
sentence_transformer_model = "all-MiniLM-L6-v2"  # Smaller, faster
```

---

### Q: Sentence transformer model downloads but doesn't load

**Problem:** Corrupted download or incompatible version.

**Solution:**
```bash
# Remove and re-download
rm -rf .cache/sentence-transformers/*

# Reinstall sentence-transformers
pip install --force-reinstall sentence-transformers

# Test
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model loaded successfully')
"
```

---

## Text Processing Issues

### Q: Similarity always too low, rewriting fails

**Problem:** Threshold too strict or text very different.

**Solution:**
```bash
# Lower threshold (in .env or code)
SIMILARITY_MIN=0.85  # Default is 0.92

# Or in code:
selector = TextSelector(similarity_min=0.85)
```

---

### Q: Change ratio violation errors

**Problem:** Too many changes needed, threshold too strict.

**Solution:**
```bash
# Increase allowed changes (in .env)
MAX_CHANGE_RATIO=0.40  # Default is 0.30

# Or in code:
selector = TextSelector(max_change_ratio=0.40)
```

---

### Q: Code blocks or citations getting modified

**Problem:** Protected span detection failing.

**Solution:**
This is a bug. Please report with example. Workaround:
```python
# Manually verify output
result = selector.rewrite(text)
assert "your_citation" in result.rewritten_text
```

---

### Q: Passive voice not being converted

**Problem:** Pattern not recognized or low confidence.

**Solution:**
```python
# Check passive detection
from clearcraft.rewriters.voice_active import VoiceActivator
activator = VoiceActivator()

# Test specific sentence
sentence = "The report was written by the team."
result = activator.convert_to_active(sentence)
print(result)  # See if conversion works
```

---

### Q: Jargon not being simplified

**Problem:** Word not in lexicon or context-dependent.

**Solution:**
```bash
# Check lexicon
cat rules/jargon_en.yaml | grep "your_word"

# Add custom entries to jargon_en.yaml
your_word:
  replacement: "simple_word"
  pos: "verb"
  context: "general"
```

---

## General Debugging

### Enable Verbose Logging

```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# Run with debug output
LOG_LEVEL=DEBUG clearcraft server
```

---

### Check Component Health

```python
# Test each component individually
from clearcraft.analysis import TextAnalyzer
from clearcraft.similarity import SimilarityChecker
from clearcraft.selector import TextSelector

# Analysis
analyzer = TextAnalyzer()
result = analyzer.analyze("Test text.")
print("Analysis OK")

# Similarity
checker = SimilarityChecker()
sim = checker.compute_similarity("text 1", "text 2")
print(f"Similarity OK: {sim}")

# Rewriting
selector = TextSelector(enable_llm=False)
result = selector.rewrite("Test text.")
print("Rewriting OK")
```

---

### Run Integration Tests

```bash
# Full test suite
make test

# Integration tests only
make integration-test

# Specific test
pytest tests/test_analysis.py -v
```

---

## Still Having Issues?

1. **Check logs:**
   ```bash
   tail -f clearcraft.log
   ```

2. **Run diagnostics:**
   ```bash
   make verify
   ```

3. **Search existing issues:**
   - GitHub Issues: https://github.com/yourorg/clearcraft/issues

4. **Create new issue** with:
   - ClearCraft version (`clearcraft version`)
   - Python version (`python --version`)
   - OS (`uname -a` or Windows version)
   - Complete error message
   - Steps to reproduce

5. **Join discussions:**
   - GitHub Discussions: https://github.com/yourorg/clearcraft/discussions

---

**Last Updated:** 2025-01-08
**Version:** 1.0.0
