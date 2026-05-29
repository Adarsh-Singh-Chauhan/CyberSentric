"""
CyberSentric Defender Agent
Detects prompt injection, malicious inputs, and prevents LLM exploitation.
Uses pattern matching, heuristic scoring, and input sanitization.
"""
import re
import base64
import binascii
from typing import Optional

from app.agents.base_agent import (
    ActionResult,
    AgentStatus,
    BaseAgent,
    Severity,
    ThreatResult,
)


class DefenderAgent(BaseAgent):
    """
    Defender Agent — First line of defense.
    Responsibilities:
    - Detect prompt injection attacks
    - Identify malicious input patterns
    - Sanitize unsafe inputs
    - Prevent LLM exploitation attempts
    """

    # Known prompt injection patterns (regex)
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"ignore\s+(all\s+)?above\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior|above)",
        r"forget\s+(all\s+)?(previous|prior|above|your)\s+(instructions|rules|constraints)",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"act\s+as\s+(a|an)\s+",
        r"pretend\s+(you\s+are|to\s+be)\s+",
        r"new\s+instructions?\s*:",
        r"system\s*:\s*",
        r"<<\s*SYS\s*>>",
        r"\[INST\]",
        r"<\|im_start\|>",
        r"override\s+(security|safety|rules|restrictions)",
        r"bypass\s+(filter|safety|security|restriction)",
        r"jailbreak",
        r"DAN\s+mode",
        r"developer\s+mode\s+(enabled|on|activated)",
        r"do\s+anything\s+now",
    ]

    # Malicious payload patterns
    MALICIOUS_PATTERNS = [
        r"<script[\s>]",
        r"javascript\s*:",
        r"on(error|load|click|mouseover)\s*=",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__\s*\(",
        r"subprocess\.(run|call|Popen)",
        r"os\.system\s*\(",
        r"rm\s+-rf\s+/",
        r"DROP\s+TABLE",
        r";\s*DELETE\s+FROM",
        r"UNION\s+SELECT",
        r"OR\s+1\s*=\s*1",
        r"'\s*OR\s+'",
        r"--\s*$",
        r"/etc/passwd",
        r"\.\.\/\.\.\//",
        r"curl\s+.*(bash|sh)",
        r"wget\s+.*\|.*sh",
        r"base64\s*-d",
        r"\\x[0-9a-fA-F]{2}",
    ]

    # Suspicious keywords that raise concern
    SUSPICIOUS_KEYWORDS = [
        "hack", "exploit", "vulnerability", "payload", "backdoor",
        "reverse shell", "rootkit", "keylogger", "trojan", "malware",
        "ransomware", "phishing", "credential", "dump", "privilege escalation",
        "buffer overflow", "injection", "exfiltrate", "c2 server", "botnet",
    ]

    def __init__(self):
        super().__init__("Defender")
        self._compiled_injection = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._compiled_malicious = [re.compile(p, re.IGNORECASE) for p in self.MALICIOUS_PATTERNS]

    async def process(self, data: dict) -> ThreatResult:
        """
        Analyze input for prompt injection and malicious content.

        Args:
            data: dict with keys:
                - input: str — The user input to analyze
                - source_ip: Optional[str]
                - user_id: Optional[str]

        Returns:
            ThreatResult with detection details
        """
        self.status = AgentStatus.PROCESSING
        self.processed_count += 1

        user_input = data.get("input", "")
        source_ip = data.get("source_ip")
        user_id = data.get("user_id")

        # Try to decode base64 to catch obfuscated/jailbreak payloads
        decoded_input = user_input
        try:
            # Match base64 strings (roughly) and try decoding
            if len(user_input) > 10 and re.match(r'^[A-Za-z0-9+/]+={0,2}$', user_input.strip()):
                decoded_bytes = base64.b64decode(user_input.strip(), validate=True)
                decoded_input = decoded_bytes.decode('utf-8', errors='ignore')
        except (binascii.Error, ValueError):
            pass

        # Run all detection checks against both raw and decoded inputs
        injection_score = max(self._check_injection(user_input), self._check_injection(decoded_input))
        malicious_score = max(self._check_malicious(user_input), self._check_malicious(decoded_input))
        suspicious_score = max(self._check_suspicious(user_input), self._check_suspicious(decoded_input))
        entropy_score = self._check_entropy(user_input)

        # Aggregate threat score (weighted)
        total_score = (
            injection_score * 0.4
            + malicious_score * 0.3
            + suspicious_score * 0.15
            + entropy_score * 0.15
        )

        # Determine severity
        if total_score >= 0.8:
            severity = Severity.CRITICAL
        elif total_score >= 0.6:
            severity = Severity.HIGH
        elif total_score >= 0.35:
            severity = Severity.MEDIUM
        elif total_score >= 0.15:
            severity = Severity.LOW
        else:
            severity = Severity.NONE

        threat_detected = severity != Severity.NONE

        # Determine threat type
        threat_type = "none"
        if injection_score > 0.5:
            threat_type = "prompt_injection"
        elif malicious_score > 0.5:
            threat_type = "malicious_payload"
        elif suspicious_score > 0.5:
            threat_type = "suspicious_content"
        elif entropy_score > 0.7:
            threat_type = "obfuscated_input"
        elif threat_detected:
            threat_type = "suspicious_input"

        # Build recommended actions
        actions = []
        if severity in (Severity.CRITICAL, Severity.HIGH):
            actions.extend(["block_input", "alert_admin", "log_incident"])
            if source_ip:
                actions.append("rate_limit_ip")
        elif severity == Severity.MEDIUM:
            actions.extend(["sanitize_input", "log_warning"])
        elif severity == Severity.LOW:
            actions.append("log_info")

        # Sanitize the input
        sanitized = self._sanitize_input(user_input) if threat_detected else user_input

        # Build description
        desc_parts = []
        if injection_score > 0.3:
            desc_parts.append(f"Prompt injection detected (score: {injection_score:.2f})")
        if malicious_score > 0.3:
            desc_parts.append(f"Malicious payload detected (score: {malicious_score:.2f})")
        if suspicious_score > 0.3:
            desc_parts.append(f"Suspicious keywords found (score: {suspicious_score:.2f})")
        if entropy_score > 0.5:
            desc_parts.append(f"High entropy / obfuscation (score: {entropy_score:.2f})")

        description = "; ".join(desc_parts) if desc_parts else "Input appears safe"

        if threat_detected:
            self.threats_detected += 1
            self.status = AgentStatus.ALERT
            self.emit_event(
                "threat_detected",
                {"threat_type": threat_type, "severity": severity.value, "score": round(total_score, 3)},
                severity=severity,
            )
        else:
            self.status = AgentStatus.IDLE
            self.emit_event("input_cleared", {"score": round(total_score, 3)})

        return ThreatResult(
            threat_detected=threat_detected,
            threat_type=threat_type,
            severity=severity,
            confidence=round(min(total_score * 1.2, 1.0), 3),
            description=description,
            source_ip=source_ip,
            user_id=user_id,
            raw_input=user_input[:500],  # Truncate for safety
            sanitized_input=sanitized[:500],
            recommended_actions=actions,
            metadata={
                "injection_score": round(injection_score, 3),
                "malicious_score": round(malicious_score, 3),
                "suspicious_score": round(suspicious_score, 3),
                "entropy_score": round(entropy_score, 3),
                "total_score": round(total_score, 3),
            },
        )

    def _check_injection(self, text: str) -> float:
        """Check for prompt injection patterns. Returns 0.0-1.0 score."""
        if not text:
            return 0.0

        matches = 0
        for pattern in self._compiled_injection:
            if pattern.search(text):
                matches += 1

        # Normalize: each match contributes significantly
        if matches >= 3:
            return 1.0
        elif matches >= 2:
            return 0.85
        elif matches >= 1:
            return 0.65
        return 0.0

    def _check_malicious(self, text: str) -> float:
        """Check for malicious payloads (XSS, SQL injection, command injection)."""
        if not text:
            return 0.0

        matches = 0
        for pattern in self._compiled_malicious:
            if pattern.search(text):
                matches += 1

        if matches >= 3:
            return 1.0
        elif matches >= 2:
            return 0.8
        elif matches >= 1:
            return 0.6
        return 0.0

    def _check_suspicious(self, text: str) -> float:
        """Check for suspicious cybersecurity-related keywords."""
        if not text:
            return 0.0

        text_lower = text.lower()
        found = sum(1 for kw in self.SUSPICIOUS_KEYWORDS if kw in text_lower)

        if found >= 5:
            return 1.0
        elif found >= 3:
            return 0.7
        elif found >= 2:
            return 0.45
        elif found >= 1:
            return 0.2
        return 0.0

    def _check_entropy(self, text: str) -> float:
        """
        Check for high entropy (possible obfuscation/encoding).
        High entropy in short strings suggests encoded/obfuscated payloads.
        """
        if not text or len(text) < 10:
            return 0.0

        import math
        from collections import Counter

        # Character frequency
        freq = Counter(text)
        length = len(text)
        entropy = -sum((c / length) * math.log2(c / length) for c in freq.values())

        # Normalize entropy (max for ASCII is about 6.6)
        normalized = entropy / 6.6

        # High entropy in short strings is more suspicious
        if length < 50 and normalized > 0.85:
            return 0.8
        elif normalized > 0.9:
            return 0.7
        elif normalized > 0.8:
            return 0.4
        return 0.0

    def _sanitize_input(self, text: str) -> str:
        """Sanitize potentially dangerous input recursively."""
        sanitized = text
        previous = ""
        # Recursive replacement for nested HTML/script tags
        while sanitized != previous:
            previous = sanitized
            # Remove script tags
            sanitized = re.sub(r"<script[^>]*>.*?</script>", "[REMOVED]", sanitized, flags=re.IGNORECASE | re.DOTALL)
            # Remove HTML tags
            sanitized = re.sub(r"<[^>]+>", "", sanitized)

        # Remove common injection markers
        sanitized = re.sub(r"(javascript|on\w+)\s*:", "[BLOCKED]:", sanitized, flags=re.IGNORECASE)
        # Remove SQL injection patterns
        sanitized = re.sub(r"(UNION\s+SELECT|DROP\s+TABLE|DELETE\s+FROM)", "[SQL_BLOCKED]", sanitized, flags=re.IGNORECASE)
        # Remove command injection
        sanitized = re.sub(r"(eval|exec|__import__|subprocess|os\.system)\s*\(", "[CMD_BLOCKED](", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()
