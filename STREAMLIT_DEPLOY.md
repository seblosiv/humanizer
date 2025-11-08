# ClearCraft Streamlit Deployment Guide

Quick guide to deploying ClearCraft on Streamlit Cloud.

---

## 🚀 Quick Deploy

### Prerequisites

1. GitHub account with repository access
2. Streamlit Cloud account (free at https://streamlit.io/cloud)
3. Repository connected to Streamlit Cloud

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Streamlit deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Set main file path: `streamlit_app.py`
   - Click "Deploy"

3. **Wait for Deployment**
   - First deployment takes 5-10 minutes
   - Models will be downloaded automatically
   - App will be available at: `https://[your-app].streamlit.app`

---

## 📁 Required Files

### streamlit_app.py
Main Streamlit application (already created).

### .streamlit/config.toml
Streamlit configuration (already created):
- Theme settings
- Server configuration
- Browser settings

### requirements.txt
Python dependencies (already updated):
- Includes all ClearCraft dependencies
- Includes streamlit>=1.29.0

### packages.txt
System dependencies (already created):
- python3-dev
- build-essential

---

## 🔧 Configuration

### Environment Variables

If using DeepInfra (optional LLM):

1. In Streamlit Cloud dashboard
2. Go to App settings → Secrets
3. Add:
   ```toml
   DEEPINFRA_API_TOKEN = "your-token-here"
   ```

**Note:** Free Streamlit deployment uses deterministic mode only (no LLM) to conserve resources.

---

## 🎯 Features Available

**Included:**
- ✅ Text analysis with readability metrics
- ✅ Deterministic rewriting (7 enhancement modules)
- ✅ Semantic similarity checking
- ✅ Citation preservation
- ✅ Quality guardrails
- ✅ Download improved text

**Not Included (Optional):**
- ❌ DeepInfra LLM mode (requires API key and costs money)

---

## 📊 Performance

**Expected:**
- First run: 30-60 seconds (model download)
- Subsequent runs: Instant startup
- Analysis: 1-3 seconds per request
- Rewriting: 5-30 seconds depending on text length

**Resource Limits (Streamlit Free Tier):**
- 1 GB RAM
- Shared CPU
- Apps sleep after 7 days of inactivity

---

## 🐛 Troubleshooting

### "App is taking too long to load"
- Normal on first deployment
- Models are being downloaded
- Wait 5-10 minutes

### "Out of memory" errors
- Reduce MAX_TEXT_LENGTH in config
- Use smaller model (already configured)
- Upgrade to Streamlit Teams plan

### "ModuleNotFoundError"
- Check requirements.txt includes all dependencies
- Redeploy from Streamlit dashboard

### Spacy model not found
- Auto-download is configured in streamlit_app.py
- Should download automatically on first run
- Check logs in Streamlit Cloud dashboard

---

## 🔐 Security Notes

**Public Deployment:**
- No authentication by default
- Don't process sensitive data
- Consider rate limiting if abuse occurs
- Users can see source code (public repo)

**Private Deployment:**
- Make GitHub repo private
- Share only with specific users
- Consider Streamlit Teams for access control

---

## 📈 Monitoring

### View Logs
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. View logs in real-time

### Usage Analytics
- Streamlit Cloud provides basic analytics
- Track active users, requests
- Monitor resource usage

---

## 🔄 Updates

### Deploy Updates
```bash
# Make changes
git add .
git commit -m "Update description"
git push origin main

# Streamlit Cloud auto-deploys from main branch
```

### Manual Redeploy
1. Go to Streamlit Cloud dashboard
2. Click "Reboot app"
3. Wait for redeploy

---

## 💰 Cost

**Free Tier:**
- Unlimited public apps
- 1 GB RAM per app
- Community support

**Streamlit Teams ($250/month):**
- Private apps
- 4 GB RAM per app
- Custom domains
- Priority support
- SSO authentication

**For ClearCraft:** Free tier is sufficient for demonstration and light usage.

---

## 📚 Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [ClearCraft Documentation](README.md)

---

## ✅ Deployment Checklist

- [ ] streamlit_app.py created
- [ ] .streamlit/config.toml configured
- [ ] requirements.txt includes streamlit
- [ ] packages.txt created
- [ ] Code pushed to GitHub
- [ ] Streamlit Cloud account connected
- [ ] App deployed successfully
- [ ] Models download automatically
- [ ] Test analysis feature
- [ ] Test rewriting feature
- [ ] Share public URL

---

## 🎉 Success!

Once deployed, your app will be available at:
```
https://[your-app-name]-[random-hash].streamlit.app
```

Share this URL with users!

---

**Last Updated:** 2025-01-08
**Version:** 1.0.0
