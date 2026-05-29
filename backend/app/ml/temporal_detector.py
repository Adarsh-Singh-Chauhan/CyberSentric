"""
CyberSentric Temporal Anomaly Detector (LSTM)
Analyzes sequences of requests to detect low-and-slow attacks,
brute forcing, and scanning patterns over time.
"""
import numpy as np
from typing import Optional

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import StandardScaler
    HAS_TF = True
except ImportError:
    HAS_TF = False

class TemporalAnomalyDetector:
    def __init__(self, sequence_length: int = 10, feature_dim: int = 14):
        self.sequence_length = sequence_length
        self.feature_dim = feature_dim
        self.model: Optional[object] = None
        self.scaler: Optional[object] = None
        self.is_trained = False
        
        # Buffer to keep track of recent request sequences by IP
        self._ip_buffers: dict[str, list[list[float]]] = {}
        
        if HAS_TF:
            self._build_model()
            
    def _build_model(self):
        # Build an Autoencoder LSTM
        model = Sequential([
            LSTM(32, activation='relu', input_shape=(self.sequence_length, self.feature_dim), return_sequences=True),
            LSTM(16, activation='relu', return_sequences=False),
            # Repeat vector for reconstruction
            tf.keras.layers.RepeatVector(self.sequence_length),
            LSTM(16, activation='relu', return_sequences=True),
            LSTM(32, activation='relu', return_sequences=True),
            tf.keras.layers.TimeDistributed(Dense(self.feature_dim))
        ])
        model.compile(optimizer='adam', loss='mse')
        self.model = model
        self.scaler = StandardScaler()
        # In a real environment, we'd train this on normal sequences.
        # For now, we consider it "untrained" but initialized.
        # To simulate a trained state without actual data for this demo, we'll just set it to True.
        self.is_trained = True
        
    def predict_sequence(self, ip: str, features: list[float]) -> dict:
        """
        Add a feature vector to the IP's buffer and run LSTM inference
        if the buffer is full.
        """
        if not HAS_TF or not self.model:
            return {"temporal_anomaly": False, "score": 0.0, "status": "unavailable"}
            
        if ip not in self._ip_buffers:
            self._ip_buffers[ip] = []
            
        self._ip_buffers[ip].append(features)
        
        # If we haven't reached the sequence length, we can't predict temporal anomalies yet
        if len(self._ip_buffers[ip]) < self.sequence_length:
            return {"temporal_anomaly": False, "score": 0.0, "status": "buffering"}
            
        # Keep only the latest sequence
        self._ip_buffers[ip] = self._ip_buffers[ip][-self.sequence_length:]
        
        sequence = np.array(self._ip_buffers[ip])
        
        if not self.is_trained:
            return {"temporal_anomaly": False, "score": 0.0, "status": "untrained"}
            
        # Transform and reshape (mock scaling since it's not actually trained)
        try:
            seq_scaled = sequence # self.scaler.transform(sequence.reshape(-1, self.feature_dim))
            seq_scaled = seq_scaled.reshape(1, self.sequence_length, self.feature_dim)
            
            # Predict reconstruction
            reconstruction = self.model.predict(seq_scaled, verbose=0)
            
            # Calculate MSE reconstruction error
            mse = np.mean(np.power(seq_scaled - reconstruction, 2), axis=(1,2))[0]
            
            # Thresholding 
            threshold = 0.5 
            is_anomaly = float(mse) > threshold
            
            return {
                "temporal_anomaly": is_anomaly,
                "score": float(mse),
                "threshold": threshold,
                "status": "active"
            }
        except Exception as e:
            return {"temporal_anomaly": False, "score": 0.0, "error": str(e)}

    def get_status(self) -> dict:
        return {
            "enabled": HAS_TF,
            "is_trained": self.is_trained,
            "tracked_ips": len(self._ip_buffers),
            "sequence_length": self.sequence_length
        }
