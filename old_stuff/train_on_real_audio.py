"""
Train on REAL audio files (50 real + 50 fake = 100 total)
Using existing augmented data
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

def extract_features(audio_path):
    """Extract simple features - FAST"""
    try:
        # Load audio
        y, sr = sf.read(audio_path)
        
        # Mono
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        # Limit to 2 seconds
        max_samples = 2 * sr
        if len(y) > max_samples:
            y = y[:max_samples]
        
        features = []
        
        # Basic stats
        features.append(np.mean(y))
        features.append(np.std(y))
        features.append(np.max(y))
        features.append(np.min(y))
        
        # Zero crossing rate
        zcr = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
        features.append(zcr)
        
        # Energy
        features.append(np.sum(y ** 2) / len(y))
        features.append(np.sqrt(np.mean(y ** 2)))
        
        # FFT
        fft = np.abs(np.fft.fft(y)[:len(y)//2])
        freqs = np.fft.fftfreq(len(y), 1/sr)[:len(y)//2]
        
        spectral_centroid = np.sum(freqs * fft) / np.sum(fft)
        features.append(spectral_centroid)
        
        # Frame energy
        frame_size = sr // 10
        num_frames = len(y) // frame_size
        frame_energies = [np.sum(y[i*frame_size:(i+1)*frame_size] ** 2) for i in range(num_frames)]
        
        features.append(np.mean(frame_energies))
        features.append(np.std(frame_energies))
        
        return np.array(features)
        
    except Exception as e:
        return None

# Load files
print("="*70)
print("🎤 Training on REAL Audio Data")
print("   100 real + 100 fake = 200 files")
print("="*70)

real_files = sorted(glob.glob("data/audio/real/*.wav"))[:100]
fake_files = sorted(glob.glob("data/audio/fake/*.wav"))[:100]

print(f"\n📂 Files:")
print(f"   Real: {len(real_files)}")
print(f"   Fake: {len(fake_files)}")

# Extract features
X = []
y = []

print(f"\n🔊 Extracting features...")

for f in tqdm(real_files, desc="   Real"):
    feat = extract_features(f)
    if feat is not None:
        X.append(feat)
        y.append(0)

for f in tqdm(fake_files, desc="   Fake"):
    feat = extract_features(f)
    if feat is not None:
        X.append(feat)
        y.append(1)

X = np.array(X)
y = np.array(y)

print(f"\n📊 Dataset:")
print(f"   Total: {len(X)}")
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
print("\n🌲 Training...")
clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n" + "="*70)
print("✅ RESULTS")
print("="*70)
print(f"\n🎯 Accuracy: {accuracy*100:.2f}%")

print("\n📊 Report:")
print(classification_report(y_test, y_pred, target_names=['Real', 'Fake/AI']))

print("\n🔢 Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"   True Real:  {cm[0][0]:4d}  |  False Fake: {cm[0][1]:4d}")
print(f"   False Real: {cm[1][0]:4d}  |  True Fake:  {cm[1][1]:4d}")

# Save
with open('models/audio_fraud_classifier.pkl', 'wb') as f:
    pickle.dump(clf, f)

print("\n💾 Saved: models/audio_fraud_classifier.pkl")
print("="*70)
print("\n✅ DONE! Model trained on REAL audio data")
print("   Ready to use at http://localhost:5001")
