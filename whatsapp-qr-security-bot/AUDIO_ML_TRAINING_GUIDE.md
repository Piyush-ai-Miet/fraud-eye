# Audio Fraud Detection - ML Training Guide

## Overview
Scikit-learn based ML model to detect:
- AI-generated voices
- Deepfake audio
- Scam calls
- Fraudulent voice messages

Target: Indian Tier 2/3 communities

## Current Status
✅ Model trained with synthetic data (100% accuracy)
✅ 38 audio features extracted (MFCC, Spectral, etc.)
✅ Random Forest classifier (100 trees)
✅ Model saved to `models/audio_fraud_classifier.pkl`

## Features Extracted
1. **MFCC** (Mel-frequency cepstral coefficients) - 13 mean + 13 std
2. **Spectral Centroid** - mean + std
3. **Spectral Rolloff** - mean + std
4. **Zero Crossing Rate** - mean + std
5. **Spectral Bandwidth** - mean + std
6. **RMS Energy** - mean + std
7. **Chroma Features** - mean + std

**Total: 38 features per audio sample**

## Training Results (Synthetic Data)
- **Accuracy**: 100%
- **Dataset**: 200 samples (100 real, 100 fake)
- **Train/Test Split**: 80/20
- **Model**: Random Forest (100 estimators, max_depth=10)

## Top Important Features
1. Spectral Rolloff (std) - 14.88%
2. MFCC std_9 - 9.58%
3. Spectral Rolloff (mean) - 7.93%
4. Spectral Bandwidth (std) - 7.20%
5. MFCC std_10 - 6.54%

## How to Use Real Datasets

### Option 1: Download from Kaggle
```bash
# Install Kaggle API
pip install kaggle

# Setup credentials
# 1. Go to https://www.kaggle.com/settings
# 2. Click "Create New API Token"
# 3. Save kaggle.json to ~/.kaggle/

# Download dataset (example)
kaggle datasets download -d awsaf49/asvpoof-2019-dataset
```

### Option 2: Manual Dataset
```bash
# Create folders
mkdir -p data/audio/real
mkdir -p data/audio/fake

# Add your audio files
# - Real audio → data/audio/real/
# - Fake/AI audio → data/audio/fake/

# Supported formats: .wav, .mp3, .flac, .ogg
```

### Option 3: Recommended Datasets
1. **ASVspoof 2019** (Official)
   - 25,380 real + 22,800 fake samples
   - Download: http://www.asvspoof.org/
   - Registration required

2. **In-the-Wild Dataset**
   - 20.8 hours real + 17.2 hours fake
   - 58 celebrities/politicians
   - Download: https://deepfake-total.com/in_the_wild

3. **FakeOrReal Dataset** (Kaggle)
   - Balanced real/fake samples
   - Multiple languages
   - Easy to download

## Training with Real Data

```bash
# 1. Download and extract dataset to data/audio/
# 2. Run training script
python3 train_audio_fraud_model.py

# 3. Choose "y" when prompted for real audio files
Use real audio files? (y/n): y

# 4. Model will be saved to models/audio_fraud_classifier.pkl
```

## Integration Status
- ✅ Model training script created
- ✅ Audio classifier wrapper created
- ✅ Feature extraction implemented
- ⏳ Integration into app_simple.py (pending)
- ⏳ Web interface testing (pending)

## Next Steps
1. Download real audio dataset from Kaggle/ASVspoof
2. Retrain model with real data
3. Integrate into Flask app
4. Test with real scam call recordings
5. Deploy to production

## Files Created
- `train_audio_fraud_model.py` - Training script
- `audio_fraud_classifier.py` - Classifier wrapper
- `download_audio_dataset.py` - Dataset download guide
- `models/audio_fraud_classifier.pkl` - Trained model
- `models/audio_feature_names.pkl` - Feature names

## Dependencies
```
librosa==0.11.0
scikit-learn==1.3.2
soundfile==0.12.1
numpy>=1.22.0
scipy>=1.6.0
```

## Usage Example
```python
from audio_fraud_classifier import audio_classifier

# Predict audio file
result = audio_classifier.predict('test_audio.wav')

print(result)
# {
#     'is_fake': False,
#     'is_real': True,
#     'confidence': 0.85,
#     'label': 'Real',
#     'probability_real': 0.85,
#     'probability_fake': 0.15
# }
```

## Performance Notes
- Synthetic data: 100% accuracy (demo only)
- Real data: Expected 85-95% accuracy
- Processing time: ~1-2 seconds per audio file
- Works without GPU (CPU only)

## For Production
1. Use real datasets (ASVspoof, In-the-Wild, etc.)
2. Collect Indian scam call recordings
3. Add data augmentation (noise, pitch shift, etc.)
4. Increase training samples (1000+ each class)
5. Cross-validation for better generalization
6. Regular model updates with new scam patterns

---
**Created**: February 6, 2026
**Status**: Demo model ready, awaiting real dataset
