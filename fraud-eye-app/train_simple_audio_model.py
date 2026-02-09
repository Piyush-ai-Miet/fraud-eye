"""
Simple Audio Fraud Detection Model
Uses basic features - NO librosa dependency
Compatible with any numpy version
"""
import numpy as np
import soundfile as sf
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os
import glob

def extract_simple_features(audio_path):
    """
    Extract simple audio features using only numpy and soundfile
    NO librosa needed!
    """
    try:
        # Load audio
        y, sr = sf.read(audio_path)
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # Limit to 2 seconds
        max_samples = 2 * sr
        if len(y) > max_samples:
            y = y[:max_samples]
        
        features = []
        
        # 1-4: Basic statistics
        features.append(np.mean(y))
        features.append(np.std(y))
        features.append(np.max(y))
        features.append(np.min(y))
        
        # 5: Zero crossing rate (pitch indicator)
        zcr = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
        features.append(zcr)
        
        # 6-7: Energy features
        features.append(np.sum(y ** 2) / len(y))  # Average energy
        features.append(np.sqrt(np.mean(y ** 2)))  # RMS
        
        # 8: Spectral centroid (using FFT)
        fft = np.abs(np.fft.fft(y)[:len(y)//2])
        freqs = np.fft.fftfreq(len(y), 1/sr)[:len(y)//2]
        spectral_centroid = np.sum(freqs * fft) / np.sum(fft) if np.sum(fft) > 0 else 0
        features.append(spectral_centroid)
        
        # 9-10: Frame energy statistics
        frame_size = sr // 10  # 100ms frames
        num_frames = len(y) // frame_size
        frame_energies = [np.sum(y[i*frame_size:(i+1)*frame_size] ** 2) for i in range(num_frames)]
        features.append(np.mean(frame_energies))
        features.append(np.std(frame_energies))
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

def load_audio_dataset(data_dir='data/audio'):
    """Load audio files from real/ and fake/ folders"""
    print(f"\n📂 Loading audio files from {data_dir}...")
    
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    # Get audio files
    real_files = []
    fake_files = []
    
    for ext in ['*.wav', '*.mp3', '*.flac', '*.ogg']:
        real_files.extend(glob.glob(os.path.join(real_dir, ext)))
        fake_files.extend(glob.glob(os.path.join(fake_dir, ext)))
    
    print(f"   Real audio files: {len(real_files)}")
    print(f"   Fake audio files: {len(fake_files)}")
    
    if len(real_files) == 0 or len(fake_files) == 0:
        print(f"\n❌ No audio files found!")
        return None, None
    
    # Extract features
    X = []
    y = []
    
    print(f"\n🔊 Processing real audio...")
    for i, audio_file in enumerate(real_files):
        if i % 10 == 0:
            print(f"   {i}/{len(real_files)}")
        features = extract_simple_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(0)  # 0 = Real
    
    print(f"\n🔊 Processing fake audio...")
    for i, audio_file in enumerate(fake_files):
        if i % 10 == 0:
            print(f"   {i}/{len(fake_files)}")
        features = extract_simple_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(1)  # 1 = Fake
    
    return np.array(X), np.array(y)

def train_model():
    """Train simple audio fraud detection model"""
    print("="*70)
    print("🎤 Simple Audio Fraud Detection Model Training")
    print("   NO librosa dependency - Works with any numpy version!")
    print("="*70)
    
    # Load dataset
    X, y = load_audio_dataset()
    
    if X is None:
        print("\n❌ Failed to load dataset")
        return None
    
    print(f"\n📊 Dataset Summary:")
    print(f"   Total samples: {len(X)}")
    print(f"   Real audio: {np.sum(y == 0)}")
    print(f"   Fake audio: {np.sum(y == 1)}")
    print(f"   Features per sample: {X.shape[1]}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📈 Data Split:")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Testing: {len(X_test)} samples")
    
    # Train Random Forest
    print("\n🌲 Training Random Forest classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*70)
    print("✅ TRAINING RESULTS")
    print("="*70)
    print(f"\n🎯 Accuracy: {accuracy*100:.2f}%")
    
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake/AI']))
    
    # Save model
    os.makedirs('models', exist_ok=True)
    
    with open('models/audio_fraud_classifier.pkl', 'wb') as f:
        pickle.dump(clf, f)
    
    feature_names = [
        'mean', 'std', 'max', 'min', 'zcr',
        'energy', 'rms', 'spectral_centroid',
        'frame_energy_mean', 'frame_energy_std'
    ]
    
    with open('models/audio_feature_names.pkl', 'wb') as f:
        pickle.dump(feature_names, f)
    
    print("\n💾 Model saved to models/audio_fraud_classifier.pkl")
    print("="*70)
    
    return clf

if __name__ == '__main__':
    print("\n🎤 Simple Audio Fraud Detection - ML Training")
    print("   Compatible with any numpy version!")
    print("   No librosa dependency!")
    
    model = train_model()
    
    if model:
        print("\n✅ Training complete!")
        print("\n📋 Next steps:")
        print("   1. Test locally: python app_simple.py")
        print("   2. Push to GitHub")
        print("   3. Deploy to Render")
    else:
        print("\n❌ Training failed!")
