"""
Download Audio Deepfake Dataset from Kaggle
Dataset: Real vs Fake Audio for fraud/scam detection
"""
import os
import sys

print("="*70)
print("Audio Deepfake Dataset Downloader")
print("="*70)
print("\n📦 Available Datasets:")
print("\n1. ASVspoof 2019 (Official)")
print("   - 25,380 real audio samples")
print("   - 22,800 fake audio samples")
print("   - Download: http://www.asvspoof.org/")
print("   - Registration required")

print("\n2. In-the-Wild Dataset")
print("   - 20.8 hours real audio")
print("   - 17.2 hours fake audio")
print("   - 58 celebrities/politicians")
print("   - Download: https://deepfake-total.com/in_the_wild")

print("\n3. FakeOrReal Dataset (Kaggle)")
print("   - Balanced real/fake samples")
print("   - Multiple languages")
print("   - Easy to download")

print("\n4. For-2-seconds Dataset (Kaggle)")
print("   - Short audio clips")
print("   - Real vs AI-generated")

print("\n" + "="*70)
print("RECOMMENDED: Use Kaggle API for easy download")
print("="*70)

print("\n📝 Setup Instructions:")
print("\n1. Install Kaggle API:")
print("   pip install kaggle")

print("\n2. Get Kaggle API credentials:")
print("   - Go to https://www.kaggle.com/settings")
print("   - Click 'Create New API Token'")
print("   - Save kaggle.json to ~/.kaggle/")

print("\n3. Download dataset:")
print("   kaggle datasets download -d <dataset-name>")

print("\n" + "="*70)
print("MANUAL DOWNLOAD OPTION")
print("="*70)

print("\nIf you have audio files already:")
print("1. Create folders:")
print("   mkdir -p data/audio/real")
print("   mkdir -p data/audio/fake")

print("\n2. Put your audio files:")
print("   - Real audio → data/audio/real/")
print("   - Fake/AI audio → data/audio/fake/")

print("\n3. Supported formats: .wav, .mp3, .flac, .ogg")

print("\n" + "="*70)
print("EXAMPLE: Download using Kaggle API")
print("="*70)

print("\n# For ASVspoof-like dataset:")
print("kaggle datasets download -d awsaf49/asvpoof-2019-dataset")

print("\n# For general deepfake audio:")
print("kaggle datasets download -d birinder1469/audiomnist")

print("\n" + "="*70)

# Check if kaggle is installed
try:
    import kaggle
    print("\n✅ Kaggle API is installed")
    print("\nTo download a dataset, run:")
    print("  python download_audio_dataset.py <dataset-name>")
except ImportError:
    print("\n⚠️ Kaggle API not installed")
    print("Install with: pip install kaggle")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)
print("\n1. Download dataset (manual or Kaggle API)")
print("2. Extract to data/audio/ folder")
print("3. Run: python train_audio_fraud_model.py")
print("4. Model will be saved to models/")
print("\n" + "="*70)
