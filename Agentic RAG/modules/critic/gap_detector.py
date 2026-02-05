from typing import List, Dict, Any
from modules.utils import get_logger, QueryHelper

logger = get_logger(__name__)

class GapDetector:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.gap_keywords = {
            "temporal": ["when", "date", "time", "period", "year", "month"],
            "spatial": ["where", "location", "place", "region", "area"],
            "causal": ["why", "reason", "cause", "because"],
            "procedural": ["how", "steps", "process", "method"],
            "comparative": ["versus", "comparison", "difference", "better"],
            "quantitative": ["how many", "how much", "quantity", "number"],
            "definition": ["what", "define", "meaning", "concept"]
        }

    def detect(self, query: str, documents: List[Dict[str, Any]]) -> List[str]:
        identified_gaps = []

        query_lower = query.lower()
        content = self._combine_content(documents)
        content_lower = content.lower()

        for gap_type, keywords in self.gap_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    if self._is_gap_present(keyword, content_lower):
                        identified_gaps.append(f"{gap_type}_gap: missing {keyword} information")

        specific_gaps = self._detect_specific_gaps(query, documents)
        identified_gaps.extend(specific_gaps)

        self.logger.info(f"Detected {len(identified_gaps)} gaps")
        return list(set(identified_gaps))

    def _combine_content(self, documents: List[Dict[str, Any]]) -> str:
        contents = []
        for doc in documents:
            content = doc.get("metadata", {}).get("content", "")
            if content:
                contents.append(content)
        return " ".join(contents)

    def _is_gap_present(self, keyword: str, content: str) -> bool:
        direct_presence = keyword in content

        if direct_presence:
            return False

        synonym_map = {
            "when": ["date", "time", "year", "month", "period"],
            "where": ["location", "place", "region", "area"],
            "why": ["reason", "cause", "because"],
            "how": ["steps", "process", "method"],
            "what": ["definition", "meaning", "concept"]
        }

        if keyword in synonym_map:
            for synonym in synonym_map[keyword]:
                if synonym in content:
                    return False

        return True

    def _detect_specific_gaps(self, query: str, documents: List[Dict[str, Any]]) -> List[str]:
        gaps = []
        query_keywords = QueryHelper.extract_keywords(query)
        content = self._combine_content(documents).lower()

        uncovered_keywords = [
            kw for kw in query_keywords
            if kw.lower() not in content
        ]

        if uncovered_keywords:
            gaps.append(f"keyword_coverage_gap: {len(uncovered_keywords)} query keywords not found")

        if len(documents) < 3:
            gaps.append("coverage_gap: insufficient document count for comprehensive answer")

        avg_doc_length = sum(len(d.get("metadata", {}).get("content", "").split())
                            for d in documents) / len(documents) if documents else 0

        if avg_doc_length < 50:
            gaps.append("depth_gap: documents may lack sufficient detail")

        return gaps

    def quantify_gaps(self, query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        gaps = self.detect(query, documents)

        gap_count = len(gaps)
        gap_types = {}

        for gap in gaps:
            gap_type = gap.split(":")[0]
            gap_types[gap_type] = gap_types.get(gap_type, 0) + 1

        gap_severity = self._calculate_severity(gaps)

        return {
            "total_gaps": gap_count,
            "gap_types": gap_types,
            "severity": gap_severity,
            "gaps": gaps
        }

    def _calculate_severity(self, gaps: List[str]) -> str:
        if len(gaps) == 0:
            return "none"
        elif len(gaps) <= 2:
            return "low"
        elif len(gaps) <= 4:
            return "medium"
        else:
            return "high"

    def should_reformulate(self, query: str, documents: List[Dict[str, Any]], threshold: int = 2) -> bool:
        gaps = self.detect(query, documents)
        return len(gaps) >= threshold
