from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from typing import List, Dict, Tuple
import json
from config import settings

class EntityExtractor:
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
                temperature=0
            )

        self.extraction_prompt = PromptTemplate(
            input_variables=["text"],
            template="""Extract all entities and relationships from the following text.

Text: {text}

Return a JSON object with this structure:
{{
    "entities": [
        {{"id": "unique_id", "name": "entity_name", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|PRODUCT|EVENT", "description": "brief description"}}
    ],
    "relationships": [
        {{"source": "entity_id", "target": "entity_id", "type": "RELATED_TO|WORKS_FOR|LOCATED_IN|CREATED|USES", "description": "relationship description"}}
    ]
}}

Only return valid JSON, no additional text."""
        )

    def extract_entities_and_relations(self, text: str) -> Tuple[List[Dict], List[Dict]]:
        chain = self.extraction_prompt | self.llm

        response = chain.invoke({"text": text})

        content = response.content
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            json_str = content[start_idx:end_idx]
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            return [], []

        entities = data.get("entities", [])
        relationships = data.get("relationships", [])

        return entities, relationships

    def enrich_entity(self, entity_name: str) -> Dict:
        prompt = PromptTemplate(
            input_variables=["entity"],
            template="""Provide a concise enrichment for the entity: {entity}

Return JSON:
{{
    "aliases": ["alternative name 1", "alternative name 2"],
    "category": "broad category",
    "significance": "high|medium|low"
}}"""
        )

        chain = prompt | self.llm
        response = chain.invoke({"entity": entity_name})

        try:
            start_idx = response.content.find('{')
            end_idx = response.content.rfind('}') + 1
            json_str = response.content[start_idx:end_idx]
            return json.loads(json_str)
        except:
            return {"aliases": [], "category": "unknown", "significance": "medium"}

entity_extractor = EntityExtractor()
