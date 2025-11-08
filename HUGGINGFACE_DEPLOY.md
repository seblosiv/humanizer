# Deploy ClearCraft to HuggingFace Spaces

**HuggingFace Spaces is the RECOMMENDED platform for ClearCraft** because:
- ✅ FREE tier with generous ML model support
- ✅ Designed for AI/ML applications
- ✅ Handles large dependencies (PyTorch, transformers, etc.)
- ✅ Better resources than Streamlit Cloud free tier
- ✅ Easy GitHub integration

---

## 🚀 Quick Deploy (5 minutes)

### Step 1: Create HuggingFace Account
1. Go to https://huggingface.co/join
2. Sign up with email or GitHub
3. Verify your email

### Step 2: Create New Space
1. Go to https://huggingface.co/new-space
2. Fill in the form:
   ```
   Space name: clearcraft
   License: mit
   SDK: Streamlit
   Hardware: CPU basic (free)
   ```
3. Click **"Create Space"**

### Step 3: Connect GitHub Repository

**Option A: Direct Git Push (Recommended)**

1. In your new Space, you'll see git instructions
2. Run these commands locally:
   ```bash
   cd /path/to/humanizer
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/clearcraft
   git push hf claude/clearcraft-humanizer-app-011CUvktJ3WqTF1d715kpMAg:main
   ```

**Option B: Upload Files via Web UI**

1. In your Space, click **"Files"** tab
2. Upload these files:
   - `streamlit_app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `packages.txt`
   - All `clearcraft/` directory files
   - All `rules/` directory files
   - All `templates/` directory files (if using FastAPI mode)

**Option C: Use HuggingFace CLI**

```bash
pip install huggingface_hub
huggingface-cli login
huggingface-cli upload-space YOUR_USERNAME/clearcraft /path/to/humanizer --repo-type=space
```

---

## 📁 Required Files

HuggingFace Spaces needs these files in the repository root:

### 1. `README.md` (Space Card)

Create a `README.md` at the root with frontmatter:

```markdown
---
title: ClearCraft
emoji: ✨
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.29.0"
app_file: streamlit_app.py
pinned: false
---

# ClearCraft

AI-powered text clarity enhancement tool.

## Features
- Readability analysis
- Text rewriting with ML
- DeepInfra LLM support
- Semantic similarity checking
```

### 2. `streamlit_app.py` ✅ (Already exists)

### 3. `requirements.txt` ✅ (Already updated with full dependencies)

### 4. `.streamlit/config.toml` ✅ (Already exists)

### 5. `packages.txt` ✅ (Already exists)

### 6. All ClearCraft modules ✅ (Already in repo)

---

## ⚙️ Configuration

### Add DeepInfra API Key (Optional)

1. In your Space, go to **Settings** → **Variables and secrets**
2. Add a new secret:
   ```
   Name: DEEPINFRA_API_TOKEN
   Value: your-api-key-here
   ```
3. Click **Save**

Users can also enter their own API key in the Streamlit sidebar!

---

## 🎯 Deployment Process

After pushing code:

1. **Building** (~5-10 minutes first time)
   - Installing Python dependencies
   - Downloading ML models (PyTorch, transformers, sentence-transformers, spaCy)
   - Total download: ~1.5GB

2. **Running** (automatic)
   - Space starts automatically
   - Available at: `https://huggingface.co/spaces/YOUR_USERNAME/clearcraft`

3. **Status Check**
   - View build logs in the Space
   - Check for errors in **Logs** tab
   - Wait for "Running" status

---

## 📊 Expected Performance

**First Build Time:** 10-15 minutes (downloading models)
**Subsequent Builds:** 2-3 minutes (cached)
**App Startup:** 30-60 seconds first time, instant after
**Hardware:** CPU basic (free tier) is sufficient

---

## 🐛 Troubleshooting

### Build fails with "Out of disk space"

**Solution:** Use HuggingFace Spaces persistent storage

Add to your Space settings:
```
Settings → Storage → Enable persistent storage
```

### spaCy model not found

**Solution:** Add to `streamlit_app.py` (already included):

```python
def ensure_spacy_model():
    import subprocess
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
```

### Models downloading every time

**Solution:** Enable persistent storage (see above)

### Build timeout

**Solution:** Reduce requirements or upgrade to better hardware tier

---

## 💰 Cost

**Free Tier:**
- ✅ Unlimited public Spaces
- ✅ CPU basic hardware
- ✅ Community support
- ✅ Perfect for ClearCraft

**Pro Tier ($9/month):**
- More powerful hardware
- Faster builds
- Private Spaces
- **Not needed for ClearCraft**

---

## 🔄 Updates

To update your deployed Space:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push hf claude/clearcraft-humanizer-app-011CUvktJ3WqTF1d715kpMAg:main
```

HuggingFace automatically rebuilds and redeploys!

---

## 🌐 Share Your Space

Your app will be available at:
```
https://huggingface.co/spaces/YOUR_USERNAME/clearcraft
```

You can:
- Share the URL directly
- Embed the Space in websites (iframes)
- Add it to HuggingFace collections
- Link from your GitHub README

---

## 📝 Alternative: Deploy from GitHub Mirror

If you want automatic syncing:

1. **Fork the repo** on GitHub
2. **In HuggingFace Space Settings:**
   - Go to **Settings** → **Linked Repositories**
   - Connect your GitHub repo
   - Enable auto-sync

Now every push to GitHub automatically deploys to HuggingFace!

---

## ✅ Deployment Checklist

- [ ] HuggingFace account created
- [ ] New Space created (SDK: Streamlit)
- [ ] Repository connected (git push or upload)
- [ ] README.md with frontmatter added
- [ ] requirements.txt verified
- [ ] Build completed successfully
- [ ] App running and accessible
- [ ] DeepInfra API key added (optional)
- [ ] Tested all features:
  - [ ] Text analysis
  - [ ] Text rewriting
  - [ ] DeepInfra LLM (if enabled)
  - [ ] Download functionality

---

## 🎉 Success!

Once deployed, your app will be live at:
```
https://huggingface.co/spaces/YOUR_USERNAME/clearcraft
```

**Advantages over Streamlit Cloud:**
- ✅ Handles large ML models
- ✅ Better free tier resources
- ✅ Designed for AI apps
- ✅ Automatic GPU access (if needed)
- ✅ Better caching
- ✅ Community features

---

## 📚 Resources

- [HuggingFace Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Streamlit on Spaces Guide](https://huggingface.co/docs/hub/spaces-sdks-streamlit)
- [HuggingFace CLI](https://huggingface.co/docs/huggingface_hub/quick-start)
- [ClearCraft Documentation](README.md)

---

**Last Updated:** 2025-01-08
**Recommended Platform:** HuggingFace Spaces
**Status:** Production Ready with Full ML Support
