"""
PyTorch Audio Deepfake Detector
Uses pretrained CRNN model from fraud-audio-detection
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models
import torchaudio
import torchaudio.transforms as T
import os

class AttentionPool(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.attn = nn.Linear(in_dim, 1)

    def forward(self, x):
        scores = self.attn(x)
        weights = F.softmax(scores, dim=1)
        return (weights * x).sum(dim=1)

class CRNNWithAttn(nn.Module):
    def __init__(self, pretrained=True, hidden_size=128, num_layers=1, dropout=0.2):
        super().__init__()
        if pretrained:
            resnet = models.resnet18(weights='DEFAULT')
        else:
            resnet = models.resnet18()
        
        w = resnet.conv1.weight.data.clone()
        resnet.conv1 = nn.Conv2d(2, 64, kernel_size=7, stride=2, padding=3, bias=False)
        resnet.conv1.weight.data[:, 0] = w[:, 0]
        self.backbone = nn.Sequential(*list(resnet.children())[:-2])

        self.gru = nn.GRU(
            input_size=512,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers>1 else 0.0
        )

        self.attn_pool = AttentionPool(hidden_size*2)

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size*2, hidden_size),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 1)
        )

    def forward(self, x):
        feat = self.backbone(x)
        feat = feat.mean(dim=2)
        feat = feat.permute(0,2,1)
        out, _ = self.gru(feat)
        pooled = self.attn_pool(out)
        return self.classifier(pooled)

class PyTorchAudioDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model_loaded = False
        self.load_model()
    
    def load_model(self):
        """Load pretrained PyTorch model"""
        model_path = '../fraud-audio-detection/models/best_model10.pth'
        
        if not os.path.exists(model_path):
            print(f"⚠️ PyTorch model not found: {model_path}")
            return
        
        try:
            self.model = CRNNWithAttn()
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model = self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            print("✅ PyTorch audio detector loaded")
        except Exception as e:
            print(f"❌ Error loading PyTorch model: {e}")
            self.model_loaded = False
    
    def preprocess(self, waveform, sample_rate):
        """Preprocess audio for model"""
        # Resample to 16kHz
        if sample_rate != 16000:
            resample = T.Resample(orig_freq=sample_rate, new_freq=16000)
            waveform = resample(waveform)
        
        # Mono to stereo
        if waveform.shape[0] == 1:
            waveform = waveform.repeat(2, 1)
        
        # Trim/pad to 4 seconds
        max_len = 16000 * 4
        if waveform.shape[1] > max_len:
            waveform = waveform[:, :max_len]
        elif waveform.shape[1] < max_len:
            pad_len = max_len - waveform.shape[1]
            waveform = torch.nn.functional.pad(waveform, (0, pad_len))
        
        # Convert to MelSpectrogram
        mel_spec = T.MelSpectrogram(
            sample_rate=16000,
            n_fft=780,
            hop_length=195,
            n_mels=64
        )(waveform)
        mel_spec = T.AmplitudeToDB(top_db=80)(mel_spec)
        
        # Normalize
        imagenet_mean = torch.tensor([0.485]).view(1, 1, 1, 1)
        imagenet_std = torch.tensor([0.229]).view(1, 1, 1, 1)
        mel_spec = mel_spec.unsqueeze(0)
        mel_spec = (mel_spec - imagenet_mean) / imagenet_std
        
        return mel_spec
    
    def predict(self, audio_path):
        """
        Predict if audio is real or fake
        Returns: dict with prediction results
        """
        if not self.model_loaded:
            return None
        
        try:
            # Load audio
            waveform, sample_rate = torchaudio.load(audio_path, backend="soundfile")
            
            # Preprocess
            input_tensor = self.preprocess(waveform, sample_rate)
            input_tensor = input_tensor.to(self.device)
            
            # Predict
            with torch.no_grad():
                output = self.model(input_tensor)
                probability = torch.sigmoid(output).item()
            
            # Threshold: > 0.4 = Real, <= 0.4 = Fake
            is_real = probability >= 0.4
            confidence = probability if is_real else (1 - probability)
            
            return {
                'is_fake': not is_real,
                'is_real': is_real,
                'confidence': confidence,
                'label': 'Real' if is_real else 'Fake/AI',
                'probability_real': probability,
                'probability_fake': 1 - probability,
                'model': 'PyTorch CRNN'
            }
            
        except Exception as e:
            print(f"PyTorch prediction error: {e}")
            return None

# Global instance
pytorch_detector = PyTorchAudioDetector()
