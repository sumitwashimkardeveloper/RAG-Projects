from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from typing import Dict
from config import settings

class AnswerGenerator:
    def __init__(self, use_anthropic: bool = False):
        if use_anthropic and settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model_name="claude-3-sonnet-20240229"
            )
        else:
            self.llm = ChatOpenAI(
                api_key=settings.openai_api_key,
                model_name=settings.llm_model,
                temperature=0.7
            )

    def generate_answer(self, query: str, graph_context: Dict) -> Dict:
        context_text = self._format_graph_context(graph_context)

        prompt = PromptTemplate(
            input_variables=["query", "context"],
            template="""You are an expert assistant that answers questions using a knowledge graph.

Knowledge Graph Context:
{context}

User Query: {query}

Based on the knowledge graph context above, provide a comprehensive answer to the user's query.
Include relevant entities, relationships, and connections found in the graph.
If information is not directly available in the graph, state that clearly.

Answer:"""
        )

        chain = prompt | self.llm
        response = chain.invoke({
            "query": query,
            "context": context_text
        })

        return {
            "query": query,
            "answer": response.content,
            "context_used": context_text[:500]
        }

    def _format_graph_context(self, graph_context: Dict) -> str:
        lines = []

        if "entity_context" in graph_context:
            lines.append("=== Entities Found ===")
            for ctx in graph_context["entity_context"]:
                if ctx.get("found"):
                    entity = ctx.get("entity", {})
                    lines.append(f"Entity: {entity.get('name', 'Unknown')}")
                    lines.append(f"Type: {entity.get('type', 'Unknown')}")
                    lines.append(f"Relationships: {ctx.get('neighbor_count', 0)}")
                    lines.append("")

        if "connections" in graph_context:
            lines.append("=== Entity Connections ===")
            for conn in graph_context["connections"]:
                lines.append(f"Paths between {conn.get('entity1')} and {conn.get('entity2')}: {conn.get('path_count')}")
                lines.append("")

        if "parsed_entities" in graph_context:
            lines.append("=== Extracted Entities ===")
            for entity_result in graph_context["parsed_entities"]:
                query_entity = entity_result.get("query_entity", {})
                lines.append(f"Entity: {query_entity.get('name')}")
                lines.append(f"Type: {query_entity.get('type')}")
                lines.append("")

        return "\n".join(lines) if lines else "No graph context available"

    def generate_answer_with_streaming(self, query: str, graph_context: Dict):
        context_text = self._format_graph_context(graph_context)

        prompt = f"""You are an expert assistant that answers questions using a knowledge graph.

Knowledge Graph Context:
{context_text}

User Query: {query}

Based on the knowledge graph context above, provide a comprehensive answer to the user's query.
Include relevant entities, relationships, and connections found in the graph.
If information is not directly available in the graph, state that clearly.

Answer:"""

        return self.llm.predict(text=prompt)

answer_generator = AnswerGenerator()
