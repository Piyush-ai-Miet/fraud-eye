# Render Deployment Settings for Fraud Eye

## ✅ Repository Configuration

### Public Repo (for testing)
- **URL**: `https://github.com/Piyush-ai-Miet/fraud-eye`
- **Branch**: `main`

### Private Repo (production - currently linked to Render)
- **URL**: `https://github.com/Piyush-ai-Miet/fraud-eye-private`
- **Branch**: `main`

---

## 🚀 Render Service Settings

### Basic Settings
- **Repository**: Choose either public or private repo above
- **Branch**: `main`
- **Root Directory**: `fraud-eye-app`
- **Runtime**: Python (auto-detected from runtime.txt)

### Build & Deploy Commands
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app_simple:app`

### Environment Variables
**No environment variables needed!** VirusTotal API key is already in the code:
```python
VIRUSTOTAL_API_KEY = "847b72227574d01600c6e59bf0bd7d6e66a822b4b119bcdaa8a0acaf8d4839aa"
```

---

## 🔧 Recent Fixes Applied

### 1. Python Version Fix
- **File**: `fraud-eye-app/runtime.txt`
- **Content**: `python-3.11.9`
- **Reason**: Python 3.13 incompatible with scikit-learn 1.3.2
- **Status**: ✅ Committed and pushed to both repos

### 2. NumPy Version Fix
- **File**: `fraud-eye-app/requirements.txt`
- **Change**: `numpy>=1.24.0,<2.0`
- **Reason**: scikit-learn 1.3.2 requires numpy<2.0
- **Status**: ✅ Already committed

### 3. ML Models
- **Location**: `fraud-eye-app/models/`
- **Files**:
  - `audio_fraud_classifier.pkl` (Audio detection)
  - `url_classifier_kaggle_enhanced.pkl` (URL detection)
  - Feature name files (.pkl)
- **Status**: ✅ All committed to private repo

---

## 📋 Deployment Steps

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Create New Web Service** (or update existing)
3. **Connect Repository**: 
   - For testing: `fraud-eye` (public)
   - For production: `fraud-eye-private`
4. **Configure Settings**:
   - Root Directory: `fraud-eye-app`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app_simple:app`
5. **Deploy**: Click "Create Web Service" or "Manual Deploy"

---

## 🔍 Monitoring Deployment

### Check Build Logs
- Watch for: `✅ Successfully loaded ML model`
- Watch for: `✅ Audio classifier model loaded`
- Watch for: `Listening on http://0.0.0.0:10000`

### Test Endpoints After Deployment
1. **Homepage**: `https://your-app.onrender.com/`
2. **Scanner**: `https://your-app.onrender.com/scanner`
3. **Voice Detection**: Test audio upload at scanner page
4. **URL Check**: Test URL scanning at scanner page

---

## ⚠️ Expected Behavior

### ML Models Status
- **URL Classifier**: Should load successfully
- **Audio Classifier**: Should load successfully
- **Pattern Detector**: Should load successfully

### If ML Models Don't Load
- Check build logs for numpy/scikit-learn errors
- Verify Python version is 3.11.9 (not 3.13)
- Verify numpy version is <2.0

---

## 🎯 Current Status

- ✅ `runtime.txt` created with Python 3.11.9
- ✅ `requirements.txt` updated with numpy<2.0
- ✅ Both repos synced (public + private)
- ✅ ML models committed to private repo
- ✅ VirusTotal API key in code (no env var needed)
- ⏳ **NEXT**: Deploy on Render and test

---

## 📞 Support

If deployment fails:
1. Check Render build logs
2. Look for Python version (should be 3.11.9)
3. Look for numpy version (should be <2.0)
4. Check if ML models are loading
5. Test locally first: `cd fraud-eye-app && python app_simple.py`
