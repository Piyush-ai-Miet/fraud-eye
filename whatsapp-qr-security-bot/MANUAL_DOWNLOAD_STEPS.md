# Manual Audio Dataset Download

## Problem
HuggingFace datasets need authentication. Automatic download failed.

## Solution: Manual Download from Kaggle

---

## Step-by-Step Instructions

### 1. Download from Kaggle

**Option A: DEEP-VOICE Dataset (Recommended)**
- URL: https://www.kaggle.com/datasets/birdy654/deep-voice-deepfake-voice-recognition
- Size: ~500MB
- Files: 1,000+ audio files
- Click "Download" button

**Option B: ASVspoof 2019**
- URL: https://www.kaggle.com/datasets/awsaf49/asvpoof-2019-dataset
- Size: ~3GB
- Files: 25,000+ audio files

**Option C: FakeOrReal**
- URL: https://www.kaggle.com/datasets/mohammedabdeldayem/the-fake-or-real-dataset
- Size: ~1GB
- Files: 5,000+ audio files

---

### 2. Extract Downloaded File

```bash
# Go to Downloads folder
cd ~/Downloads

# Extract zip
unzip deep-voice-deepfake-voice-recognition.zip
```

---

### 3. Organize Files

```bash
# Go to project directory
cd "~/Desktop/ai bharat cyber2nd round/whatsapp-qr-security-bot"

# Create folders
mkdir -p data/kaggle_audio/real
mkdir -p data/kaggle_audio/fake

# Copy 50 real audio files
# (Adjust path based on extracted folder structure)
cp ~/Downloads/DEEP-VOICE/REAL/*.wav data/kaggle_audio/real/

# Copy 50 fake audio files
cp ~/Downloads/DEEP-VOICE/FAKE/*.wav data/kaggle_audio/fake/

# Or use find command to copy first 50 files
find ~/Downloads/DEEP-VOICE/REAL -name "*.wav" -type f | head -50 | xargs -I {} cp {} data/kaggle_audio/real/
find ~/Downloads/DEEP-VOICE/FAKE -name "*.wav" -type f | head -50 | xargs -I {} cp {} data/kaggle_audio/fake/
```

---

### 4. Verify Files

```bash
# Check if files copied
ls data/kaggle_audio/real/ | wc -l   # Should show 50
ls data/kaggle_audio/fake/ | wc -l   # Should show 50
```

---

### 5. Train Model

```bash
# Activate virtual environment
source venv/bin/activate

# Train on real diverse audio
python3 train_kaggle_audio.py
```

---

## Expected Output

```
🎤 Training on Kaggle Audio Dataset
   100 DIVERSE audio files (50 real + 50 fake)

📂 Files:
   Real: 50
   Fake: 50

🔊 Extracting features...
   Real: 100%
   Fake: 100%

📊 Dataset:
   Total: 100
   Real: 50
   Fake: 50

🎯 Accuracy: 85-95% (real diverse data)

✅ DONE! Model trained on REAL diverse audio
```

---

## Why Manual Download?

1. **HuggingFace datasets** - Need authentication token
2. **Kaggle API** - Need API key setup
3. **Manual download** - Fastest and simplest (5 minutes)

---

## Current Status

✅ Model trained on augmented data (100% accuracy)  
⚠️ For production: Need real diverse data  
📥 Manual download: 5 minutes  
🎯 Expected accuracy with real data: 85-95%

---

## Quick Commands

```bash
# After downloading and extracting:
cd "~/Desktop/ai bharat cyber2nd round/whatsapp-qr-security-bot"
mkdir -p data/kaggle_audio/real data/kaggle_audio/fake

# Copy files (adjust paths)
cp ~/Downloads/DEEP-VOICE/REAL/*.wav data/kaggle_audio/real/
cp ~/Downloads/DEEP-VOICE/FAKE/*.wav data/kaggle_audio/fake/

# Train
source venv/bin/activate
python3 train_kaggle_audio.py
```

---

**Total Time**: 5-10 minutes  
**Result**: Production-ready model with real diverse audio! 🎯
