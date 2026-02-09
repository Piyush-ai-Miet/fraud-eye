"""
Audio Processing Utility
Extract features from audio files for fraud detection
"""
import numpy as np

def calculate_zero_crossing_rate(audio):
    """Calculate zero crossing rate"""
    zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
    return zcr

def calculate_rms_energy(audio):
    """Calculate RMS energy"""
    rms = np.sqrt(np.mean(audio**2))
    return rms

def calculate_spectral_centroid(audio, sr=22050):
    """Calculate spectral centroid (brightness)"""
    spectrum = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    centroid = np.sum(freqs * spectrum) / np.sum(spectrum)
    return centroid

def extract_audio_features(audio, sr=22050):
    """Extract all audio features"""
    return {
        'zero_crossing_rate': calculate_zero_crossing_rate(audio),
        'rms_energy': calculate_rms_energy(audio),
        'spectral_centroid': calculate_spectral_centroid(audio, sr),
        'duration': len(audio) / sr,
        'sample_rate': sr
    }

def is_audio_suspicious(features):
    """Simple rule-based audio fraud detection"""
    # Very low energy might indicate synthetic audio
    if features['rms_energy'] < 0.01:
        return True, "Very low energy - possibly synthetic"
    
    # Unusual spectral centroid
    if features['spectral_centroid'] > 8000 or features['spectral_centroid'] < 500:
        return True, "Unusual frequency distribution"
    
    return False, "Audio appears normal"

if __name__ == '__main__':
    # Test with dummy data
    dummy_audio = np.random.randn(22050)  # 1 second of random audio
    features = extract_audio_features(dummy_audio)
    print(f"Audio Features: {features}")
    suspicious, reason = is_audio_suspicious(features)
    print(f"Suspicious: {suspicious} - {reason}")
