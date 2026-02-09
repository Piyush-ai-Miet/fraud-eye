"""
Download Real Audio Deepfake Dataset
Using Zenodo dataset (88,600 audio clips)
"""
import os
import requests
from tqdm import tqdm
import zipfile

def download_file(url, output_path):
    """Download file with progress bar"""
    print(f"\n📥 Downloading from: {url}")
    print(f"   Saving to: {output_path}")
    
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(output_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    
    print(f"   ✅ Downloaded: {output_path}")

def download_zenodo_dataset():
    """
    Download Zenodo audio deepfake dataset
    88,600 audio clips (16-bit PCM wav)
    """
    print("="*70)
    print("🎤 Downloading Real Audio Deepfake Dataset")
    print("   Source: Zenodo (88,600 audio clips)")
    print("="*70)
    
    # Zenodo dataset URL
    # https://zenodo.org/records/4904579
    dataset_url = "https://zenodo.org/records/4904579/files/release_in_the_wild.zip"
    
    # Create data directory
    os.makedirs("data/audio_dataset", exist_ok=True)
    
    # Download
    zip_path = "data/audio_dataset/in_the_wild.zip"
    
    if os.path.exists(zip_path):
        print(f"\n⚠️ File already exists: {zip_path}")
        choice = input("   Re-download? (y/n): ").strip().lower()
        if choice != 'y':
            print("   Skipping download...")
            return zip_path
    
    try:
        download_file(dataset_url, zip_path)
        return zip_path
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        print("\n💡 Manual download:")
        print(f"   1. Visit: https://zenodo.org/records/4904579")
        print(f"   2. Download: release_in_the_wild.zip")
        print(f"   3. Save to: {zip_path}")
        return None

def extract_dataset(zip_path):
    """Extract dataset"""
    print(f"\n📦 Extracting dataset...")
    
    extract_dir = "data/audio_dataset/in_the_wild"
    
    if os.path.exists(extract_dir):
        print(f"   ⚠️ Directory already exists: {extract_dir}")
        choice = input("   Re-extract? (y/n): ").strip().lower()
        if choice != 'y':
            print("   Skipping extraction...")
            return extract_dir
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"   ✅ Extracted to: {extract_dir}")
        return extract_dir
    except Exception as e:
        print(f"   ❌ Extraction failed: {e}")
        return None

def organize_dataset(extract_dir):
    """
    Organize dataset into real/fake folders
    """
    print(f"\n📁 Organizing dataset...")
    
    # Create folders
    real_dir = "data/audio/real"
    fake_dir = "data/audio/fake"
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)
    
    # Count files
    import glob
    
    # Find all audio files
    audio_files = []
    for ext in ['*.wav', '*.mp3', '*.flac']:
        audio_files.extend(glob.glob(os.path.join(extract_dir, '**', ext), recursive=True))
    
    print(f"   Found {len(audio_files)} audio files")
    
    # Organize by filename pattern
    # In-the-Wild dataset has 'real' and 'fake' in filenames
    real_count = 0
    fake_count = 0
    
    for audio_file in tqdm(audio_files[:1000], desc="   Organizing"):  # Limit to 1000 files
        filename = os.path.basename(audio_file)
        
        # Check if real or fake
        if 'real' in filename.lower() or 'bonafide' in filename.lower():
            # Copy to real folder
            dest = os.path.join(real_dir, filename)
            if not os.path.exists(dest):
                os.system(f'cp "{audio_file}" "{dest}"')
                real_count += 1
        else:
            # Copy to fake folder
            dest = os.path.join(fake_dir, filename)
            if not os.path.exists(dest):
                os.system(f'cp "{audio_file}" "{dest}"')
                fake_count += 1
    
    print(f"\n   ✅ Organized:")
    print(f"      Real audio: {real_count} files → {real_dir}")
    print(f"      Fake audio: {fake_count} files → {fake_dir}")
    
    return real_count, fake_count

def main():
    print("\n🎤 Real Audio Deepfake Dataset Downloader")
    print("   For training production-ready model")
    print("\n" + "="*70)
    
    # Option 1: Zenodo dataset (recommended)
    print("\n📊 Dataset Options:")
    print("   1. Zenodo In-the-Wild (88,600 clips) - RECOMMENDED")
    print("   2. Manual download (provide your own dataset)")
    
    choice = input("\nSelect option (1/2): ").strip()
    
    if choice == '1':
        # Download Zenodo dataset
        zip_path = download_zenodo_dataset()
        
        if zip_path and os.path.exists(zip_path):
            # Extract
            extract_dir = extract_dataset(zip_path)
            
            if extract_dir:
                # Organize
                real_count, fake_count = organize_dataset(extract_dir)
                
                print("\n" + "="*70)
                print("✅ DATASET READY")
                print("="*70)
                print(f"\n📊 Summary:")
                print(f"   Real audio: {real_count} files")
                print(f"   Fake audio: {fake_count} files")
                print(f"   Total: {real_count + fake_count} files")
                
                print(f"\n🎯 Next step:")
                print(f"   python3 train_audio_fraud_model.py")
                print(f"   Choose 'y' to use real audio files")
                
    elif choice == '2':
        print("\n📝 Manual Download Instructions:")
        print("   1. Download audio dataset from:")
        print("      - Zenodo: https://zenodo.org/records/4904579")
        print("      - ASVspoof: http://www.asvspoof.org/")
        print("      - In-the-Wild: https://deepfake-total.com/in_the_wild")
        print("\n   2. Organize files:")
        print("      data/audio/real/*.wav (real audio)")
        print("      data/audio/fake/*.wav (fake audio)")
        print("\n   3. Train model:")
        print("      python3 train_audio_fraud_model.py")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
