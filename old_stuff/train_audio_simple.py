"""
Train Audio Fraud Detection Model - SIMPLIFIED VERSION
NO NUMBA DEPENDENCY - uses soundfile + basic numpy
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

def extract_simple_features(audio_path, duration=2):
    """
    Extract SIMPLE audio features without librosa
    Features: Time-domain statistics, frequency-domain basics
    NO NUMBA NEEDED
    """
    try:
        # Load audio using soundfile (no numba)
        y, sr = sf.read(audio_path)
        
        # Convert to mono if stereo
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # Limit duration
        max_samples = int(duration * sr)
        if len(y) > max_samples:
            y = y[:max_samples]
        
        # Pad if too short
        if len(y) < max_samples:
            y = np.pad(y, (0, max_samples - len(y)), mode='constant')
        
        features = []
        
        # 1. Time-domain features
        features.append(np.mean(y))  # Mean amplitude
        features.append(np.std(y))   # Standard deviation
        features.append(np.max(y))   # Max amplitude
        features.append(np.min(y))   # Min amplitude
        features.append(np.median(y))  # Median
        
        # 2. Zero crossing rate (important for voice detection)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
        features.append(zero_crossings)
        
        # 3. Energy
        energy = np.sum(y ** 2) / len(y)
        features.append(energy)
        
        # 4. RMS (Root Mean Square)
        rms = np.sqrt(np.mean(y ** 2))
        features.append(rms)
        
        # 5. Spectral features (basic FFT)
        fft = np.fft.fft(y)
        fft_magnitude = np.abs(fft[:len(fft)//2])
        
        # Spectral centroid (center of mass of spectrum)
        freqs = np.fft.fftfreq(len(y), 1/sr)[:len(fft)//2]
        spectral_centroid = np.sum(freqs * fft_magnitude) / np.sum(fft_magnitude)
        features.append(spectral_centroid)
        
        # Spectral rolloff (frequency below which 85% of energy is contained)
        cumsum = np.cumsum(fft_magnitude)
        rolloff_idx = np.where(cumsum >= 0.85 * cumsum[-1])[0][0]
        spectral_rolloff = freqs[rolloff_idx]
        features.append(spectral_rolloff)
        
        # Spectral bandwidth
        spectral_bandwidth = np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * fft_magnitude) / np.sum(fft_magnitude))
        features.append(spectral_bandwidth)
        
        # 6. Pitch estimation (simple autocorrelation method)
        # AI voices often have unnatural pitch patterns
        autocorr = np.correlate(y, y, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # Find first peak after zero lag
        peaks = []
        for i in range(1, min(len(autocorr), sr//50)):  # Search up to 50 Hz
            if i > 0 and i < len(autocorr)-1:
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append((i, autocorr[i]))
        
        if peaks:
            # Get strongest peak
            strongest_peak = max(peaks, key=lambda x: x[1])
            pitch = sr / strongest_peak[0]
            features.append(pitch)
            features.append(strongest_peak[1])  # Peak strength
        else:
            features.append(0)
            features.append(0)
        
        # 7. Frame-based statistics (divide audio into frames)
        frame_size = sr // 10  # 100ms frames
        num_frames = len(y) // frame_size
        
        frame_energies = []
        frame_zcrs = []
        
        for i in range(num_frames):
            frame = y[i*frame_size:(i+1)*frame_size]
            frame_energies.append(np.sum(frame ** 2))
            frame_zcrs.append(np.sum(np.abs(np.diff(np.sign(frame)))) / (2 * len(frame)))
        
        # Statistics of frame energies
        features.append(np.mean(frame_energies))
        features.append(np.std(frame_energies))
        features.append(np.max(frame_energies))
        features.append(np.min(frame_energies))
        
        # Statistics of frame ZCRs
        features.append(np.mean(frame_zcrs))
        features.append(np.std(frame_zcrs))
        
        # 8. Spectral flux (change in spectrum over time)
        spectral_flux = []
        prev_fft = None
        for i in range(num_frames):
            frame = y[i*frame_size:(i+1)*frame_size]
            fft_frame = np.abs(np.fft.fft(frame)[:len(frame)//2])
            if prev_fft is not None:
                flux = np.sum((fft_frame - prev_fft) ** 2)
                spectral_flux.append(flux)
            prev_fft = fft_frame
        
        if spectral_flux:
            features.append(np.mean(spectral_flux))
            features.append(np.std(spectral_flux))
        else:
            features.append(0)
            features.append(0)
        
        return np.array(features)
        
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

def load_audio_dataset(data_dir='data/audio'):
    """Load audio files and extract features"""
    print(f"\n📂 Loading audio files from {data_dir}...")
    
    real_dir = os.path.join(data_dir, 'real')
    fake_dir = os.path.join(data_dir, 'fake')
    
    if not os.path.exists(real_dir) or not os.path.exists(fake_dir):
        print(f"❌ Dataset folders not found!")
        return None, None
    
    # Get audio files
    real_files = []
    fake_files = []
    
    for ext in ['*.wav', '*.mp3', '*.flac', '*.ogg']:
        real_files.extend(glob.glob(os.path.join(real_dir, ext)))
        fake_files.extend(glob.glob(os.path.join(fake_dir, ext)))
    
    print(f"   Real audio files: {len(real_files)}")
    print(f"   Fake audio files: {len(fake_files)}")
    
    # Limit to 50 files each for faster training
    real_files = real_files[:50]
    fake_files = fake_files[:50]
    
    print(f"   Using: {len(real_files)} real + {len(fake_files)} fake = {len(real_files) + len(fake_files)} total")
    
    if len(real_files) == 0 or len(fake_files) == 0:
        print(f"\n❌ No audio files found!")
        return None, None
    
    # Extract features
    X = []
    y = []
    
    print(f"\n🔊 Extracting features from real audio...")
    for audio_file in tqdm(real_files):
        features = extract_simple_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(0)  # 0 = Real
    
    print(f"\n🔊 Extracting features from fake audio...")
    for audio_file in tqdm(fake_files):
        features = extract_simple_features(audio_file)
        if features is not None:
            X.append(features)
            y.append(1)  # 1 = Fake
    
    return np.array(X), np.array(y)

def train_model():
    """Train Random Forest classifier"""
    print("="*70)
    print("🎤 Audio Fraud Detection Model Training (SIMPLIFIED)")
    print("   NO NUMBA DEPENDENCY")
    print("="*70)
    
    # Load dataset
    X, y = load_audio_dataset()
    
    if X is None or len(X) == 0:
        print("\n❌ No data loaded!")
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
    print(classification_report(y_test, y_pred, 
                                target_names=['Real', 'Fake/AI']))
    
    print("\n🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Real:  {cm[0][0]:4d}  |  False Fake: {cm[0][1]:4d}")
    print(f"   False Real: {cm[1][0]:4d}  |  True Fake:  {cm[1][1]:4d}")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    
    with open('models/audio_fraud_classifier.pkl', 'wb') as f:
        pickle.dump(clf, f)
    
    print("\n💾 Model saved to models/audio_fraud_classifier.pkl")
    print("="*70)
    
    return clf

if __name__ == '__main__':
    print("\n🎤 Audio Fraud Detection - Simplified Training")
    print("   NO NUMBA DEPENDENCY")
    print("   Using 200 real audio files (100 real + 100 fake)")
    
    model = train_model()
    
    if model:
        print("\n✅ Training complete!")
        print("\n📋 Next steps:")
        print("   1. Model is ready to use")
        print("   2. Test at http://localhost:5001")
        print("\n" + "="*70)
