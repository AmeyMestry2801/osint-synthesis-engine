"""
Evidence grounding to prevent LLM hallucinations
Every claim must cite a source
"""

from typing import Tuple, List, Dict, Any
from src.logging_config import get_logger

logger = get_logger(__name__)


class GroundingValidator:
    """Validates findings are grounded in evidence"""

    def validate_finding(
        self,
        assertion: str,
        evidence_chunks: List[str],
        confidence_threshold: float = 0.7
    ) -> Tuple[bool, float]:
        """
        Validate that a finding is grounded in evidence
        
        Returns:
            Tuple of (is_valid, confidence)
        """
        if not evidence_chunks:
            logger.warning(f"Finding has no evidence: {assertion}")
            return False, 0.0

        # Check that evidence supports assertion
        assertion_terms = self._extract_key_terms(assertion)
        evidence_text = " ".join(evidence_chunks)
        evidence_terms = self._extract_key_terms(evidence_text)

        # Calculate term overlap
        matching_terms = assertion_terms & evidence_terms
        overlap_ratio = len(matching_terms) / len(assertion_terms) if assertion_terms else 0.0

        is_grounded = overlap_ratio >= 0.5
        confidence = min(1.0, overlap_ratio + 0.2)

        if not is_grounded:
            logger.warning(f"Low grounding for: {assertion} (overlap: {overlap_ratio:.2%})")

        return is_grounded, confidence

    def filter_hallucinations(
        self,
        response_text: str,
        evidence_chunks: List[str]
    ) -> Tuple[str, List[str]]:
        """
        Filter out hallucinated claims from LLM response
        
        Returns:
            Tuple of (filtered_response, flagged_claims)
        """
        evidence_text = "\n".join(evidence_chunks)
        sentences = response_text.split(". ")

        filtered_sentences = []
        flagged_claims = []

        for sentence in sentences:
            is_grounded, _ = self.validate_finding(sentence, evidence_chunks)
            if is_grounded:
                filtered_sentences.append(sentence)
            else:
                logger.warning(f"Flagged hallucination: {sentence}")
                flagged_claims.append(sentence)

        filtered_response = ". ".join(filtered_sentences)
        return filtered_response, flagged_claims

    def _extract_key_terms(self, text: str) -> set:
        """Extract key terms from text"""
        import re
        terms = re.findall(r'\b[a-z]+\b', text.lower())
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as'
        }
        return {t for t in terms if t not in stopwords and len(t) > 2}


# Global instance
_grounding: GroundingValidator = None


def get_grounding_validator() -> GroundingValidator:
    """Get global grounding validator"""
    global _grounding
    if _grounding is None:
        _grounding = GroundingValidator()
    return _grounding