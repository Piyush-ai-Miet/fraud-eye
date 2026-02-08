"""
Train Audio Fraud Detection Model using scikit-learn
Detects AI-generated voice, deepfakes, and scam calls
"""
import numpy as np
import librosa
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os
import glob
from tqdm import tqdm

def extract_audio_features(audio_path, duration=3):
    """
    Extract audio features using librosa
    Features: MFCC, Spectral features, Zero Crossing Rate, Pitch
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, duration=duration, sr=16000)
        
        # Extract features
        features = []
        
        # 1. MFCC (Mel-frequency cepstral coefficients) - 13 coefficients
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_mean = np.mean(mfcc, axis=1)
        mfcc_std = np.std(mfcc, axis=1)
        features.extend(mfcc_mean)
        features.extend(mfcc_std)
        
        # 2. Spectral Centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features.append(np.mean(spectral_centroid))
        features.append(np.std(spectral_centroid))
        
        # 3. Spectral Rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        features.append(np.mean(spectral_rolloff))
        features.append(np.std(spectral_rolloff))
        
        # 4. Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        features.append(np.mean(zcr))
        features.append(np.std(zcr))
        
        # 5. Spectral Bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        features.append(np.mean(spectral_bandwidth))
        features.append(np.std(spectral_bandwidth))
        
        # 6. RMS Energy
        rms = librosa.feature.rms(y=y)
        features.append(np.mean(rms))
        features.append(np.std(rms))
        
        # 7. Chroma Features
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        features.append(np.mean(chroma))
        features.append(np.std(chroma))
        
        # 8. Pitch (F0) - IMPORTANT for AI voice detection
        # AI voices often have unnatural pitch patterns
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 0:
                features.append(np.mean(pitch_values))  # Mean pitch
                features.append(np.std(pitch_values))   # Pitch variation
                features.append(np.max(pitch_values))   # Max pitch
                features.append(np.min(pitch_values))   # Min pitch
            else:
                features.extend([0, 0, 0, 0])
        except:
            features.extend([0, 0, 0, 0])
        
        # 9. Spectral Contrast (helps detect AI artifacts)
        spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
        features.append(np.mean(spectral_contrast))
        features.append(np.std(spectral_contrast))
        
        # 10. Tonnetz (harmonic features - AI voices have different patterns)
        tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
        features.append(np.mean(tonnetz))
        features.append(np.std(tonnetz))
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

def load_audio_dataset(data_dir='data/audio'):
    """
    Load audio files from directory structure:
    data/audio/real/*.wav
    data/audio/fake/*.wav
    """
    print(f"\n📂 Loading audio files from {data_dir}...")
    
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
        print(f"❌ Dataset folders not found!")
        print(f"   Expected: {real_dir} and {fake_dir}")
        print(f"\n💡 Create folders and add audio files:")
        print(f"   mkdir -p {real_dir}")
        print(f"   mkdir -p {fake_dir}")
        return None, None
    
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
        print(f"   Add .wav, .mp3, .flac, or .ogg files to:")
        print(f"   - {real_dir}/")
        print(f"   - {fake_dir}/")
        return None, None
    
    # Extract features
    X = []
    y = []
    
    print(f"\n🔊 Extracting features from real audio...")
    for audio_file in tqdm(real_files):
        features = extract_audio_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(0)  # 0 = Real
    
    print(f"\n🔊 Extracting features from fake audio...")
    for audio_file in tqdm(fake_files):
        features = extract_audio_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(1)  # 1 = Fake
    
    return np.array(X), np.array(y)

def create_synthetic_dataset():
    """
    Create a synthetic dataset for demonstration
    Use this if no real audio files are available
    """
    print("\n⚠️ Using synthetic data for demonstration")
    print("   For production, use real audio datasets!")
    
    np.random.seed(42)
    
    # Real audio samples (100 samples)
    # Real human voice has natural pitch variation, harmonics
    real_samples = []
    for i in range(100):
        mfcc_mean = np.random.normal(0, 20, 13)
        mfcc_std = np.random.normal(15, 5, 13)
        spectral_centroid = [np.random.normal(2000, 500), np.random.normal(400, 100)]
        spectral_rolloff = [np.random.normal(4000, 800), np.random.normal(600, 150)]
        zcr = [np.random.normal(0.1, 0.03), np.random.normal(0.02, 0.01)]
        spectral_bandwidth = [np.random.normal(1800, 400), np.random.normal(300, 80)]
        rms = [np.random.normal(0.05, 0.02), np.random.normal(0.01, 0.005)]
        chroma = [np.random.normal(0.5, 0.15), np.random.normal(0.1, 0.03)]
        
        # Pitch features (natural human voice: 85-255 Hz for male, 165-255 Hz for female)
        pitch_mean = np.random.normal(180, 40)  # Natural pitch
        pitch_std = np.random.normal(25, 8)     # Good variation
        pitch_max = pitch_mean + np.random.normal(60, 15)
        pitch_min = pitch_mean - np.random.normal(50, 12)
        pitch = [pitch_mean, pitch_std, pitch_max, pitch_min]
        
        # Spectral contrast (natural voice has good contrast)
        spectral_contrast = [np.random.normal(25, 5), np.random.normal(8, 2)]
        
        # Tonnetz (harmonic features)
        tonnetz = [np.random.normal(0.3, 0.1), np.random.normal(0.08, 0.02)]
        
        features = np.concatenate([
            mfcc_mean, mfcc_std, spectral_centroid, spectral_rolloff,
            zcr, spectral_bandwidth, rms, chroma, pitch,
            spectral_contrast, tonnetz
        ])
        real_samples.append(features)
    
    # Fake audio samples (100 samples)
    # AI voice has unnatural pitch, less variation, artifacts
    fake_samples = []
    for i in range(100):
        mfcc_mean = np.random.normal(0, 15, 13)  # Less variation
        mfcc_std = np.random.normal(10, 3, 13)   # Lower std
        spectral_centroid = [np.random.normal(2500, 300), np.random.normal(300, 50)]
        spectral_rolloff = [np.random.normal(5000, 500), np.random.normal(400, 80)]
        zcr = [np.random.normal(0.08, 0.02), np.random.normal(0.015, 0.005)]
        spectral_bandwidth = [np.random.normal(1500, 250), np.random.normal(200, 40)]
        rms = [np.random.normal(0.04, 0.015), np.random.normal(0.008, 0.003)]
        chroma = [np.random.normal(0.6, 0.1), np.random.normal(0.08, 0.02)]
        
        # Pitch features (AI voice: more uniform, less natural variation)
        pitch_mean = np.random.normal(200, 20)  # More uniform
        pitch_std = np.random.normal(12, 4)     # Less variation (KEY DIFFERENCE)
        pitch_max = pitch_mean + np.random.normal(30, 8)
        pitch_min = pitch_mean - np.random.normal(25, 6)
        pitch = [pitch_mean, pitch_std, pitch_max, pitch_min]
        
        # Spectral contrast (AI voice has less contrast, artifacts)
        spectral_contrast = [np.random.normal(18, 3), np.random.normal(5, 1)]
        
        # Tonnetz (AI voice has different harmonic patterns)
        tonnetz = [np.random.normal(0.4, 0.06), np.random.normal(0.05, 0.01)]
        
        features = np.concatenate([
            mfcc_mean, mfcc_std, spectral_centroid, spectral_rolloff,
            zcr, spectral_bandwidth, rms, chroma, pitch,
            spectral_contrast, tonnetz
        ])
        fake_samples.append(features)
    
    X = np.array(real_samples + fake_samples)
    y = np.array([0] * 100 + [1] * 100)  # 0 = Real, 1 = Fake
    
    return X, y

def train_model(use_real_data=True):
    """Train Random Forest classifier for audio fraud detection"""
    print("="*70)
    print("🎤 Audio Fraud Detection Model Training")
    print("   For Indian Tier 2/3 Communities")
    print("="*70)
    
    # Load dataset
    if use_real_data:
        X, y = load_audio_dataset()
        if X is None:
            print("\n⚠️ Falling back to synthetic data...")
            X, y = create_synthetic_dataset()
    else:
        X, y = create_synthetic_dataset()
    
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
    print(classification_report(y_test, y_pred, 
                                target_names=['Real', 'Fake/AI']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Real:  {cm[0][0]:4d}  |  False Fake: {cm[0][1]:4d}")
    print(f"   False Real: {cm[1][0]:4d}  |  True Fake:  {cm[1][1]:4d}")
    
    # Feature importance
    feature_names = (
        [f'MFCC_mean_{i}' for i in range(13)] +
        [f'MFCC_std_{i}' for i in range(13)] +
        ['SpectralCentroid_mean', 'SpectralCentroid_std',
         'SpectralRolloff_mean', 'SpectralRolloff_std',
         'ZCR_mean', 'ZCR_std',
         'SpectralBandwidth_mean', 'SpectralBandwidth_std',
         'RMS_mean', 'RMS_std',
         'Chroma_mean', 'Chroma_std',
         'Pitch_mean', 'Pitch_std', 'Pitch_max', 'Pitch_min',
         'SpectralContrast_mean', 'SpectralContrast_std',
         'Tonnetz_mean', 'Tonnetz_std']
    )
    
    importances = clf.feature_importances_
    top_features = sorted(zip(feature_names, importances), 
                         key=lambda x: x[1], reverse=True)[:5]
    
    print("\n🔝 Top 5 Important Features:")
    for feat, imp in top_features:
        print(f"   {feat:30s}: {imp:.4f}")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    
    with open('models/audio_fraud_classifier.pkl', 'wb') as f:
        pickle.dump(clf, f)
    
    with open('models/audio_feature_names.pkl', 'wb') as f:
        pickle.dump(feature_names, f)
    
    print("\n💾 Model saved to models/audio_fraud_classifier.pkl")
    print("="*70)
    
    return clf

if __name__ == '__main__':
    print("\n🎤 Audio Fraud Detection - ML Training")
    print("   Detects: AI voice, deepfakes, scam calls")
    print("   For: Indian Tier 2/3 communities")
    
    print("\n📝 Dataset Options:")
    print("   1. Use real audio files from data/audio/")
    print("   2. Use synthetic data (demo only)")
    
    choice = input("\nUse real audio files? (y/n): ").strip().lower()
    use_real = choice == 'y'
    
    model = train_model(use_real_data=use_real)
    
    print("\n✅ Training complete!")
    print("\n📋 Next steps:")
    print("   1. Test model: python test_audio_model.py")
    print("   2. Integrate into app_simple.py")
    print("   3. Upload audio to web interface")
    print("\n" + "="*70)
