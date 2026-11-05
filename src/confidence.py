"""
Confidence scoring and human-in-the-loop gates
"""

from typing import Dict, Tuple, Any
from enum import Enum
from src.logging_config import get_logger

logger = get_logger(__name__)


class ConfidenceTier(str, Enum):
    """Confidence tiers"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConfidenceCalculator:
    """Calculate confidence scores for findings"""

    def __init__(self):
        self.high_threshold = 0.85
        self.medium_threshold = 0.70
        self.low_threshold = 0.50

    def calculate_confidence(
        self,
        evidence_confidences: list,
        reasoning_quality: float = 0.9
    ) -> Tuple[float, ConfidenceTier]:
        """
        Calculate overall confidence for a finding
        
        Returns:
            Tuple of (confidence_score, confidence_tier)
        """
        if not evidence_confidences:
            return 0.0, ConfidenceTier.LOW

        # Average evidence confidences
        avg_confidence = sum(evidence_confidences) / len(evidence_confidences)

        # Apply reasoning quality modifier
        final_confidence = avg_confidence * reasoning_quality

        # Clamp to 0-1
        final_confidence = min(1.0, max(0.0, final_confidence))

        # Determine tier
        if final_confidence >= self.high_threshold:
            tier = ConfidenceTier.HIGH
        elif final_confidence >= self.medium_threshold:
            tier = ConfidenceTier.MEDIUM
        else:
            tier = ConfidenceTier.LOW

        logger.info(f"Confidence: {final_confidence:.2%} ({tier.value})")
        return final_confidence, tier

    def confidence_to_risk_level(
        self,
        confidence: float,
        severity: str = "medium"
    ) -> RiskLevel:
        """
        Convert confidence + severity to risk level
        """
        severity_scores = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8,
            "critical": 1.0
        }

        severity_score = severity_scores.get(severity, 0.5)
        risk_score = (confidence + severity_score) / 2

        if risk_score >= 0.75:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            return RiskLevel.HIGH
        elif risk_score >= 0.25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


class ConfidenceGate:
    """Applies confidence-based triage gates"""

    def __init__(self):
        self.high_threshold = 0.85
        self.medium_threshold = 0.70

    def triage_finding(self, confidence: float) -> Dict[str, Any]:
        """
        Triage a finding based on confidence
        
        Returns:
            Dict with routing decision
        """
        if confidence >= self.high_threshold:
            return {
                "status": "auto_approve",
                "confidence_tier": ConfidenceTier.HIGH,
                "requires_review": False,
                "reason": "High confidence - auto-approved"
            }
        elif confidence >= self.medium_threshold:
            return {
                "status": "analyst_review",
                "confidence_tier": ConfidenceTier.MEDIUM,
                "requires_review": True,
                "reason": "Medium confidence - queue for analyst review",
                "priority": "medium"
            }
        else:
            return {
                "status": "high_priority_review",
                "confidence_tier": ConfidenceTier.LOW,
                "requires_review": True,
                "reason": "Low confidence - high priority review",
                "priority": "high"
            }

    def should_auto_approve(self, confidence: float) -> bool:
        """Check if finding should auto-approve"""
        return confidence >= self.high_threshold


# Global instances
_confidence_calculator: ConfidenceCalculator = None
_confidence_gate: ConfidenceGate = None


def get_confidence_calculator() -> ConfidenceCalculator:
    """Get global confidence calculator"""
    global _confidence_calculator
    if _confidence_calculator is None:
        _confidence_calculator = ConfidenceCalculator()
    return _confidence_calculator


def get_confidence_gate() -> ConfidenceGate:
    """Get global confidence gate"""
    global _confidence_gate
    if _confidence_gate is None:
        _confidence_gate = ConfidenceGate()
    return _confidence_gate