from typing import Dict, List, Any
from modules.utils import get_logger

logger = get_logger(__name__)

class PromptTemplateManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.templates = self._initialize_templates()
        self.custom_templates = {}

    def _initialize_templates(self) -> Dict[str, str]:
        return {
            "default": """Based on the provided context, answer the following question:

Question: {query}

Context:
{context}

Answer:""",

            "detailed": """Please provide a comprehensive answer to the following question using the provided context.

Question: {query}

Supporting Context:
{context}

Please structure your answer with:
1. Direct answer to the question
2. Supporting details and examples
3. Any relevant limitations or caveats

Answer:""",

            "summary": """Summarize the key points relevant to the following question based on the context provided:

Question: {query}

Context:
{context}

Summary:""",

            "technical": """Provide a technical explanation for the following question using the provided context:

Question: {query}

Technical Context:
{context}

Technical Explanation:""",

            "comparative": """Compare and contrast the information in the context to answer the following question:

Question: {query}

Context:
{context}

Comparative Analysis:""",

            "educational": """Explain the following in a way that would help someone learn about it:

Question: {query}

Educational Context:
{context}

Educational Explanation:""",

            "practical": """Provide practical, actionable guidance based on the following question and context:

Question: {query}

Context:
{context}

Practical Guidance:""",

            "analytical": """Analyze the following question and context to provide insights:

Question: {query}

Context for Analysis:
{context}

Analysis:"""
        }

    def get_template(self, template_name: str = "default") -> str:
        if template_name in self.custom_templates:
            return self.custom_templates[template_name]
        return self.templates.get(template_name, self.templates["default"])

    def add_custom_template(self, name: str, template: str):
        self.custom_templates[name] = template
        self.logger.info(f"Added custom template: {name}")

    def format_prompt(self, query: str, context: str, template_name: str = "default") -> str:
        template = self.get_template(template_name)

        try:
            prompt = template.format(query=query, context=context)
            return prompt
        except KeyError as e:
            self.logger.error(f"Error formatting prompt: {e}")
            return f"Question: {query}\n\nContext:\n{context}"

    def format_prompt_with_instructions(self, query: str, context: str, instructions: str,
                                       template_name: str = "default") -> str:
        template = self.get_template(template_name)

        try:
            base_prompt = template.format(query=query, context=context)
            return f"{instructions}\n\n{base_prompt}"
        except KeyError:
            return f"{instructions}\n\nQuestion: {query}\n\nContext:\n{context}"

    def get_available_templates(self) -> List[str]:
        return list(self.templates.keys()) + list(self.custom_templates.keys())

    def select_template(self, intent: str) -> str:
        intent_lower = intent.lower()

        if "technical" in intent_lower or "algorithm" in intent_lower:
            return "technical"
        elif "compare" in intent_lower or "difference" in intent_lower:
            return "comparative"
        elif "learn" in intent_lower or "explain" in intent_lower:
            return "educational"
        elif "how" in intent_lower or "guide" in intent_lower:
            return "practical"
        elif "summary" in intent_lower or "brief" in intent_lower:
            return "summary"
        elif "analyze" in intent_lower or "insight" in intent_lower:
            return "analytical"
        else:
            return "default"
