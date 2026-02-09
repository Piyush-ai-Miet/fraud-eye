"""
Test Audio ML Model
Check if model is working correctly
"""
import pickle
import numpy as np
import soundfile as sf
import glob

# Load model
print("="*70)
print("🧪 Testing Audio ML Model")
print("="*70)

with open('models/audio_fraud_classifier.pkl', 'rb') as f:
    model = pickle.load(f)

print(f"\n✅ Model loaded")
print(f"   Estimators: {model.n_estimators}")
print(f"   Features expected: {model.n_features_in_}")
print(f"   Classes: {model.classes_}")

# Extract features function (same as training)
def extract_features(audio_path):
    try:
        y, sr = sf.read(audio_path)
        
        if len(y.shape) > 1:
            y = np.mean(y, axis=1)
        
        max_samples = 2 * sr
        if len(y) > max_samples:
            y = y[:max_samples]
        
        features = []
        
        features.append(np.mean(y))
        features.append(np.std(y))
        features.append(np.max(y))
        features.append(np.min(y))
        
        zcr = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
        features.append(zcr)
        
        features.append(np.sum(y ** 2) / len(y))
        features.append(np.sqrt(np.mean(y ** 2)))
        
        fft = np.abs(np.fft.fft(y)[:len(y)//2])
        freqs = np.fft.fftfreq(len(y), 1/sr)[:len(y)//2]
        
        spectral_centroid = np.sum(freqs * fft) / np.sum(fft)
        features.append(spectral_centroid)
        
        frame_size = sr // 10
        num_frames = len(y) // frame_size
        frame_energies = [np.sum(y[i*frame_size:(i+1)*frame_size] ** 2) for i in range(num_frames)]
        
        features.append(np.mean(frame_energies))
        features.append(np.std(frame_energies))
        
        return np.array(features).reshape(1, -1)
        
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test on real files
print("\n" + "="*70)
print("📊 Testing on Training Data")
print("="*70)

real_files = sorted(glob.glob("data/audio/real/*.wav"))[:5]
fake_files = sorted(glob.glob("data/audio/fake/*.wav"))[:5]

print(f"\n🔊 Testing REAL audio files:")
real_correct = 0
for f in real_files:
    feat = extract_features(f)
    if feat is not None:
        pred = model.predict(feat)[0]
        prob = model.predict_proba(feat)[0]
        label = "Real" if pred == 0 else "Fake/AI"
        confidence = prob[pred] * 100
        
        is_correct = (pred == 0)
        real_correct += is_correct
        
        status = "✅" if is_correct else "❌"
        print(f"   {status} {f.split('/')[-1][:30]:30s} → {label:8s} ({confidence:.1f}%)")

print(f"\n🔊 Testing FAKE audio files:")
fake_correct = 0
for f in fake_files:
    feat = extract_features(f)
    if feat is not None:
        pred = model.predict(feat)[0]
        prob = model.predict_proba(feat)[0]
        label = "Real" if pred == 0 else "Fake/AI"
        confidence = prob[pred] * 100
        
        is_correct = (pred == 1)
        fake_correct += is_correct
        
        status = "✅" if is_correct else "❌"
        print(f"   {status} {f.split('/')[-1][:30]:30s} → {label:8s} ({confidence:.1f}%)")

print("\n" + "="*70)
print("📈 Results:")
print(f"   Real files correct: {real_correct}/{len(real_files)}")
print(f"   Fake files correct: {fake_correct}/{len(fake_files)}")
print(f"   Total accuracy: {(real_correct + fake_correct)}/{len(real_files) + len(fake_files)}")
print("="*70)
