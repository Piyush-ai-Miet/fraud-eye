"""
Train Audio Fraud Detection Model - FAST VERSION
Minimal features, maximum speed
NO NUMBA DEPENDENCY
"""
import numpy as np
import soundfile as sf
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import os
import glob
from tqdm import tqdm

def extract_fast_features(audio_path, duration=2):
    """
    Extract MINIMAL features for FAST training
    Only the most important features for AI voice detection
    """
    try:
        # Load audio
        y, sr = sf.read(audio_path)
        
        # Convert to mono
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # Limit duration
        max_samples = int(duration * sr)
        if len(y) > max_samples:
            y = y[:max_samples]
        
        features = []
        
        # 1. Basic statistics (5 features)
        features.append(np.mean(y))
        features.append(np.std(y))
        features.append(np.max(y))
        features.append(np.min(y))
        features.append(np.median(y))
        
        # 2. Zero crossing rate (1 feature) - IMPORTANT for voice
        zcr = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
        features.append(zcr)
        
        # 3. Energy (2 features)
        energy = np.sum(y ** 2) / len(y)
        rms = np.sqrt(np.mean(y ** 2))
        features.append(energy)
        features.append(rms)
        
        # 4. Simple spectral features (3 features)
        fft = np.abs(np.fft.fft(y)[:len(y)//2])
        freqs = np.fft.fftfreq(len(y), 1/sr)[:len(y)//2]
        
        spectral_centroid = np.sum(freqs * fft) / np.sum(fft)
        features.append(spectral_centroid)
        
        cumsum = np.cumsum(fft)
        rolloff_idx = np.where(cumsum >= 0.85 * cumsum[-1])[0][0]
        features.append(freqs[rolloff_idx])
        
        spectral_bandwidth = np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * fft) / np.sum(fft))
        features.append(spectral_bandwidth)
        
        # 5. Frame statistics (4 features) - IMPORTANT for AI detection
        frame_size = sr // 10
        num_frames = len(y) // frame_size
        
        frame_energies = [np.sum(y[i*frame_size:(i+1)*frame_size] ** 2) for i in range(num_frames)]
        
        features.append(np.mean(frame_energies))
        features.append(np.std(frame_energies))
        features.append(np.max(frame_energies))
        features.append(np.min(frame_energies))
        
        # Total: 15 features (fast to compute)
        return np.array(features)
        
    except Exception as e:
        print(f"Error: {audio_path}: {e}")
        return None

def load_dataset():
    """Load audio files"""
    print(f"\n📂 Loading audio files...")
    
    real_dir = "data/audio/real"
    fake_dir = "data/audio/fake"
    
    # Get files
    real_files = glob.glob(os.path.join(real_dir, '*.wav'))
    fake_files = glob.glob(os.path.join(fake_dir, '*.wav'))
    
    print(f"   Real: {len(real_files)} files")
    print(f"   Fake: {len(fake_files)} files")
    
    # Extract features
    X = []
    y = []
    
    print(f"\n🔊 Extracting features (FAST MODE)...")
    
    # Real audio
    for audio_file in tqdm(real_files, desc="   Real"):
        features = extract_fast_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(0)
    
    # Fake audio
    for audio_file in tqdm(fake_files, desc="   Fake"):
        features = extract_fast_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(1)
    
    return np.array(X), np.array(y)

def train_model():
    """Train model"""
    print("="*70)
    print("🎤 Audio Fraud Detection - FAST TRAINING")
    print("   Training on REAL audio data (200 files)")
    print("="*70)
    
    # Load data
    X, y = load_dataset()
    
    if len(X) == 0:
        print("\n❌ No data!")
        return None
    
    print(f"\n📊 Dataset:")
    print(f"   Total: {len(X)} samples")
    print(f"   Real: {np.sum(y == 0)}")
    print(f"   Fake: {np.sum(y == 1)}")
    print(f"   Features: {X.shape[1]}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n📈 Split:")
    print(f"   Train: {len(X_train)}")
    print(f"   Test: {len(X_test)}")
    
    # Train
    print("\n🌲 Training Random Forest...")
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
    print("✅ RESULTS")
    print("="*70)
    print(f"\n🎯 Accuracy: {accuracy*100:.2f}%")
    
    print("\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake/AI']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Real:  {cm[0][0]:4d}  |  False Fake: {cm[0][1]:4d}")
    print(f"   False Real: {cm[1][0]:4d}  |  True Fake:  {cm[1][1]:4d}")
    
    # Save
    os.makedirs('models', exist_ok=True)
    
    with open('models/audio_fraud_classifier.pkl', 'wb') as f:
        pickle.dump(clf, f)
    
    print("\n💾 Model saved: models/audio_fraud_classifier.pkl")
    print("="*70)
    
    return clf

if __name__ == '__main__':
    print("\n🎤 FAST Audio Training")
    print("   Using 200 REAL audio files")
    print("   15 features per sample")
    print("   Training time: ~30 seconds")
    
    model = train_model()
    
    if model:
        print("\n✅ Training complete!")
        print("   Model trained on REAL audio data")
        print("   Ready to use at http://localhost:5001")
        print("\n" + "="*70)
