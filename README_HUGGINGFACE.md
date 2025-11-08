---
title: ClearCraft - AI Text Clarity Enhancement
emoji: ✨
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.29.0"
app_file: streamlit_app.py
pinned: false
license: mit
---

# ClearCraft ✨

**Production-grade AI text clarity and readability enhancement tool with ethical guardrails.**

ClearCraft improves text clarity, readability, and flow while preserving meaning, citations, and formatting. It uses deterministic text processing combined with optional DeepInfra LLM enhancement.

## 🎯 Features

- **📊 Readability Analysis** - Flesch, Gunning Fog, MTLD, TTR, passive voice detection
- **✍️ Text Rewriting** - 7 deterministic enhancement modules
- **🤖 LLM Enhancement** - Optional DeepInfra integration (Llama 4, Claude, Qwen, DeepSeek)
- **🔬 Semantic Similarity** - Neural embeddings to preserve meaning (92%+ threshold)
- **📝 Citation Preservation** - Protects references, links, code blocks, formatting
- **⚖️ Quality Guardrails** - Max 30% change ratio, ethical safeguards

## 🚀 Quick Start

1. **Enter your text** in the main text area
2. **Choose settings** in the sidebar (tone, sentence length, etc.)
3. **Optional:** Enable DeepInfra LLM and enter API key
4. **Click "Analyze"** to see readability metrics
5. **Click "Rewrite"** to improve your text
6. **Download** the improved version

## 🤖 DeepInfra LLM (Optional)

To use LLM enhancement:

1. Get a free API key from [DeepInfra](https://deepinfra.com)
2. Enable "LLM Enhancement" in the sidebar
3. Enter your API key
4. Choose a model (Llama 4, Claude, Qwen, DeepSeek)

**Note:** LLM feature costs money per token. Works great without it!

## ⚙️ How It Works

### Deterministic Rewriters (Always Active):
1. **Syntax Split** - Breaks overly long sentences
2. **Syntax Merge** - Combines ultra-short fragments
3. **Voice Activator** - Converts passive to active voice
4. **Jargon Simplifier** - Replaces technical terms
5. **Repetition Trimmer** - Removes fillers and varies openings
6. **Grammar Corrector** - Applies whitelisted fixes
7. **Formatter** - Normalizes quotes, dashes, spacing

### Optional LLM Polish:
- Uses DeepInfra API for editorial refinement
- Multiple model choices
- Still enforces similarity/change guardrails

### Quality Guarantees:
- ✅ **92%+ semantic similarity** (meaning preserved)
- ✅ **Max 30% text changes** (author voice preserved)
- ✅ **Citations protected** (references, links, code blocks intact)
- ✅ **Ethical guardrails** (blocks misuse attempts)

## 📊 Example

**Before:**
> The implementation of sophisticated algorithmic methodologies was undertaken by the research team to facilitate optimization of complex paradigms.

**After:**
> The research team implemented sophisticated algorithms to optimize complex systems.

**Metrics:**
- Flesch Reading Ease: 23.5 → 48.2 ✅
- Passive Voice: 100% → 0% ✅
- Semantic Similarity: 94.3% ✅
- Change Ratio: 28% ✅

## ⚖️ Ethical Use

ClearCraft is designed for **legitimate text improvement only**:

✅ Academic paper clarity
✅ Business document simplification
✅ Blog post readability
✅ Technical documentation

❌ NOT for:
- Bypassing AI detection
- Academic dishonesty
- Evading content filters
- Deceptive content generation

## 🛠️ Technology Stack

- **NLP:** spaCy, sentence-transformers, PyTorch
- **Metrics:** Flesch-Kincaid, Gunning Fog, SMOG, MTLD
- **UI:** Streamlit
- **LLM:** DeepInfra API (optional)

## 📚 Documentation

- [Full Documentation](https://github.com/seblosiv/humanizer)
- [Deployment Guide](HUGGINGFACE_DEPLOY.md)
- [Research Methods](METHODS.md)
- [Performance Tuning](PERFORMANCE.md)
- [Security Best Practices](SECURITY.md)

## 📝 License

MIT License with Ethical Use Notice

---

**Built with ❤️ using Python, spaCy, Transformers, and Streamlit**

**Version:** 1.0.0
**Platform:** HuggingFace Spaces
**GitHub:** https://github.com/seblosiv/humanizer
