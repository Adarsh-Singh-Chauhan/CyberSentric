"""
CyberSentric — Threat Classifier
==================================
Maps ML anomaly scores + defender heuristic results into
final structured threat classifications.

This module bridges the gap between raw ML output and the
actionable threat response the system needs. It combines:
  - Isolation Forest anomaly score
  - Defender Agent's rule-based detection
  - Behavioral pattern analysis

Output format:
    {
        "threat": "brute_force",
        "severity": "high",
        "confidence": 0.92,
        "threat_category": "authentication_attack",
        "recommended_actions": ["block_ip", "alert_admin"],
        "explanation": "Multiple failed login attempts detected..."
    }
"""


class ThreatClassifier:
    """
    Takes combined analysis results and produces the final
    structured threat classification.
    """

    # Threat type → category mapping
    THREAT_CATEGORIES = {
        "brute_force": "authentication_attack",
        "credential_stuffing": "authentication_attack",
        "ml_anomaly": "behavioral_anomaly",
        "rate_abuse": "denial_of_service",
        "endpoint_scanning": "reconnaissance",
        "prompt_injection": "ai_exploitation",
        "malicious_payload": "code_injection",
        "xss": "code_injection",
        "sqli": "code_injection",
        "suspicious_content": "social_engineering",
        "obfuscated_input": "evasion_technique",
        "blocked_ip": "repeat_offender",
        "none": "clean",
    }

    # Severity → numeric weight for merging
    SEVERITY_WEIGHT = {
        "none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4
    }

    @classmethod
    def classify(
        cls,
        ml_result: dict,
        defender_threats: list[dict],
        behavioral_flags: dict,
    ) -> dict:
        """
        Produce final structured threat output.

        Args:
            ml_result: output from AnomalyDetector.predict()
            defender_threats: list of threat dicts from DefenderAgent
            behavioral_flags: {
                "failed_logins": int,
                "request_count": int,
                "unique_endpoints": int,
                "ip": str,
                "user_id": str,
            }
        Returns:
            Structured threat dict
        """
        threats_found = []
        anomaly_score = ml_result.get("anomaly_score", 0.0)
        ml_class = ml_result.get("classification", "normal")

        # ── 1. ML-based anomaly ─────────────────────────────────
        if ml_class == "high_threat":
            threats_found.append({
                "type": "ml_anomaly",
                "severity": "critical" if anomaly_score >= 0.80 else "high",
                "confidence": ml_result.get("confidence", 0.0),
                "detail": f"Isolation Forest anomaly — score {anomaly_score:.3f}",
            })
        elif ml_class == "suspicious":
            threats_found.append({
                "type": "ml_anomaly",
                "severity": "medium",
                "confidence": ml_result.get("confidence", 0.0),
                "detail": f"Suspicious pattern detected — score {anomaly_score:.3f}",
            })

        # ── 2. Behavioural pattern detection ────────────────────
        failed_logins = behavioral_flags.get("failed_logins", 0)
        request_count = behavioral_flags.get("request_count", 0)
        unique_eps = behavioral_flags.get("unique_endpoints", 0)

        if failed_logins >= 10:
            threats_found.append({
                "type": "brute_force",
                "severity": "critical",
                "confidence": min(0.5 + failed_logins * 0.04, 0.99),
                "detail": f"{failed_logins} failed logins detected — active brute force",
            })
        elif failed_logins >= 5:
            threats_found.append({
                "type": "brute_force",
                "severity": "high",
                "confidence": min(0.5 + failed_logins * 0.05, 0.95),
                "detail": f"{failed_logins} failed logins — possible brute force attempt",
            })

        if request_count >= 100:
            threats_found.append({
                "type": "rate_abuse",
                "severity": "high",
                "confidence": min(0.6 + request_count * 0.002, 0.95),
                "detail": f"{request_count} requests in 10min window — rate abuse",
            })

        if unique_eps >= 20:
            threats_found.append({
                "type": "endpoint_scanning",
                "severity": "high",
                "confidence": min(0.5 + unique_eps * 0.02, 0.95),
                "detail": f"{unique_eps} unique endpoints accessed — recon scanning",
            })

        # ── 3. Defender rule-based threats ──────────────────────
        for dt in defender_threats:
            threats_found.append({
                "type": dt.get("type", "defender_alert"),
                "severity": dt.get("severity", "medium"),
                "confidence": dt.get("confidence", 0.7),
                "detail": dt.get("detail", "Flagged by Defender Agent"),
            })

        # ── 4. If nothing found, it's clean ─────────────────────
        if not threats_found:
            return {
                "threat": "none",
                "severity": "none",
                "confidence": round(max(0.0, 1.0 - anomaly_score), 3),
                "threat_category": "clean",
                "recommended_actions": [],
                "explanation": "No threats detected — input is clean",
                "anomaly_score": round(anomaly_score, 4),
                "threats_detail": [],
            }

        # ── 5. Pick the worst threat as the primary ─────────────
        worst = max(
            threats_found,
            key=lambda t: cls.SEVERITY_WEIGHT.get(t["severity"], 0)
        )

        # Build recommended actions based on severity
        severity = worst["severity"]
        actions = cls._get_actions(severity, behavioral_flags.get("ip"))

        return {
            "threat": worst["type"],
            "severity": severity,
            "confidence": round(worst["confidence"], 3),
            "threat_category": cls.THREAT_CATEGORIES.get(
                worst["type"], "unknown"
            ),
            "recommended_actions": actions,
            "explanation": " | ".join(t["detail"] for t in threats_found),
            "anomaly_score": round(anomaly_score, 4),
            "threats_detail": threats_found,
        }

    @staticmethod
    def _get_actions(severity: str, ip: str = None) -> list[str]:
        """Generate recommended response actions based on severity."""
        if severity in ("critical", "high"):
            actions = ["block_ip", "alert_admin", "log_critical",
                       "increase_monitoring"]
            if ip:
                actions.append("rate_limit_ip")
            return actions
        elif severity == "medium":
            return ["rate_limit", "sanitize_input", "log_warning"]
        elif severity == "low":
            return ["log_info"]
        return []
