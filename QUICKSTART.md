# ClearCraft Quick Start Guide

Get up and running with ClearCraft in 5 minutes! ⚡

---

## 🚀 Installation (Choose One)

### Option 1: Automated Setup (Recommended)
```bash
git clone <repo-url>
cd humanizer
chmod +x setup.sh
./setup.sh
source venv/bin/activate
```

### Option 2: Docker (Fastest)
```bash
docker-compose up -d
# Visit http://localhost:8000
```

### Option 3: Manual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🎯 First Steps

### 1. Start the Web Server
```bash
clearcraft server
```
Visit: **http://localhost:8000**

### 2. Analyze Text (CLI)
```bash
clearcraft analyze --text "Your text here"
```

### 3. Rewrite Text (CLI)
```bash
clearcraft rewrite --text "Your text here" --output improved.txt
```

---

## 📋 Common Commands

### Web Server
```bash
# Start server
clearcraft server

# Custom port
clearcraft server --port 8080

# Development mode (auto-reload)
clearcraft server --reload
```

### Analysis
```bash
# From file
clearcraft analyze --file document.txt

# From stdin
echo "Text here" | clearcraft analyze --text -
```

### Rewriting
```bash
# Basic rewrite
clearcraft rewrite --file input.txt --output output.txt

# Academic tone
clearcraft rewrite --file paper.txt --tone academic

# Conversational tone
clearcraft rewrite --file blog.txt --tone conversational

# Custom sentence length
clearcraft rewrite --file doc.txt --min-length 16 --max-length 24

# With LLM (requires API key)
clearcraft rewrite --file doc.txt --llm

# Without disclosure
clearcraft rewrite --file doc.txt --no-disclosure
```

---

## 🌐 API Usage

### Analyze Endpoint
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'
```

### Rewrite Endpoint
```bash
curl -X POST http://localhost:8000/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "tone": "neutral",
    "enable_llm": false
  }'
```

### Health Check
```bash
curl http://localhost:8000/healthz
```

---

## 🐍 Python API

### Quick Example
```python
from clearcraft.selector import TextSelector

# Initialize
selector = TextSelector()

# Rewrite
result = selector.rewrite("Your text here", tone="neutral")

# Print results
print(result.rewritten_text)
print(f"Similarity: {result.overall_similarity:.1%}")
```

### Detailed Example
```python
from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector

# Analyze first
analyzer = TextAnalyzer()
analysis = analyzer.analyze("Your text here")

print(f"Flesch Score: {analysis.metrics.flesch_reading_ease:.1f}")
print(f"Passive Voice: {analysis.metrics.passive_ratio:.1%}")

# Then rewrite
selector = TextSelector(
    target_avg_sentence_length=(14, 22),
    max_change_ratio=0.30,
    similarity_min=0.92,
)

result = selector.rewrite(
    text="Your text here",
    tone="neutral",
)

print(f"Original: {result.original_text}")
print(f"Improved: {result.rewritten_text}")
```

---

## 🎨 Web Interface

1. **Navigate** to http://localhost:8000
2. **Choose tab**:
   - **Analyze**: Get readability metrics
   - **Rewrite**: Improve clarity
3. **Paste** your text
4. **Configure** options (tone, sentence length, etc.)
5. **Click** Analyze or Rewrite
6. **Review** results and download

---

## ⚙️ Configuration

### Environment Variables (.env)
```bash
# Copy template
cp .env.sample .env

# Edit configuration
nano .env
```

### Key Settings
```bash
# DeepInfra (optional - for LLM mode)
DEEPINFRA_API_TOKEN=your_token_here

# Quality settings
MAX_CHANGE_RATIO=0.30      # Max 30% changes
SIMILARITY_MIN=0.92         # Min 92% similarity

# Readability targets
TARGET_AVG_SENTENCE_LENGTH_MIN=14
TARGET_AVG_SENTENCE_LENGTH_MAX=22
```

---

## 📊 Example Workflows

### Academic Paper Enhancement
```bash
# 1. Analyze readability
clearcraft analyze --file paper.txt

# 2. Rewrite with academic tone
clearcraft rewrite \
  --file paper.txt \
  --output paper_improved.txt \
  --tone academic \
  --min-length 16 \
  --max-length 24

# 3. Review changes
diff paper.txt paper_improved.txt
```

### Business Document Simplification
```bash
# Simplify jargon-heavy business text
clearcraft rewrite \
  --file business_doc.txt \
  --output simplified.txt \
  --tone conversational \
  --min-length 12 \
  --max-length 18
```

### Blog Post Readability
```bash
# Improve blog readability
clearcraft rewrite \
  --file blog_draft.txt \
  --output blog_final.txt \
  --tone conversational
```

---

## 🧪 Try the Interactive Demo

```bash
python examples/demo.py
```

**Demonstrates:**
- ✅ Text analysis with metrics
- ✅ Before/after rewriting
- ✅ Semantic similarity
- ✅ Jargon simplification
- ✅ Citation preservation

---

## 🐳 Docker Commands

```bash
# Build
docker build -t clearcraft .

# Run
docker run -d -p 8000:8000 clearcraft

# With docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔍 Sample Files

Try with included samples:

```bash
# Complex academic text
clearcraft analyze --file examples/sample_academic.txt

# Business jargon
clearcraft rewrite --file examples/sample_business.txt

# Blog with fillers
clearcraft rewrite --file examples/sample_blog.txt --tone conversational
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'clearcraft'"
```bash
# Ensure virtual environment is activated
source venv/bin/activate
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

### "Port 8000 already in use"
```bash
# Use different port
clearcraft server --port 8080

# Or find and kill process
lsof -i :8000
kill -9 <PID>
```

### Docker issues
```bash
# Rebuild
docker-compose build --no-cache

# Check logs
docker-compose logs
```

---

## 📚 Learn More

- **Full Documentation**: [README.md](README.md)
- **Usage Examples**: [USAGE.md](USAGE.md)
- **Research Methods**: [METHODS.md](METHODS.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🎯 Quick Tips

1. **Always analyze first** to understand baseline metrics
2. **Start with default settings** then adjust as needed
3. **Use appropriate tone** for your content type
4. **Review output carefully** - always verify changes
5. **Enable disclosure** for transparency
6. **Try the demo** to see all features in action

---

## ⚡ One-Liner Examples

```bash
# Analyze and show key metrics
clearcraft analyze --text "Text here" | grep -E "Flesch|Passive"

# Quick rewrite with defaults
echo "Text here" | clearcraft rewrite --text - --output -

# Batch process multiple files
for f in *.txt; do clearcraft rewrite --file "$f" --output "improved_$f"; done

# Check if service is healthy
curl -sf http://localhost:8000/healthz && echo "OK" || echo "FAIL"
```

---

## 🚀 Next Steps

After getting started:

1. **Explore the web UI** at http://localhost:8000
2. **Try different tones** (neutral, academic, conversational)
3. **Test with your own content**
4. **Review API documentation** at http://localhost:8000/docs
5. **Configure DeepInfra** for premium LLM mode (optional)

---

**Need Help?** See [USAGE.md](USAGE.md) for detailed examples or run `clearcraft --help`

**Ready to dive deeper?** Check out [README.md](README.md) for comprehensive documentation.

---

*Last Updated: 2025-01-08 | Version 1.0.0*
