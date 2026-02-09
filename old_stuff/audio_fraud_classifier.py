"""
Audio Fraud Classifier - Scikit-learn based
Detects AI voice, deepfakes, scam calls
UPDATED: Uses soundfile (no numba dependency)
"""
import numpy as np
import soundfile as sf
import pickle
import os

class AudioFraudClassifier:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        model_path = 'models/audio_fraud_classifier.pkl'
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                
                self.model_loaded = True
                print("✅ Audio fraud classifier loaded")
            except Exception as e:
                print(f"❌ Error loading audio model: {e}")
                self.model_loaded = False
        else:
            print("⚠️ Audio fraud model not found")
            self.model_loaded = False
    
    def extract_features(self, audio_path):
        """
        Extract features - MUST MATCH train_on_real_audio.py
        10 features total
        """
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
            
            # 1-4: Basic stats
            features.append(np.mean(y))
            features.append(np.std(y))
            features.append(np.max(y))
            features.append(np.min(y))
            
            # 5: Zero crossing rate
            zcr = np.sum(np.abs(np.diff(np.sign(y)))) / (2 * len(y))
            features.append(zcr)
            
            # 6-7: Energy
            features.append(np.sum(y ** 2) / len(y))
            features.append(np.sqrt(np.mean(y ** 2)))
            
            # 8: FFT - Spectral centroid
            fft = np.abs(np.fft.fft(y)[:len(y)//2])
            freqs = np.fft.fftfreq(len(y), 1/sr)[:len(y)//2]
            
            spectral_centroid = np.sum(freqs * fft) / np.sum(fft)
            features.append(spectral_centroid)
            
            # 9-10: Frame energy
            frame_size = sr // 10
            num_frames = len(y) // frame_size
            frame_energies = [np.sum(y[i*frame_size:(i+1)*frame_size] ** 2) for i in range(num_frames)]
            
            features.append(np.mean(frame_energies))
            features.append(np.std(frame_energies))
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return None
    
    def predict(self, audio_path):
        """
        Predict if audio is real or fake
        Returns: dict with prediction results
        """
        if not self.model_loaded:
            return None
        
        try:
            # Extract features
            features = self.extract_features(audio_path)
            
            if features is None:
                return None
            
            # Predict
            prediction = self.model.predict(features)[0]
            probability = self.model.predict_proba(features)[0]
            
            is_fake = bool(prediction == 1)
            confidence = float(probability[1] if is_fake else probability[0])
            
            return {
                'is_fake': is_fake,
                'is_real': not is_fake,
                'confidence': confidence,
                'label': 'Fake/AI' if is_fake else 'Real',
                'probability_real': float(probability[0]),
                'probability_fake': float(probability[1])
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return None

# Global instance
audio_classifier = AudioFraudClassifier()
