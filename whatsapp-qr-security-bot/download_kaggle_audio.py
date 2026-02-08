"""
Download Audio Dataset from HuggingFace
Extract 100 files (50 real + 50 fake) and train ML model
"""
import os
import sys

print("="*70)
print("🎤 Kaggle Audio Dataset Downloader")
print("   Source: HuggingFace Deepfake-Eval-2024")
print("="*70)

# Check if datasets library is installed
try:
    from datasets import load_dataset
    print("\n✅ HuggingFace datasets library found")
except ImportError:
    print("\n❌ HuggingFace datasets library not found")
    print("\n📦 Installing...")
    os.system("pip install datasets")
    from datasets import load_dataset

print("\n📥 Downloading dataset from HuggingFace...")
print("   Dataset: nuriachandra/Deepfake-Eval-2024")
print("   This may take 5-10 minutes...")

try:
    # Load dataset
    dataset = load_dataset("nuriachandra/Deepfake-Eval-2024", split="train", streaming=True)
    
    print("\n✅ Dataset loaded (streaming mode)")
    
    # Create directories
    os.makedirs("data/kaggle_audio/real", exist_ok=True)
    os.makedirs("data/kaggle_audio/fake", exist_ok=True)
    
    print("\n🔊 Extracting audio files...")
    
    real_count = 0
    fake_count = 0
    
    # Extract 100 files (50 real + 50 fake)
    for i, sample in enumerate(dataset):
        if real_count >= 50 and fake_count >= 50:
            break
        
        # Check if sample has audio
        if 'audio' in sample and 'label' in sample:
            audio = sample['audio']
            label = sample['label']
            
            # Save real audio
            if label == 0 and real_count < 50:  # 0 = real
                filename = f"data/kaggle_audio/real/real_{real_count}.wav"
                # Save audio file
                import soundfile as sf
                sf.write(filename, audio['array'], audio['sampling_rate'])
                real_count += 1
                print(f"   Real: {real_count}/50", end='\r')
            
            # Save fake audio
            elif label == 1 and fake_count < 50:  # 1 = fake
                filename = f"data/kaggle_audio/fake/fake_{fake_count}.wav"
                # Save audio file
                import soundfile as sf
                sf.write(filename, audio['array'], audio['sampling_rate'])
                fake_count += 1
                print(f"   Fake: {fake_count}/50", end='\r')
    
    print(f"\n\n✅ Downloaded:")
    print(f"   Real audio: {real_count} files")
    print(f"   Fake audio: {fake_count} files")
    print(f"   Total: {real_count + fake_count} files")
    
    print("\n📁 Files saved to:")
    print(f"   data/kaggle_audio/real/")
    print(f"   data/kaggle_audio/fake/")
    
    print("\n🎯 Next step:")
    print("   python3 train_kaggle_audio.py")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n💡 Alternative: Manual download")
    print("   1. Visit: https://huggingface.co/datasets/nuriachandra/Deepfake-Eval-2024")
    print("   2. Download audio files")
    print("   3. Place in data/kaggle_audio/real/ and data/kaggle_audio/fake/")

print("\n" + "="*70)
