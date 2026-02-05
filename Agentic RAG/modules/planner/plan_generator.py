from typing import List, Dict, Any
from dataclasses import dataclass, field
from modules.utils import get_logger

logger = get_logger(__name__)

@dataclass
class PlanStep:
    step_number: int
    action: str
    description: str
    dependencies: List[int] = field(default_factory=list)
    estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalPlan:
    query: str
    steps: List[PlanStep]
    total_estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class PlanGenerator:
    def __init__(self, config=None):
        self.config = config
        self.max_steps = 5

    def generate_plan(self, query: str, analysis: Dict[str, Any], strategy: str) -> RetrievalPlan:
        sub_queries = analysis.get("sub_queries", [])
        complexity = analysis.get("complexity", 0.0)
        has_multiple_parts = analysis.get("has_multiple_parts", False)

        steps = []

        steps.append(PlanStep(
            step_number=1,
            action="parse_query",
            description="Parse and normalize the input query",
            estimated_cost=0.1
        ))

        steps.append(PlanStep(
            step_number=2,
            action="retrieve_documents",
            description=f"Retrieve documents using {strategy} strategy",
            dependencies=[1],
            estimated_cost=0.3
        ))

        if has_multiple_parts:
            steps.append(PlanStep(
                step_number=3,
                action="process_sub_queries",
                description=f"Process {len(sub_queries)} sub-queries",
                dependencies=[2],
                estimated_cost=0.2 * len(sub_queries)
            ))

        if complexity > 0.6:
            steps.append(PlanStep(
                step_number=len(steps) + 1,
                action="refine_results",
                description="Apply advanced filtering and ranking",
                dependencies=[max([s.step_number for s in steps])],
                estimated_cost=0.2
            ))

        steps.append(PlanStep(
            step_number=len(steps) + 1,
            action="aggregate_results",
            description="Aggregate and deduplicate results",
            dependencies=[s.step_number for s in steps if s.action != "aggregate_results"],
            estimated_cost=0.1
        ))

        total_cost = sum(step.estimated_cost for step in steps)

        plan = RetrievalPlan(
            query=query,
            steps=steps,
            total_estimated_cost=total_cost,
            metadata={
                "complexity": complexity,
                "sub_query_count": len(sub_queries),
                "strategy": strategy
            }
        )

        logger.info(f"Generated retrieval plan with {len(steps)} steps, estimated cost: {total_cost:.2f}")
        return plan

    def optimize_plan(self, plan: RetrievalPlan) -> RetrievalPlan:
        if len(plan.steps) > self.max_steps:
            optimized_steps = self._merge_steps(plan.steps)
            plan.steps = optimized_steps

        return plan

    def _merge_steps(self, steps: List[PlanStep]) -> List[PlanStep]:
        if len(steps) <= self.max_steps:
            return steps

        merged = []
        for i, step in enumerate(steps):
            if i < len(steps) - 1 and self._can_merge(step, steps[i + 1]):
                continue

            merged.append(step)

        return merged if len(merged) <= self.max_steps else steps[:self.max_steps]

    def _can_merge(self, step1: PlanStep, step2: PlanStep) -> bool:
        return (
            step2.step_number in step1.dependencies or
            step1.action.startswith(step2.action.split("_")[0])
        )

    def validate_plan(self, plan: RetrievalPlan) -> Dict[str, Any]:
        issues = []

        all_step_numbers = {step.step_number for step in plan.steps}

        for step in plan.steps:
            for dep in step.dependencies:
                if dep not in all_step_numbers:
                    issues.append(f"Step {step.step_number} has invalid dependency: {dep}")

        if plan.total_estimated_cost > 1.0:
            issues.append(f"High estimated cost: {plan.total_estimated_cost:.2f}")

        if len(plan.steps) > self.max_steps:
            issues.append(f"Plan exceeds max steps: {len(plan.steps)} > {self.max_steps}")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warning_count": len([i for i in issues if "High" in i])
        }
