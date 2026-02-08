from typing import Dict, Any, Tuple, List
from modules.utils import get_logger

logger = get_logger(__name__)

class AnswerValidator:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.min_length = 50
        self.max_length = 5000

    def validate(self, answer: str, query: str, documents: List[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        issues = []
        score = 1.0

        length_valid, length_issues = self._validate_length(answer)
        if not length_valid:
            issues.extend(length_issues)
            score -= 0.2

        relevance_valid, relevance_issues = self._validate_relevance(answer, query)
        if not relevance_valid:
            issues.extend(relevance_issues)
            score -= 0.2

        if documents:
            grounding_valid, grounding_issues = self._validate_grounding(answer, documents)
            if not grounding_valid:
                issues.extend(grounding_issues)
                score -= 0.2

        structure_valid, structure_issues = self._validate_structure(answer)
        if not structure_valid:
            issues.extend(structure_issues)
            score -= 0.1

        quality_valid, quality_issues = self._validate_quality(answer)
        if not quality_valid:
            issues.extend(quality_issues)
            score -= 0.15

        final_score = max(score, 0.0)
        is_valid = len(issues) < 3 and final_score >= 0.5

        return is_valid, final_score, issues

    def _validate_length(self, answer: str) -> Tuple[bool, List[str]]:
        issues = []
        answer_length = len(answer)

        if answer_length < self.min_length:
            issues.append(f"Answer is too short ({answer_length} chars, minimum {self.min_length})")

        if answer_length > self.max_length:
            issues.append(f"Answer is too long ({answer_length} chars, maximum {self.max_length})")

        return len(issues) == 0, issues

    def _validate_relevance(self, answer: str, query: str) -> Tuple[bool, List[str]]:
        issues = []

        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())

        overlap = len(query_words & answer_words)
        expected_overlap = max(2, len(query_words) // 2)

        if overlap < expected_overlap:
            issues.append(f"Answer may not directly address the query (overlap: {overlap} words)")

        if answer.lower() == query.lower():
            issues.append("Answer is identical to query (not synthesized)")

        return len(issues) == 0, issues

    def _validate_grounding(self, answer: str, documents: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        issues = []

        combined_doc_text = " ".join([
            d.get("metadata", {}).get("content", "").lower()
            for d in documents
        ])

        answer_lower = answer.lower()
        sentences = [s.strip() for s in answer.split('.') if s.strip()]

        grounded_sentences = 0
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if self._is_grounded(sentence_lower, combined_doc_text):
                grounded_sentences += 1

        grounded_percentage = (grounded_sentences / len(sentences) * 100) if sentences else 0

        if grounded_percentage < 50:
            issues.append(f"Less than 50% of answer is grounded in source documents ({grounded_percentage:.0f}%)")

        return grounded_percentage >= 50, issues

    def _is_grounded(self, sentence: str, doc_text: str) -> bool:
        words = sentence.split()
        key_words = [w for w in words if len(w) > 3]

        if not key_words:
            return True

        matched = sum(1 for word in key_words if word in doc_text)
        return matched / len(key_words) > 0.3 if key_words else False

    def _validate_structure(self, answer: str) -> Tuple[bool, List[str]]:
        issues = []

        has_capital_start = answer[0].isupper() if answer else False
        has_sentence_end = answer.rstrip().endswith(('.', '!', '?')) if answer else False

        if not has_capital_start:
            issues.append("Answer should start with a capital letter")

        if not has_sentence_end:
            issues.append("Answer should end with proper punctuation")

        return len(issues) == 0, issues

    def _validate_quality(self, answer: str) -> Tuple[bool, List[str]]:
        issues = []

        repeated_words = self._check_repetition(answer)
        if repeated_words:
            issues.append(f"Excessive repetition detected: {', '.join(repeated_words[:3])}")

        if "um" in answer or "uh" in answer or "like" in answer:
            issues.append("Answer contains filler words")

        paragraph_count = len([p for p in answer.split('\n') if p.strip()])
        if paragraph_count == 0:
            issues.append("Answer lacks paragraph structure")

        return len(issues) == 0, issues

    def _check_repetition(self, answer: str) -> List[str]:
        words = answer.lower().split()
        word_counts = {}

        for word in words:
            if len(word) > 4:
                word_counts[word] = word_counts.get(word, 0) + 1

        return [word for word, count in word_counts.items() if count > 3]

    def get_quality_score_breakdown(self, answer: str, query: str,
                                    documents: List[Dict[str, Any]] = None) -> Dict[str, float]:
        _, length_score = self._score_component(self._validate_length(answer)[0])
        _, relevance_score = self._score_component(self._validate_relevance(answer, query)[0])
        _, quality_score = self._score_component(self._validate_quality(answer)[0])
        _, structure_score = self._score_component(self._validate_structure(answer)[0])

        grounding_score = 1.0
        if documents:
            _, grounding_score = self._score_component(self._validate_grounding(answer, documents)[0])

        return {
            "length": length_score,
            "relevance": relevance_score,
            "quality": quality_score,
            "structure": structure_score,
            "grounding": grounding_score,
            "overall": (length_score + relevance_score + quality_score + structure_score + grounding_score) / 5
        }

    def _score_component(self, is_valid: bool) -> Tuple[str, float]:
        return ("pass" if is_valid else "fail", 1.0 if is_valid else 0.0)
