# ClearCraft Performance Tuning Guide

Comprehensive guide to optimizing ClearCraft performance for different workloads and constraints.

---

## Table of Contents

1. [Understanding Performance](#understanding-performance)
2. [Quick Optimization Checklist](#quick-optimization-checklist)
3. [Configuration Tuning](#configuration-tuning)
4. [Hardware Considerations](#hardware-considerations)
5. [Model Selection](#model-selection)
6. [Caching Strategies](#caching-strategies)
7. [Text Processing Optimization](#text-processing-optimization)
8. [API Performance](#api-performance)
9. [Benchmarking](#benchmarking)
10. [Troubleshooting Slow Performance](#troubleshooting-slow-performance)

---

## Understanding Performance

### Performance Metrics

ClearCraft performance is measured across several dimensions:

1. **Latency**: Time to process a single request
2. **Throughput**: Requests processed per second
3. **Memory Usage**: RAM consumed by models and processing
4. **CPU Utilization**: Computational load
5. **Disk I/O**: Model loading and caching operations

### Performance Bottlenecks

Common bottlenecks in order of impact:

1. **Model Loading** (first request only): 2-10 seconds
2. **Semantic Similarity Computation**: 50-500ms per comparison
3. **NLP Processing** (spaCy): 10-100ms per 1000 words
4. **Rewriter Operations**: 5-50ms per sentence
5. **Text Chunking**: 1-10ms per 1000 words

---

## Quick Optimization Checklist

### For Speed (Maximum Performance)

```bash
# Copy to .env
CHUNK_SIZE=2000
MAX_TEXT_LENGTH=100000
MAX_CHANGE_RATIO=0.35
SIMILARITY_MIN=0.88
SENTENCE_TRANSFORMER_MODEL=paraphrase-MiniLM-L3-v2
TRANSFORMERS_CACHE=.cache/huggingface
SENTENCE_TRANSFORMERS_HOME=.cache/sentence-transformers
```

**Expected:** 2-3x faster processing, slightly lower quality

### For Quality (Maximum Accuracy)

```bash
# Copy to .env
CHUNK_SIZE=500
MAX_TEXT_LENGTH=50000
MAX_CHANGE_RATIO=0.25
SIMILARITY_MIN=0.95
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-mpnet-base-v2
```

**Expected:** Highest quality, 2-3x slower

### Balanced Configuration (Recommended)

```bash
# Copy to .env
CHUNK_SIZE=1000
MAX_TEXT_LENGTH=50000
MAX_CHANGE_RATIO=0.30
SIMILARITY_MIN=0.92
SENTENCE_TRANSFORMER_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**Expected:** Good balance of speed and quality

---

## Configuration Tuning

### Chunk Size Optimization

**Impact:** Affects processing speed and accuracy

```python
# Large chunks (faster, less precise)
CHUNK_SIZE=2000
# Pros: Fewer similarity checks, faster overall
# Cons: Less granular control, may miss subtle issues
# Use for: Batch processing, large documents, speed-critical apps

# Medium chunks (balanced)
CHUNK_SIZE=1000
# Pros: Good balance
# Cons: None significant
# Use for: General purpose, production defaults

# Small chunks (slower, more precise)
CHUNK_SIZE=500
# Pros: Very precise improvements, better quality
# Cons: More similarity checks, slower processing
# Use for: Academic papers, high-stakes content
```

**Recommendation:** Start with 1000, adjust based on use case.

### Similarity Threshold Tuning

**Impact:** Affects processing success rate and quality

```python
# Strict similarity (0.95+)
SIMILARITY_MIN=0.95
# Pros: Minimal semantic drift, preserves meaning strictly
# Cons: May reject valid improvements, slower
# Use for: Legal documents, academic papers, citations-heavy

# Moderate similarity (0.90-0.94)
SIMILARITY_MIN=0.92
# Pros: Good balance, allows improvements while preserving meaning
# Cons: None significant
# Use for: General purpose, most content types

# Relaxed similarity (0.85-0.89)
SIMILARITY_MIN=0.88
# Pros: More aggressive improvements, faster processing
# Cons: Higher semantic drift risk
# Use for: Blog posts, creative content, informal writing
```

**Recommendation:** 0.92 for production, adjust based on content type.

### Change Ratio Limits

**Impact:** Affects how much text can be modified

```python
# Conservative (20-25%)
MAX_CHANGE_RATIO=0.25
# Pros: Minimal changes, preserves original style
# Cons: May not improve heavily problematic text
# Use for: Academic writing, formal documents

# Moderate (30-35%)
MAX_CHANGE_RATIO=0.30
# Pros: Balanced improvements
# Cons: None significant
# Use for: General purpose, business documents

# Aggressive (40%+)
MAX_CHANGE_RATIO=0.40
# Pros: Substantial improvements possible
# Cons: May alter original voice/style
# Use for: Heavily jargon-laden text, poor initial quality
```

**Recommendation:** 0.30 for production.

---

## Hardware Considerations

### CPU Optimization

**Requirements:**
- Minimum: 2 cores, 2.0 GHz
- Recommended: 4 cores, 3.0 GHz
- Optimal: 8+ cores, 3.5+ GHz

**Tuning:**

```bash
# Limit CPU threads (reduces peak usage)
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Set in systemd service
Environment="OMP_NUM_THREADS=4"
```

**Impact:** Lower thread count reduces peak CPU but may increase latency.

### Memory Optimization

**Requirements:**
- Minimum: 2 GB RAM
- Recommended: 4 GB RAM
- Optimal: 8+ GB RAM

**Memory Usage Breakdown:**
- Base Python process: ~100 MB
- spaCy model (en_core_web_sm): ~40 MB
- Sentence-transformer (all-MiniLM-L6-v2): ~80 MB
- Sentence-transformer (all-mpnet-base-v2): ~420 MB
- Processing overhead: ~200-500 MB

**Tuning:**

```bash
# Use smaller models
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2  # 80 MB
SPACY_MODEL=en_core_web_sm                    # 40 MB

# Limit text length
MAX_TEXT_LENGTH=10000  # Reduce memory per request
```

### Disk I/O Optimization

**Requirements:**
- Minimum: 5 GB free space
- Recommended: 10 GB free space (for caching)

**Tuning:**

```bash
# Use SSD for cache directory
TRANSFORMERS_CACHE=/ssd/path/cache

# Persistent cache location
SENTENCE_TRANSFORMERS_HOME=/var/cache/clearcraft
```

**Impact:** SSD can improve model loading by 2-3x.

---

## Model Selection

### Sentence Transformer Models

**Comparison:**

| Model | Size | Dimensions | Speed | Accuracy | Use Case |
|-------|------|------------|-------|----------|----------|
| paraphrase-MiniLM-L3-v2 | 60 MB | 384 | Fastest | Good | Speed-critical, batch |
| all-MiniLM-L6-v2 | 80 MB | 384 | Fast | Very Good | **Production default** |
| all-mpnet-base-v2 | 420 MB | 768 | Slow | Excellent | High-quality, academic |
| all-MiniLM-L12-v2 | 120 MB | 384 | Moderate | Excellent | Balanced quality |

**Recommendation:**
- **Production:** all-MiniLM-L6-v2
- **Low resource:** paraphrase-MiniLM-L3-v2
- **High quality:** all-mpnet-base-v2

**Changing models:**

```python
# In config.py or .env
SENTENCE_TRANSFORMER_MODEL=paraphrase-MiniLM-L3-v2

# Test performance
python examples/benchmark.py
```

### spaCy Models

**Options:**
- `en_core_web_sm`: 12 MB, fast, good accuracy (default)
- `en_core_web_md`: 40 MB, moderate, better accuracy
- `en_core_web_lg`: 560 MB, slow, best accuracy

**Recommendation:** Stick with `en_core_web_sm` unless you need entity recognition accuracy.

---

## Caching Strategies

### Model Caching

**Problem:** Models re-download on every deployment.

**Solution:**

```bash
# Set persistent cache
TRANSFORMERS_CACHE=/var/cache/clearcraft/huggingface
SENTENCE_TRANSFORMERS_HOME=/var/cache/clearcraft/sentence-transformers

# Pre-download models
python -c "
from sentence_transformers import SentenceTransformer
import spacy
SentenceTransformer('all-MiniLM-L6-v2')
spacy.load('en_core_web_sm')
"
```

**Docker:**

```yaml
# docker-compose.yml
volumes:
  - model-cache:/app/.cache
```

### Application-Level Caching

**Singleton pattern (already implemented):**

```python
# Models loaded once, reused across requests
analyzer = TextAnalyzer()  # Loads spaCy once
similarity_checker = SimilarityChecker()  # Loads transformer once
```

**Result caching (future enhancement):**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached(text: str):
    return analyzer.analyze(text)
```

---

## Text Processing Optimization

### Chunking Strategy

**Optimal chunk sizes by use case:**

```python
# Academic papers (precision)
CHUNK_SIZE=500

# Business documents (balanced)
CHUNK_SIZE=1000

# Blog posts (speed)
CHUNK_SIZE=1500

# Batch processing (throughput)
CHUNK_SIZE=2000
```

### Readability Target Tuning

**Impact:** Affects number of sentence splits/merges

```bash
# Tight range (more modifications)
TARGET_AVG_SENTENCE_LENGTH_MIN=15
TARGET_AVG_SENTENCE_LENGTH_MAX=20

# Wide range (fewer modifications, faster)
TARGET_AVG_SENTENCE_LENGTH_MIN=12
TARGET_AVG_SENTENCE_LENGTH_MAX=25
```

**Recommendation:** Wider range = faster processing.

### Passive Voice Threshold

**Impact:** Affects active voice conversion attempts

```bash
# Strict (more conversions)
MAX_PASSIVE_RATIO=0.10

# Relaxed (fewer conversions, faster)
MAX_PASSIVE_RATIO=0.20
```

---

## API Performance

### Server Configuration

**Single Worker (Development):**

```bash
clearcraft server
# Uvicorn default: 1 worker
```

**Multiple Workers (Production):**

```bash
uvicorn clearcraft.server:app --workers 4 --host 0.0.0.0 --port 8000
# Workers = (2 x CPU cores) + 1
```

**Gunicorn (Production):**

```bash
gunicorn clearcraft.server:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Request Optimization

**Batch processing:**

```python
# Instead of:
for text in texts:
    result = requests.post("/api/rewrite", json={"text": text})

# Use concurrent requests:
import concurrent.futures

def rewrite(text):
    return requests.post("/api/rewrite", json={"text": text})

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(rewrite, texts))
```

### Connection Pooling

```python
import requests

# Reuse session
session = requests.Session()

# Benefits: Connection reuse, faster requests
for i in range(100):
    response = session.post("/api/rewrite", json={"text": text})
```

---

## Benchmarking

### Running Benchmarks

```bash
# Built-in benchmark tool
python examples/benchmark.py

# Custom benchmark
make benchmark
```

**Expected Performance (all-MiniLM-L6-v2, 4 core CPU):**

| Text Length | Analysis Time | Rewrite Time | Throughput |
|-------------|---------------|--------------|------------|
| 100 chars   | 0.05s        | 0.3s         | 2000 c/s   |
| 1,000 chars | 0.1s         | 1.5s         | 650 c/s    |
| 5,000 chars | 0.3s         | 4.0s         | 1200 c/s   |
| 10,000 chars| 0.5s         | 7.0s         | 1400 c/s   |

**Note:** First request adds 2-5s for model loading.

### Profiling

**Python profiler:**

```bash
python -m cProfile -o profile.stats examples/demo.py

# Analyze
python -m pstats profile.stats
# > sort cumtime
# > stats 20
```

**Memory profiling:**

```bash
pip install memory_profiler

python -m memory_profiler examples/demo.py
```

**Line profiler:**

```bash
pip install line_profiler

# Add @profile decorator to functions
kernprof -l -v examples/demo.py
```

---

## Troubleshooting Slow Performance

### Issue: First request takes 5-10 seconds

**Cause:** Model loading

**Solution:**
- Accept initial latency (models cached after)
- Pre-warm server on startup
- Use serverless with warm instances

### Issue: Every request is slow (>10s for 1000 chars)

**Cause:** CPU/memory constraints or configuration

**Diagnosis:**

```bash
# Check CPU usage
top
# Look for python process at 100% sustained

# Check memory
free -h
# Look for swap usage

# Check disk I/O
iostat -x 1
```

**Solutions:**
- Increase CPU allocation
- Add more memory
- Use smaller models
- Reduce chunk size

### Issue: Similarity checks very slow

**Cause:** Large model or many comparisons

**Solution:**

```bash
# Switch to smaller model
SENTENCE_TRANSFORMER_MODEL=paraphrase-MiniLM-L3-v2

# Increase chunk size (fewer comparisons)
CHUNK_SIZE=2000
```

### Issue: Server crashes with large texts

**Cause:** Out of memory

**Solution:**

```bash
# Reduce max text length
MAX_TEXT_LENGTH=10000

# Add swap space (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Issue: Degrading performance over time

**Cause:** Memory leak or resource exhaustion

**Diagnosis:**

```bash
# Monitor memory over time
watch -n 1 free -h

# Check for zombie processes
ps aux | grep clearcraft
```

**Solution:**
- Restart server periodically
- Use worker timeout (Gunicorn)
- Report potential memory leak

---

## Performance Optimization Workflow

### 1. Baseline Measurement

```bash
# Run benchmark
python examples/benchmark.py > baseline.txt

# Note current config
cat .env > baseline_config.txt
```

### 2. Identify Bottleneck

```python
# Profile the slow operation
import time

start = time.time()
analyzer.analyze(text)
print(f"Analysis: {time.time() - start:.2f}s")

start = time.time()
selector.rewrite(text)
print(f"Rewrite: {time.time() - start:.2f}s")
```

### 3. Apply Optimization

Choose from:
- Model change
- Configuration tuning
- Hardware upgrade
- Caching improvement

### 4. Re-measure

```bash
# Run benchmark again
python examples/benchmark.py > optimized.txt

# Compare
diff baseline.txt optimized.txt
```

### 5. Validate Quality

```bash
# Run integration tests
make integration-test

# Verify similarity still acceptable
# Check output quality manually
```

---

## Advanced Optimization Techniques

### Multi-Stage Caching

```python
# Cache at multiple levels
# 1. Model caching (built-in)
# 2. Result caching (add LRU)
# 3. CDN caching (for API responses)
```

### Lazy Loading

```python
# Load models only when needed
class LazyAnalyzer:
    def __init__(self):
        self._analyzer = None

    @property
    def analyzer(self):
        if self._analyzer is None:
            self._analyzer = TextAnalyzer()
        return self._analyzer
```

### Async Processing

```python
# For API (already implemented in FastAPI)
@app.post("/api/rewrite")
async def rewrite_text(request: RewriteRequest):
    # FastAPI handles async automatically
    result = selector.rewrite(request.text)
    return result
```

### Background Jobs

```python
# For long-running tasks
from celery import Celery

app = Celery('clearcraft', broker='redis://localhost')

@app.task
def rewrite_async(text: str):
    return selector.rewrite(text)
```

---

## Production Optimization Checklist

- [ ] Enable model caching with persistent volume
- [ ] Set appropriate chunk size for workload
- [ ] Choose right model (balance speed/quality)
- [ ] Configure worker count (2 x CPU cores + 1)
- [ ] Set reasonable timeouts (120s)
- [ ] Monitor memory usage
- [ ] Enable connection pooling (clients)
- [ ] Use async processing where possible
- [ ] Implement result caching (if appropriate)
- [ ] Set up health checks
- [ ] Monitor performance metrics
- [ ] Pre-warm models on startup
- [ ] Use SSD for cache directory
- [ ] Limit max text length appropriately
- [ ] Configure logging level (WARNING+ in prod)

---

## Performance Targets by Tier

### Basic Tier (2 cores, 2GB RAM)

**Configuration:**
```bash
SENTENCE_TRANSFORMER_MODEL=paraphrase-MiniLM-L3-v2
CHUNK_SIZE=1500
MAX_TEXT_LENGTH=10000
```

**Expected:**
- 1-2s for 1000 chars
- 5-10s for 5000 chars
- 1-2 concurrent requests

### Standard Tier (4 cores, 4GB RAM)

**Configuration:**
```bash
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
MAX_TEXT_LENGTH=50000
```

**Expected:**
- 0.5-1s for 1000 chars
- 3-5s for 5000 chars
- 5-10 concurrent requests

### Premium Tier (8+ cores, 8GB+ RAM)

**Configuration:**
```bash
SENTENCE_TRANSFORMER_MODEL=all-mpnet-base-v2
CHUNK_SIZE=500
MAX_TEXT_LENGTH=100000
```

**Expected:**
- 0.3-0.7s for 1000 chars
- 2-4s for 5000 chars
- 20+ concurrent requests

---

## Monitoring Performance

### Key Metrics to Track

1. **Response Time (p50, p95, p99)**
2. **Throughput (requests/second)**
3. **Error Rate (%)**
4. **CPU Utilization (%)**
5. **Memory Usage (MB)**
6. **Model Load Time (s)**

### Using Built-in Monitoring

```python
from clearcraft.monitoring import HealthMonitor

monitor = HealthMonitor()
health = monitor.check_system_health()

print(f"CPU: {health.cpu_percent}%")
print(f"Memory: {health.memory_percent}%")
print(f"Models: {health.models_available}")
```

### External Monitoring (Prometheus)

```python
# Add metrics endpoint
from prometheus_client import Counter, Histogram

request_count = Counter('clearcraft_requests_total', 'Total requests')
request_duration = Histogram('clearcraft_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

---

## Summary: Performance Best Practices

1. **Start with defaults** - optimize only when needed
2. **Measure first** - use benchmarks to identify bottlenecks
3. **Optimize iteratively** - change one thing at a time
4. **Validate quality** - ensure optimizations don't hurt output
5. **Monitor continuously** - track performance over time
6. **Document changes** - keep record of optimizations
7. **Consider trade-offs** - speed vs quality, cost vs performance

---

**Last Updated:** 2025-01-08
**Version:** 1.0.0
**Next:** [Security Best Practices](SECURITY.md)
