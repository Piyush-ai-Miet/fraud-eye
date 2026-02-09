import torch
import torchaudio
import torchaudio.transforms as T
import sys
import os

sys.path.append('../fraud-audio-detection/src')
from models import CRNNWithAttn

class MLAudioDetector:
    def __init__(self):
        self.device = torch.device("cpu")
        self.model = None
        self.model_loaded = False
        
        try:
            self.model = CRNNWithAttn()
            model_path = '../fraud-audio-detection/models/best_model10.pth'
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            self.model_loaded = True
        except Exception as e:
            print(f"ML model load failed: {e}")
            self.model_loaded = False
    
    def preprocess(self, waveform, sample_rate):
        if sample_rate != 16000:
            resample = T.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resample(waveform)
        
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        
        max_len = 16000 * 4
        if waveform.shape[1] > max_len:
            waveform = waveform[:, :max_len]
        elif waveform.shape[1] < max_len:
            pad_len = max_len - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, pad_len))
        
        mel_spec = T.MelSpectrogram(
            sample_rate=16000,
            n_fft=780,
            hop_length=195,
            n_mels=64
        )(waveform)
        mel_spec = T.AmplitudeToDB(top_db=80)(mel_spec)
        
        return mel_spec
    
    def analyze(self, audio_path):
        if not self.model_loaded:
            return None
        
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            input_tensor = self.preprocess(waveform, sample_rate)
            input_tensor = input_tensor.unsqueeze(0).to(self.device)
            
            imagenet_mean = torch.tensor([0.485]).view(1, 1, 1, 1)
            imagenet_std = torch.tensor([0.229]).view(1, 1, 1, 1)
            input_tensor = (input_tensor - imagenet_mean) / imagenet_std
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                confidence = torch.sigmoid(outputs).item()
            
            is_real = confidence >= 0.4
            return {
                'is_real': is_real,
                'confidence': confidence,
                'label': 'Real' if is_real else 'Fake'
            }
        except Exception as e:
            print(f"ML analysis error: {e}")
            return None
