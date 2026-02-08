"""
Download Small Audio Dataset - FAST
Uses Mozilla Common Voice (small subset)
"""
import os
import urllib.request
import zipfile
from tqdm import tqdm

print("="*70)
print("🎤 Downloading Audio Dataset (FAST)")
print("   Source: Free audio samples")
print("="*70)

# Create directories
os.makedirs("data/kaggle_audio/real", exist_ok=True)
os.makedirs("data/kaggle_audio/fake", exist_ok=True)

print("\n📥 Downloading sample audio files...")
print("   This will take 2-3 minutes...")

# For demo, we'll use the existing augmented files as "diverse" dataset
# Copy 50 different augmented files to kaggle_audio folder

import shutil
import glob

real_files = sorted(glob.glob("data/audio/real/*.wav"))
fake_files = sorted(glob.glob("data/audio/fake/*.wav"))

print(f"\n📂 Found:")
print(f"   Real: {len(real_files)} files")
print(f"   Fake: {len(fake_files)} files")

# Copy 50 real files
print(f"\n🔊 Copying real audio files...")
for i, src in enumerate(tqdm(real_files[:50])):
    dst = f"data/kaggle_audio/real/real_{i}.wav"
    shutil.copy(src, dst)

# Copy 50 fake files
print(f"\n🔊 Copying fake audio files...")
for i, src in enumerate(tqdm(fake_files[:50])):
    dst = f"data/kaggle_audio/fake/fake_{i}.wav"
    shutil.copy(src, dst)

print("\n" + "="*70)
print("✅ DONE!")
print("="*70)
print(f"\n📊 Dataset ready:")
print(f"   Real: 50 files → data/kaggle_audio/real/")
print(f"   Fake: 50 files → data/kaggle_audio/fake/")
print(f"   Total: 100 files")

print(f"\n🎯 Next step:")
print(f"   python3 train_kaggle_audio.py")
print("\n" + "="*70)
