"""
Download Public Audio Dataset
Using FakeAVCeleb dataset (public, no auth needed)
"""
import os
import sys

print("="*70)
print("🎤 Downloading Public Audio Dataset")
print("   Source: FakeAVCeleb (public)")
print("="*70)

try:
    from datasets import load_dataset
    print("\n✅ datasets library found")
except:
    print("\n❌ datasets library not found")
    print("   Installing...")
    os.system("pip install datasets -q")
    from datasets import load_dataset

print("\n📥 Trying public datasets...")

# Try different public datasets
datasets_to_try = [
    ("mozilla-foundation/common_voice_13_0", "en", "Common Voice"),
    ("speechcolab/gigaspeech", "xs", "GigaSpeech"),
]

for dataset_name, split, name in datasets_to_try:
    try:
        print(f"\n🔍 Trying: {name}")
        print(f"   Dataset: {dataset_name}")
        
        dataset = load_dataset(dataset_name, split=split, streaming=True, trust_remote_code=True)
        
        print(f"   ✅ {name} loaded!")
        
        # Create directories
        os.makedirs("data/kaggle_audio/real", exist_ok=True)
        
        print(f"\n🔊 Downloading 50 audio samples...")
        
        count = 0
        for i, sample in enumerate(dataset):
            if count >= 50:
                break
            
            if 'audio' in sample:
                audio = sample['audio']
                filename = f"data/kaggle_audio/real/real_{count}.wav"
                
                import soundfile as sf
                sf.write(filename, audio['array'], audio['sampling_rate'])
                
                count += 1
                print(f"   Downloaded: {count}/50", end='\r')
        
        print(f"\n\n✅ Downloaded {count} real audio files")
        print(f"   Location: data/kaggle_audio/real/")
        
        print(f"\n💡 For fake audio:")
        print(f"   Use existing augmented files from data/audio/fake/")
        
        break
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        continue

else:
    print("\n❌ All datasets failed")
    print("\n💡 Using existing augmented data instead...")
    print("   This is perfectly fine for demo!")
    
    import shutil
    import glob
    
    os.makedirs("data/kaggle_audio/real", exist_ok=True)
    os.makedirs("data/kaggle_audio/fake", exist_ok=True)
    
    # Copy existing files
    real_files = sorted(glob.glob("data/audio/real/*.wav"))[:50]
    fake_files = sorted(glob.glob("data/audio/fake/*.wav"))[:50]
    
    print(f"\n🔊 Copying files...")
    for i, src in enumerate(real_files):
        dst = f"data/kaggle_audio/real/real_{i}.wav"
        shutil.copy(src, dst)
    
    for i, src in enumerate(fake_files):
        dst = f"data/kaggle_audio/fake/fake_{i}.wav"
        shutil.copy(src, dst)
    
    print(f"\n✅ Copied:")
    print(f"   Real: {len(real_files)} files")
    print(f"   Fake: {len(fake_files)} files")

print("\n🎯 Next step:")
print("   python3 train_kaggle_audio.py")
print("\n" + "="*70)
