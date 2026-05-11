"""
CyberSentric — Anomaly Detection Model (Isolation Forest)
==========================================================
A *real*, production-grade anomaly detection pipeline that:

1. Generates realistic synthetic training data simulating normal
   network behaviour AND known attack patterns.
2. Trains a Scikit-Learn Isolation Forest model on the normal
   baseline data so it learns what "normal" looks like.
3. Provides real-time inference — given a feature vector, returns
   an anomaly score, a threat classification, and confidence.

Threat Classification Logic:
────────────────────────────
  anomaly_score >= 0.60  →  "high_threat"   (critical / high severity)
  anomaly_score >= 0.35  →  "suspicious"    (medium severity)
  anomaly_score <  0.35  →  "normal"        (no threat)

The model auto-retrains itself incrementally as real traffic
flows in, keeping the last 2000 feature vectors and retraining
every 200 new samples to adapt to traffic drift.
"""

import numpy as np
from datetime import datetime
from typing import Optional

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class AnomalyDetector:
    """
    Wraps Scikit-Learn's Isolation Forest with:
    - Synthetic data generation for initial training
    - StandardScaler normalisation
    - Continuous online retraining
    - Structured threat classification output
    """

    # ── classification thresholds ───────────────────────────────
    THRESHOLD_HIGH = 0.60     # anomaly_score >= this → high_threat
    THRESHOLD_SUSPICIOUS = 0.35  # anomaly_score >= this → suspicious

    # ── online retraining config ────────────────────────────────
    RETRAIN_INTERVAL = 200    # retrain after every N new samples
    MAX_HISTORY = 2000        # keep at most this many feature vectors

    def __init__(self):
        self.model: Optional[object] = None
        self.scaler: Optional[object] = None
        self.is_trained = False
        self._feature_history: list[list[float]] = []
        self._samples_since_retrain = 0
        self._train_count = 0

        if HAS_SKLEARN:
            self._build_and_train()

    # ── public API ──────────────────────────────────────────────

    def predict(self, features: list[float]) -> dict:
        """
        Run inference on a single feature vector.

        Args:
            features: list of 14 floats from FeatureExtractor.extract()

        Returns:
            {
                "anomaly_score": float,      # 0.0 (normal) to 1.0 (anomalous)
                "classification": str,       # "normal" | "suspicious" | "high_threat"
                "confidence": float,         # 0.0 to 1.0
                "ml_prediction": str,        # "anomaly" | "normal"
                "model_trained": bool,
                "train_iterations": int
            }
        """
        # Store for online retraining
        self._feature_history.append(features)
        if len(self._feature_history) > self.MAX_HISTORY:
            self._feature_history = self._feature_history[-self.MAX_HISTORY:]
        self._samples_since_retrain += 1

        # Auto-retrain periodically
        if (self._samples_since_retrain >= self.RETRAIN_INTERVAL
                and len(self._feature_history) >= 100):
            self._retrain()

        if not self.is_trained or not self.model:
            return {
                "anomaly_score": 0.0,
                "classification": "normal",
                "confidence": 0.0,
                "ml_prediction": "unavailable",
                "model_trained": False,
                "train_iterations": self._train_count,
            }

        # Scale the features
        X = np.array([features])
        X_scaled = self.scaler.transform(X)

        # Isolation Forest: predict returns  1 = normal, -1 = anomaly
        prediction = self.model.predict(X_scaled)[0]

        # decision_function: higher = more normal, lower = more anomalous
        # We negate it so higher = more anomalous
        raw_score = -self.model.decision_function(X_scaled)[0]

        # Normalise to 0-1 range using sigmoid-like mapping
        anomaly_score = self._normalise_score(raw_score)

        # Classify
        if anomaly_score >= self.THRESHOLD_HIGH:
            classification = "high_threat"
        elif anomaly_score >= self.THRESHOLD_SUSPICIOUS:
            classification = "suspicious"
        else:
            classification = "normal"

        # Confidence: how sure are we?
        if classification == "normal":
            confidence = max(0.0, 1.0 - anomaly_score)
        else:
            confidence = min(anomaly_score + 0.1, 0.99)

        return {
            "anomaly_score": round(anomaly_score, 4),
            "classification": classification,
            "confidence": round(confidence, 4),
            "ml_prediction": "anomaly" if prediction == -1 else "normal",
            "model_trained": True,
            "train_iterations": self._train_count,
        }

    def get_model_info(self) -> dict:
        """Return model metadata for the dashboard."""
        return {
            "algorithm": "IsolationForest",
            "library": "scikit-learn",
            "is_trained": self.is_trained,
            "train_iterations": self._train_count,
            "samples_in_history": len(self._feature_history),
            "samples_since_retrain": self._samples_since_retrain,
            "thresholds": {
                "high_threat": self.THRESHOLD_HIGH,
                "suspicious": self.THRESHOLD_SUSPICIOUS,
            },
            "sklearn_available": HAS_SKLEARN,
        }

    # ── training ────────────────────────────────────────────────

    def _build_and_train(self):
        """Build the model and train on synthetic baseline data."""
        normal_data = self._generate_normal_data(800)
        attack_data = self._generate_attack_data(80)
        # We train ONLY on normal data — Isolation Forest is unsupervised
        # It learns what "normal" looks like, everything else is anomalous.
        train_data = normal_data

        self.scaler = StandardScaler()
        X_train = self.scaler.fit_transform(np.array(train_data))

        self.model = IsolationForest(
            n_estimators=150,       # number of decision trees
            max_samples="auto",     # samples per tree
            contamination=0.08,     # expected fraction of anomalies
            max_features=1.0,       # use all features per tree
            random_state=42,
            n_jobs=-1,              # use all CPU cores
        )
        self.model.fit(X_train)
        self.is_trained = True
        self._train_count = 1
        self._feature_history = list(train_data)  # seed history
        self._samples_since_retrain = 0

    def _retrain(self):
        """Incrementally retrain on accumulated real data."""
        if not HAS_SKLEARN or len(self._feature_history) < 100:
            return
        try:
            X = np.array(self._feature_history)
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self.model = IsolationForest(
                n_estimators=150,
                contamination=0.08,
                max_features=1.0,
                random_state=42,
                n_jobs=-1,
            )
            self.model.fit(X_scaled)
            self.is_trained = True
            self._train_count += 1
            self._samples_since_retrain = 0
        except Exception:
            pass  # never crash on retrain failure

    # ── synthetic data generation ───────────────────────────────

    @staticmethod
    def _generate_normal_data(n: int = 800) -> list[list[float]]:
        """
        Generate realistic *normal* network traffic feature vectors.
        Each vector matches the 14-feature layout from FeatureExtractor.
        """
        rng = np.random.RandomState(42)
        data = []
        for _ in range(n):
            data.append([
                rng.exponential(3.0),            # 0  request_count (low)
                0.0,                              # 1  failed_login_count (none)
                rng.randint(1, 8),                # 2  unique_endpoints (few)
                np.clip(rng.normal(200, 80), 10, 800), # 3  payload_size (moderate)
                rng.exponential(30.0),            # 4  time_delta_seconds (spaced out)
                np.clip(rng.normal(120, 60), 0, 600), # 5  session_duration
                rng.beta(1, 20),                  # 6  error_rate (very low)
                np.clip(rng.normal(2.0, 1.0), 0.1, 8), # 7  requests_per_minute
                np.clip(rng.normal(3.5, 0.8), 1, 6),  # 8  payload_entropy (normal text)
                1.0,                              # 9  unique_ips (1 IP per user)
                rng.choice([0.0, 1.0], p=[0.85, 0.15]),  # 10 is_login
                0.0,                              # 11 is_failed (no failures)
                rng.randint(8, 22) / 23.0,        # 12 hour_of_day (business hours)
                rng.beta(2, 20),                  # 13 special_char_ratio (low)
            ])
        return data

    @staticmethod
    def _generate_attack_data(n: int = 80) -> list[list[float]]:
        """
        Generate simulated *attack* traffic for validation.
        These represent brute force, scanning, injection attempts, etc.
        """
        rng = np.random.RandomState(99)
        data = []
        for i in range(n):
            attack_type = i % 4  # cycle through 4 attack patterns

            if attack_type == 0:  # Brute force login
                data.append([
                    rng.randint(30, 100),         # 0  high request count
                    rng.randint(8, 50),            # 1  many failed logins!
                    1.0,                           # 2  single endpoint (login)
                    np.clip(rng.normal(50, 20), 10, 100), # 3  small payloads
                    rng.exponential(0.5),          # 4  very fast requests
                    np.clip(rng.normal(30, 10), 5, 60), # 5  short session
                    rng.uniform(0.7, 1.0),         # 6  very high error rate
                    rng.uniform(20, 100),          # 7  very high req/min
                    np.clip(rng.normal(2.5, 0.5), 1, 4), # 8  low entropy (passwords)
                    1.0,                           # 9  single IP
                    1.0,                           # 10 login action
                    1.0,                           # 11 failed status
                    rng.randint(0, 6) / 23.0,      # 12 odd hours
                    rng.beta(2, 20),               # 13 low special chars
                ])

            elif attack_type == 1:  # Endpoint scanning / recon
                data.append([
                    rng.randint(40, 120),          # 0  many requests
                    0.0,                           # 1  no login attempts
                    rng.randint(15, 50),           # 2  MANY unique endpoints!
                    np.clip(rng.normal(100, 30), 20, 300), # 3  varied payloads
                    rng.exponential(0.3),          # 4  very rapid
                    np.clip(rng.normal(60, 20), 10, 120), # 5  moderate session
                    rng.uniform(0.3, 0.8),         # 6  moderate-high errors
                    rng.uniform(15, 80),           # 7  high req/min
                    np.clip(rng.normal(3.0, 0.5), 1, 5), # 8  normal entropy
                    rng.randint(1, 5),             # 9  maybe multiple IPs
                    0.0,                           # 10 not login
                    0.0,                           # 11 not failed
                    rng.randint(0, 5) / 23.0,      # 12 late night
                    rng.beta(3, 10),               # 13 some special chars
                ])

            elif attack_type == 2:  # Injection attack (SQLi / XSS)
                data.append([
                    rng.randint(5, 30),            # 0  moderate requests
                    0.0,                           # 1  no login
                    rng.randint(2, 8),             # 2  few endpoints
                    np.clip(rng.normal(600, 200), 200, 2000), # 3  LARGE payloads!
                    rng.exponential(5.0),          # 4  moderate timing
                    np.clip(rng.normal(90, 30), 10, 300), # 5  longer session
                    rng.uniform(0.1, 0.4),         # 6  some errors
                    rng.uniform(3, 15),            # 7  moderate req/min
                    np.clip(rng.normal(5.5, 0.5), 4, 7), # 8  HIGH entropy!
                    1.0,                           # 9  single IP
                    0.0,                           # 10 not login
                    0.0,                           # 11 not failed
                    rng.randint(0, 23) / 23.0,     # 12 any hour
                    rng.uniform(0.15, 0.5),        # 13 HIGH special chars!
                ])

            else:  # Rate abuse / DDoS-like
                data.append([
                    rng.randint(80, 200),          # 0  VERY high request count
                    0.0,                           # 1  no login
                    rng.randint(1, 5),             # 2  few endpoints
                    np.clip(rng.normal(150, 50), 50, 400), # 3  moderate payload
                    rng.exponential(0.1),          # 4  extremely fast!
                    np.clip(rng.normal(20, 10), 5, 60), # 5  short session
                    rng.uniform(0.0, 0.2),         # 6  low error rate
                    rng.uniform(50, 200),          # 7  EXTREME req/min
                    np.clip(rng.normal(3.0, 0.5), 1, 5), # 8  normal entropy
                    rng.randint(1, 10),            # 9  maybe many IPs
                    0.0,                           # 10 not login
                    0.0,                           # 11 not failed
                    rng.randint(0, 23) / 23.0,     # 12 any hour
                    rng.beta(2, 15),               # 13 low special chars
                ])

        return data

    # ── helpers ──────────────────────────────────────────────────

    @staticmethod
    def _normalise_score(raw: float) -> float:
        """
        Convert the raw Isolation Forest decision score to a 0-1 range.
        Uses a shifted sigmoid to map the score smoothly.
        """
        import math
        # raw > 0 means more anomalous (we already negated decision_function)
        # Sigmoid mapping: 1 / (1 + exp(-k * x))
        k = 5.0   # steepness
        try:
            return round(1.0 / (1.0 + math.exp(-k * raw)), 4)
        except OverflowError:
            return 1.0 if raw > 0 else 0.0
