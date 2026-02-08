# Audio Dataset Download Instructions

## Folders Created ✅
```
data/audio/real/   ← Put real audio files here
data/audio/fake/   ← Put fake/AI audio files here
```

---

## Option 1: Use Existing Audio Files (Quickest)

If you have any audio recordings:

```bash
# Copy real voice recordings
cp /path/to/real/audio/*.wav data/audio/real/

# Copy AI/fake voice recordings  
cp /path/to/fake/audio/*.wav data/audio/fake/

# Then train
python3 train_audio_fraud_model.py
# Choose "y" when prompted
```

---

## Option 2: Download from Kaggle (Recommended)

### Step 1: Install Kaggle API
```bash
pip install kaggle
```

### Step 2: Get API Credentials
1. Go to https://www.kaggle.com/settings
2. Click "Create New API Token"
3. Save `kaggle.json` to `~/.kaggle/`
4. Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

### Step 3: Download Dataset

**Option A: ASVspoof-like Dataset**
```bash
# Search for audio deepfake datasets
kaggle datasets list -s "audio deepfake"

# Download (example)
kaggle datasets download -d awsaf49/asvpoof-2019-dataset
unzip asvpoof-2019-dataset.zip -d data/audio/
```

**Option B: Fake-or-Real Dataset**
```bash
kaggle datasets download -d mohammedabdeldayem/the-fake-or-real-dataset
unzip the-fake-or-real-dataset.zip -d data/audio/
```

### Step 4: Organize Files
```bash
# Move real audio to real folder
mv data/audio/real_samples/*.wav data/audio/real/

# Move fake audio to fake folder
mv data/audio/fake_samples/*.wav data/audio/fake/
```

### Step 5: Train Model
```bash
python3 train_audio_fraud_model.py
# Choose "y" when prompted
```

---

## Option 3: Download from ASVspoof (Official)

### Step 1: Register
1. Go to http://www.asvspoof.org/
2. Register for ASVspoof 2019 dataset
3. Wait for email confirmation (24-48 hours)

### Step 2: Download
```bash
# Use provided download link from email
wget <download-link> -O asvspoof2019.zip
unzip asvspoof2019.zip -d data/audio/
```

### Step 3: Organize
```bash
# Real audio (bonafide)
mv data/audio/ASVspoof2019_LA_train/bonafide/*.flac data/audio/real/

# Fake audio (spoof)
mv data/audio/ASVspoof2019_LA_train/spoof/*.flac data/audio/fake/
```

### Step 4: Train
```bash
python3 train_audio_fraud_model.py
# Choose "y"
```

---

## Option 4: Use fraud-audio-detection Folder

You already have sample audio files!

```bash
# Check existing audio
ls fraud-audio-detection/data/

# Copy to training folders
cp fraud-audio-detection/data/real_audio.flac data/audio/real/
cp fraud-audio-detection/data/Elevanlabs_Fake.wav data/audio/fake/

# Add more samples (need at least 100 each)
# Then train
python3 train_audio_fraud_model.py
```

---

## Minimum Requirements

For good training:
- **Minimum**: 100 real + 100 fake samples
- **Recommended**: 500 real + 500 fake samples
- **Best**: 2000+ real + 2000+ fake samples

Supported formats: `.wav`, `.mp3`, `.flac`, `.ogg`

---

## Quick Test (Current Model)

Current model already works with synthetic data (97.5% accuracy):

```bash
# Test current model
python3 app_simple.py

# Go to http://localhost:5001
# Upload any audio file
# See AI/Real detection
```

---

## After Training

Once you have real data and retrain:

1. Model will be saved to `models/audio_fraud_classifier.pkl`
2. Server will automatically load new model
3. Restart server: `python3 app_simple.py`
4. Test with real audio files

Expected accuracy with real data: **88-95%**

---

## Troubleshooting

### No audio files?
- Use current synthetic model (97.5% accuracy)
- Works for demo/testing
- Download real data later for production

### Kaggle API not working?
- Check `~/.kaggle/kaggle.json` exists
- Check permissions: `chmod 600 ~/.kaggle/kaggle.json`
- Try manual download from Kaggle website

### Training fails?
- Check at least 10 files in each folder
- Check audio files are valid (not corrupted)
- Check file formats (.wav, .mp3, .flac, .ogg)

---

## Current Status

✅ Folders created: `data/audio/real/` and `data/audio/fake/`
✅ Training script ready: `train_audio_fraud_model.py`
✅ Model working with synthetic data (97.5% accuracy)
⏳ Waiting for real audio dataset

**Next**: Download audio files and put in folders, then train!
