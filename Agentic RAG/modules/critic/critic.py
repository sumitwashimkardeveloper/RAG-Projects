from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class CriticFeedback:
    is_relevant: bool
    confidence_score: float
    gaps_identified: List[str] = field(default_factory=list)
    completeness_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class Critic:
    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

    def evaluate(self, query: str, documents: List, context: Dict[str, Any] = None) -> CriticFeedback:
        raise NotImplementedError("Implement in Phase 5")

    def evaluate_relevance(self, query: str, documents: List) -> Tuple[bool, float]:
        raise NotImplementedError("Implement in Phase 5")

    def calculate_confidence(self, documents: List, query: str) -> float:
        raise NotImplementedError("Implement in Phase 5")

    def detect_gaps(self, query: str, documents: List) -> List[str]:
        raise NotImplementedError("Implement in Phase 5")

    def check_completeness(self, query: str, documents: List) -> float:
        raise NotImplementedError("Implement in Phase 5")
