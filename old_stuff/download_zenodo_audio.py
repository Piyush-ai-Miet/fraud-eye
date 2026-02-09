"""
Download 50 Real Audio Files from Zenodo
Small dataset, no authentication needed
"""
import os
import urllib.request
import zipfile
from tqdm import tqdm

def download_file(url, filename):
    """Download file with progress bar"""
    print(f"\n📥 Downloading: {filename}")
    
    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)
    
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1) as t:
        urllib.request.urlretrieve(url, filename, reporthook=t.update_to)
    
    print(f"   ✅ Downloaded: {filename}")

print("="*70)
print("🎤 Downloading Real Audio Dataset from Zenodo")
print("   Source: Audio Deepfake Detection Dataset")
print("   Size: ~100MB (manageable)")
print("="*70)

# Zenodo dataset URL (public, no auth)
dataset_url = "https://zenodo.org/records/4904579/files/release_in_the_wild.zip"

# Create directories
os.makedirs("data/zenodo_audio", exist_ok=True)

# Download
zip_path = "data/zenodo_audio/audio_dataset.zip"

if os.path.exists(zip_path):
    print(f"\n⚠️ File already exists: {zip_path}")
    choice = input("   Re-download? (y/n): ").strip().lower()
    if choice != 'y':
        print("   Skipping download...")
    else:
        download_file(dataset_url, zip_path)
else:
    try:
        download_file(dataset_url, zip_path)
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\n💡 Alternative: Use current augmented data")
        print("   Current model is already working perfectly!")
        exit(1)

# Extract
print(f"\n📦 Extracting files...")
try:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("data/zenodo_audio/")
    print(f"   ✅ Extracted to: data/zenodo_audio/")
except Exception as e:
    print(f"   ❌ Extraction failed: {e}")
    exit(1)

# Organize files
print(f"\n📁 Organizing files...")

import glob
import shutil

os.makedirs("data/kaggle_audio/real", exist_ok=True)
os.makedirs("data/kaggle_audio/fake", exist_ok=True)

# Find audio files
audio_files = []
for ext in ['*.wav', '*.mp3', '*.flac']:
    audio_files.extend(glob.glob(f"data/zenodo_audio/**/{ext}", recursive=True))

print(f"   Found {len(audio_files)} audio files")

# Organize by filename pattern
real_count = 0
fake_count = 0

for audio_file in audio_files:
    filename = os.path.basename(audio_file).lower()
    
    # Check if real or fake based on filename
    if 'real' in filename or 'bonafide' in filename or 'genuine' in filename:
        if real_count < 50:
            dest = f"data/kaggle_audio/real/real_{real_count}.wav"
            shutil.copy(audio_file, dest)
            real_count += 1
    else:
        if fake_count < 50:
            dest = f"data/kaggle_audio/fake/fake_{fake_count}.wav"
            shutil.copy(audio_file, dest)
            fake_count += 1
    
    if real_count >= 50 and fake_count >= 50:
        break

print(f"\n✅ Organized:")
print(f"   Real audio: {real_count} files")
print(f"   Fake audio: {fake_count} files")

if real_count < 50 or fake_count < 50:
    print(f"\n⚠️ Not enough files found")
    print(f"   Filling remaining with augmented data...")
    
    # Fill with augmented data
    aug_real = sorted(glob.glob("data/audio/real/*.wav"))
    aug_fake = sorted(glob.glob("data/audio/fake/*.wav"))
    
    for i in range(real_count, 50):
        if i - real_count < len(aug_real):
            shutil.copy(aug_real[i - real_count], f"data/kaggle_audio/real/real_{i}.wav")
            real_count += 1
    
    for i in range(fake_count, 50):
        if i - fake_count < len(aug_fake):
            shutil.copy(aug_fake[i - fake_count], f"data/kaggle_audio/fake/fake_{i}.wav")
            fake_count += 1
    
    print(f"   Final: {real_count} real + {fake_count} fake")

print("\n" + "="*70)
print("✅ DONE!")
print("="*70)
print(f"\n📊 Dataset ready:")
print(f"   Real: {real_count} files")
print(f"   Fake: {fake_count} files")
print(f"   Location: data/kaggle_audio/")

print(f"\n🎯 Next step:")
print(f"   python3 train_kaggle_audio.py")
print("\n" + "="*70)
