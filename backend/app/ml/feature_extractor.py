"""
CyberSentric — Feature Extraction Engine
=========================================
Extracts numerical feature vectors from raw JSON log events for
the Isolation Forest anomaly detection model.

Each incoming log event is expected to be a dict like:
    {
        "timestamp": "2026-05-10T12:34:56",
        "user_id": "user42",
        "source_ip": "192.168.1.10",
        "action": "login",
        "status": "failed",
        "endpoint": "/api/auth/login",
        "input": "some payload text"
    }

The extractor maintains sliding-window statistics per user and per IP
to compute *behavioural* features that the ML model can learn from.
"""

import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional


class FeatureExtractor:
    """
    Stateful feature extractor that builds per-user and per-IP
    activity profiles over a configurable sliding window, then
    returns a fixed-length numeric feature vector for each event.

    Feature vector (14 dimensions):
    ────────────────────────────────
     0  request_count          — total requests in window
     1  failed_login_count     — failed login attempts in window
     2  unique_endpoints       — unique API endpoints hit
     3  payload_size           — length of the input payload (chars)
     4  time_delta_seconds     — seconds since previous request
     5  session_duration       — seconds between first and last request
     6  error_rate             — fraction of failed/error requests
     7  requests_per_minute    — request frequency
     8  payload_entropy        — Shannon entropy of the input string
     9  unique_ips_for_user    — how many different IPs this user used
    10  is_login_action        — 1.0 if action == "login", else 0.0
    11  is_failed_status       — 1.0 if status == "failed", else 0.0
    12  hour_of_day            — 0-23, normalised to 0-1
    13  special_char_ratio     — fraction of non-alphanumeric chars
    """

    WINDOW_MINUTES = 10  # sliding window for activity tracking
    FEATURE_NAMES = [
        "request_count", "failed_login_count", "unique_endpoints",
        "payload_size", "time_delta_seconds", "session_duration",
        "error_rate", "requests_per_minute", "payload_entropy",
        "unique_ips_for_user", "is_login_action", "is_failed_status",
        "hour_of_day", "special_char_ratio",
    ]
    NUM_FEATURES = len(FEATURE_NAMES)

    def __init__(self, window_minutes: int = 10):
        self.WINDOW_MINUTES = window_minutes
        # Per-user activity buffer:  user_id -> [event_dict, ...]
        self._user_activity: dict[str, list[dict]] = defaultdict(list)
        # Per-IP activity buffer:    ip -> [event_dict, ...]
        self._ip_activity: dict[str, list[dict]] = defaultdict(list)
        # Track which IPs a user has been seen on
        self._user_ips: dict[str, set[str]] = defaultdict(set)

    # ── public API ──────────────────────────────────────────────

    def extract(self, event: dict) -> list[float]:
        """
        Accept a raw log event dict and return a 14-dim feature vector.
        Also updates internal sliding-window state.
        """
        uid = event.get("user_id", "unknown")
        ip = event.get("source_ip", "unknown")
        now = self._parse_ts(event.get("timestamp"))

        # Build internal record
        record = {
            "timestamp": now,
            "action": event.get("action", "request"),
            "status": event.get("status", "success"),
            "endpoint": event.get("endpoint", "/"),
            "payload_size": len(str(event.get("input", ""))),
        }

        # Append and prune window
        self._user_activity[uid].append(record)
        self._ip_activity[ip].append(record)
        self._user_ips[uid].add(ip)
        self._prune(uid, ip, now)

        acts = self._user_activity[uid]
        payload_text = str(event.get("input", ""))

        # ── Compute each feature ────────────────────────────────
        request_count = float(len(acts))

        failed_login_count = float(sum(
            1 for a in acts
            if a["action"] == "login" and a["status"] == "failed"
        ))

        unique_endpoints = float(len(set(a["endpoint"] for a in acts)))

        payload_size = float(record["payload_size"])

        if len(acts) >= 2:
            time_delta = (acts[-1]["timestamp"] - acts[-2]["timestamp"]).total_seconds()
        else:
            time_delta = 60.0
        time_delta = max(time_delta, 0.01)

        if len(acts) >= 2:
            session_duration = (acts[-1]["timestamp"] - acts[0]["timestamp"]).total_seconds()
        else:
            session_duration = 0.0

        total = max(len(acts), 1)
        error_count = sum(1 for a in acts if a["status"] in ("failed", "error"))
        error_rate = error_count / total

        if session_duration > 0:
            requests_per_minute = (len(acts) / session_duration) * 60.0
        else:
            requests_per_minute = float(len(acts))

        payload_entropy = self._shannon_entropy(payload_text)

        unique_ips = float(len(self._user_ips.get(uid, set())))

        is_login = 1.0 if event.get("action") == "login" else 0.0
        is_failed = 1.0 if event.get("status") == "failed" else 0.0

        hour_of_day = now.hour / 23.0  # normalise 0-1

        special_char_ratio = self._special_char_ratio(payload_text)

        return [
            request_count,        # 0
            failed_login_count,   # 1
            unique_endpoints,     # 2
            payload_size,         # 3
            time_delta,           # 4
            session_duration,     # 5
            error_rate,           # 6
            requests_per_minute,  # 7
            payload_entropy,      # 8
            unique_ips,           # 9
            is_login,             # 10
            is_failed,            # 11
            hour_of_day,          # 12
            special_char_ratio,   # 13
        ]

    def get_feature_names(self) -> list[str]:
        return list(self.FEATURE_NAMES)

    # ── private helpers ─────────────────────────────────────────

    def _prune(self, uid: str, ip: str, now: datetime):
        """Remove events older than the sliding window."""
        cutoff = now - timedelta(minutes=self.WINDOW_MINUTES)
        self._user_activity[uid] = [
            a for a in self._user_activity[uid] if a["timestamp"] > cutoff
        ]
        self._ip_activity[ip] = [
            a for a in self._ip_activity[ip] if a["timestamp"] > cutoff
        ]

    @staticmethod
    def _parse_ts(ts) -> datetime:
        """Parse ISO timestamp string, or return current time."""
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
            except ValueError:
                pass
        return datetime.utcnow()

    @staticmethod
    def _shannon_entropy(text: str) -> float:
        """Compute Shannon entropy of a string (bits per character)."""
        if not text:
            return 0.0
        freq = Counter(text)
        length = len(text)
        entropy = -sum(
            (c / length) * math.log2(c / length) for c in freq.values()
        )
        return round(entropy, 4)

    @staticmethod
    def _special_char_ratio(text: str) -> float:
        """Fraction of non-alphanumeric, non-space characters."""
        if not text:
            return 0.0
        special = sum(1 for ch in text if not ch.isalnum() and ch != " ")
        return round(special / len(text), 4)
