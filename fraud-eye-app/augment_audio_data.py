"""
Augment audio data to create more training samples
From 2 files → 100+ files using simple audio augmentation
No numba dependency - uses soundfile only
"""
import numpy as np
import soundfile as sf
import os
from tqdm import tqdm

def add_noise(audio, noise_factor=0.005):
    """Add random noise"""
    noise = np.random.randn(len(audio))
    return audio + noise_factor * noise

def change_volume(audio, factor=1.0):
    """Change volume"""
    return audio * factor

def augment_audio_file(input_path, output_dir, label, num_augmentations=50):
    """
    Create multiple augmented versions of one audio file
    Simple augmentations without numba dependency
    """
    print(f"\n🔊 Augmenting: {os.path.basename(input_path)}")
    
    # Load audio using soundfile
    audio, sr = sf.read(input_path)
    
    # Convert to mono if stereo
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
    
    # Save original
    output_path = os.path.join(output_dir, f"{label}_original.wav")
    sf.write(output_path, audio, sr)
    print(f"   ✅ Original saved")
    
    augmented_count = 0
    
    # Create augmentations
    for i in tqdm(range(num_augmentations), desc="   Augmenting"):
        try:
            # Random augmentation combination
            aug_audio = audio.copy()
            
            # 1. Add noise (70% chance)
            if np.random.random() > 0.3:
                noise_factor = np.random.uniform(0.001, 0.015)
                aug_audio = add_noise(aug_audio, noise_factor)
            
            # 2. Change volume (50% chance)
            if np.random.random() > 0.5:
                volume_factor = np.random.uniform(0.8, 1.2)
                aug_audio = change_volume(aug_audio, volume_factor)
            
            # 3. Time shift (40% chance)
            if np.random.random() > 0.6:
                shift_amount = np.random.randint(-sr//4, sr//4)
                aug_audio = np.roll(aug_audio, shift_amount)
            
            # 4. Add multiple noise layers (30% chance)
            if np.random.random() > 0.7:
                noise_factor2 = np.random.uniform(0.002, 0.008)
                aug_audio = add_noise(aug_audio, noise_factor2)
            
            # Save augmented audio
            output_path = os.path.join(output_dir, f"{label}_aug_{i+1}.wav")
            sf.write(output_path, aug_audio, sr)
            augmented_count += 1
            
        except Exception as e:
            print(f"   ⚠️ Error in augmentation {i}: {e}")
            continue
    
    print(f"   ✅ Created {augmented_count} augmented samples")
    return augmented_count + 1  # +1 for original

def main():
    print("="*70)
    print("🎤 Audio Data Augmentation")
    print("   Creating training dataset from 2 audio files")
    print("="*70)
    
    # Check input files
    real_file = "data/audio/real/real_audio.flac"
    fake_file = "data/audio/fake/Elevanlabs_Fake.wav"
    
    if not os.path.exists(real_file):
        print(f"❌ Real audio not found: {real_file}")
        return
    
    if not os.path.exists(fake_file):
        print(f"❌ Fake audio not found: {fake_file}")
        return
    
    print(f"\n📂 Input files:")
    print(f"   Real: {real_file}")
    print(f"   Fake: {fake_file}")
    
    # Create output directories
    os.makedirs("data/audio/real", exist_ok=True)
    os.makedirs("data/audio/fake", exist_ok=True)
    
    # Augment real audio
    print("\n" + "="*70)
    print("1️⃣ Augmenting REAL audio...")
    print("="*70)
    real_count = augment_audio_file(
        real_file, 
        "data/audio/real", 
        "real",
        num_augmentations=99  # 99 + 1 original = 100 total
    )
    
    # Augment fake audio
    print("\n" + "="*70)
    print("2️⃣ Augmenting FAKE audio...")
    print("="*70)
    fake_count = augment_audio_file(
        fake_file, 
        "data/audio/fake", 
        "fake",
        num_augmentations=99  # 99 + 1 original = 100 total
    )
    
    # Summary
    print("\n" + "="*70)
    print("✅ AUGMENTATION COMPLETE")
    print("="*70)
    print(f"\n📊 Dataset Summary:")
    print(f"   Real audio samples: {real_count}")
    print(f"   Fake audio samples: {fake_count}")
    print(f"   Total samples: {real_count + fake_count}")
    
    print(f"\n📁 Files saved to:")
    print(f"   data/audio/real/ ({real_count} files)")
    print(f"   data/audio/fake/ ({fake_count} files)")
    
    print(f"\n🎯 Next step:")
    print(f"   python3 train_audio_fraud_model.py")
    print(f"   Choose 'y' to use real audio files")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
