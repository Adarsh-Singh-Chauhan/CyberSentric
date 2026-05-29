"""
CyberSentric — Analyzer Agent (ML-Powered)
============================================
The Analyzer Agent is the core intelligence layer of CyberSentric.
It replaces simple rule-based detection with a **real** machine learning
pipeline powered by Scikit-Learn's Isolation Forest algorithm.

Pipeline:
─────────
  1. Raw JSON log event comes in
  2. FeatureExtractor builds a 14-dim behavioural feature vector
  3. AnomalyDetector (Isolation Forest) scores it as normal/anomalous
  4. ThreatClassifier merges ML score + behavioral flags + defender
     results into a final structured threat output
  5. Structured result returned to Orchestrator

No dummy logic — this is a real, working ML inference pipeline
that trains on synthetic baseline data at startup, then continuously
retrains on live traffic for drift adaptation.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from app.agents.base_agent import AgentStatus, BaseAgent, Severity, ThreatResult
from app.ml.feature_extractor import FeatureExtractor
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.threat_classifier import ThreatClassifier
from app.ml.temporal_detector import TemporalAnomalyDetector


class AnalyzerAgent(BaseAgent):
    """
    ML-Powered Analyzer Agent.

    Uses:
      - FeatureExtractor:   converts raw logs → 14-dim feature vectors
      - AnomalyDetector:    Isolation Forest trained on normal baseline
      - ThreatClassifier:   merges ML + rules → structured threat output
    """

    def __init__(self):
        super().__init__("Analyzer")

        # ── ML Pipeline Components ──────────────────────────────
        self.feature_extractor = FeatureExtractor(window_minutes=10)
        self.anomaly_detector = AnomalyDetector()
        self.threat_classifier = ThreatClassifier()
        self.temporal_detector = TemporalAnomalyDetector()

        # ── Per-user/IP activity tracking (for behavioral flags) ─
        self._user_activity: dict[str, list[dict]] = defaultdict(list)
        self._ip_activity: dict[str, list[dict]] = defaultdict(list)

        # ── Statistics ──────────────────────────────────────────
        self.total_anomalies = 0
        self.total_clean = 0

    async def process(self, data: dict) -> ThreatResult:
        """
        Full ML analysis pipeline.

        Input:
            data dict with keys:
                - input: str
                - source_ip: str
                - user_id: str
                - action: str (e.g. "login", "request")
                - status: str (e.g. "success", "failed")
                - endpoint: str
                - defender_result: dict (optional, from Defender Agent)

        Output:
            ThreatResult with real ML-backed detection
        """
        self.status = AgentStatus.PROCESSING
        self.processed_count += 1

        uid = data.get("user_id", "unknown")
        ip = data.get("source_ip", "unknown")
        now = datetime.utcnow()

        # ── Step 0: Track activity for behavioral flags ─────────
        record = {
            "timestamp": now,
            "action": data.get("action", "request"),
            "status": data.get("status", "success"),
            "endpoint": data.get("endpoint", "/"),
        }
        self._user_activity[uid].append(record)
        self._ip_activity[ip].append(record)
        self._prune_activity(uid, ip, now)

        # ── Step 1: Feature Extraction ──────────────────────────
        event_log = {
            "timestamp": now.isoformat(),
            "user_id": uid,
            "source_ip": ip,
            "action": data.get("action", "request"),
            "status": data.get("status", "success"),
            "endpoint": data.get("endpoint", "/"),
            "input": data.get("input", ""),
        }
        features = self.feature_extractor.extract(event_log)

        # ── Step 2: ML Inference (Isolation Forest) ─────────────
        ml_result = self.anomaly_detector.predict(features)

        # ── Step 2.5: Temporal Inference (LSTM) ─────────────────
        temporal_result = self.temporal_detector.predict_sequence(ip, features)

        # ── Step 3: Behavioral Flags ────────────────────────────
        acts = self._user_activity.get(uid, [])
        behavioral_flags = {
            "failed_logins": sum(
                1 for a in acts
                if a["action"] == "login" and a["status"] == "failed"
            ),
            "request_count": len(self._ip_activity.get(ip, [])),
            "unique_endpoints": len(set(a["endpoint"] for a in acts)),
            "ip": ip,
            "user_id": uid,
            "temporal_anomaly": temporal_result.get("temporal_anomaly", False),
            "temporal_score": temporal_result.get("score", 0.0),
        }

        # ── Step 4: Defender results (if available) ─────────────
        defender_threats = []
        dr = data.get("defender_result")
        if dr and isinstance(dr, dict) and dr.get("threat_detected"):
            defender_threats.append({
                "type": dr.get("threat_type", "defender_alert"),
                "severity": dr.get("severity", "medium"),
                "confidence": dr.get("confidence", 0.7),
                "detail": dr.get("description", "Flagged by Defender Agent"),
            })

        # ── Step 5: Threat Classification ───────────────────────
        classification = self.threat_classifier.classify(
            ml_result=ml_result,
            defender_threats=defender_threats,
            behavioral_flags=behavioral_flags,
        )

        # ── Step 6: Map to ThreatResult ─────────────────────────
        threat_type = classification["threat"]
        severity_str = classification["severity"]
        confidence = classification["confidence"]

        try:
            severity = Severity(severity_str)
        except ValueError:
            severity = Severity.NONE

        threat_detected = severity != Severity.NONE

        # Build recommended actions from classifier
        actions = classification.get("recommended_actions", [])

        # Description
        description = classification.get("explanation", "No threats detected")

        # Update agent stats
        if threat_detected:
            self.threats_detected += 1
            self.total_anomalies += 1
            self.status = AgentStatus.ALERT
        else:
            self.total_clean += 1
            self.status = AgentStatus.IDLE

        # Emit event for Monitor/WebSocket
        self.emit_event(
            "analysis_complete",
            {
                "threat_type": threat_type,
                "severity": severity.value,
                "anomaly_score": ml_result.get("anomaly_score", 0.0),
                "ml_classification": ml_result.get("classification", "normal"),
                "confidence": confidence,
                "model_iterations": ml_result.get("train_iterations", 0),
            },
            severity=severity,
        )

        return ThreatResult(
            threat_detected=threat_detected,
            threat_type=threat_type,
            severity=severity,
            confidence=round(confidence, 3),
            description=description,
            source_ip=ip,
            user_id=uid,
            raw_input=str(data.get("input", ""))[:300],
            recommended_actions=actions,
            metadata={
                "anomaly_score": ml_result.get("anomaly_score", 0.0),
                "ml_prediction": ml_result.get("ml_prediction", "n/a"),
                "ml_classification": ml_result.get("classification", "normal"),
                "ml_confidence": ml_result.get("confidence", 0.0),
                "model_trained": ml_result.get("model_trained", False),
                "train_iterations": ml_result.get("train_iterations", 0),
                "behavioral_flags": behavioral_flags,
                "threats_detail": classification.get("threats_detail", []),
                "feature_vector": {
                    name: round(val, 4)
                    for name, val in zip(
                        self.feature_extractor.get_feature_names(),
                        features,
                    )
                },
            },
        )

    def get_status(self) -> dict:
        """Extended status including ML model info."""
        base = super().get_status()
        base["ml_model"] = self.anomaly_detector.get_model_info()
        base["temporal_model"] = self.temporal_detector.get_status()
        base["total_anomalies"] = self.total_anomalies
        base["total_clean"] = self.total_clean
        return base

    # ── helpers ──────────────────────────────────────────────────

    def _prune_activity(self, uid: str, ip: str, now: datetime):
        """Remove activity records older than 10 minutes."""
        cutoff = now - timedelta(minutes=10)
        self._user_activity[uid] = [
            a for a in self._user_activity[uid] if a["timestamp"] > cutoff
        ]
        self._ip_activity[ip] = [
            a for a in self._ip_activity[ip] if a["timestamp"] > cutoff
        ]
