import pytest
from modules.answer_generator import PromptTemplateManager

@pytest.fixture
def manager():
    return PromptTemplateManager()

def test_get_default_template(manager):
    template = manager.get_template("default")

    assert "{query}" in template
    assert "{context}" in template

def test_get_all_templates(manager):
    templates = manager.get_available_templates()

    assert len(templates) > 0
    assert "default" in templates
    assert "detailed" in templates

def test_format_prompt(manager):
    query = "What is Python?"
    context = "Python is a programming language"

    prompt = manager.format_prompt(query, context)

    assert query in prompt
    assert context in prompt

def test_add_custom_template(manager):
    manager.add_custom_template("custom", "Custom: {query} with {context}")

    template = manager.get_template("custom")

    assert "Custom:" in template

def test_select_template_technical(manager):
    selected = manager.select_template("technical algorithm")

    assert selected == "technical"

def test_select_template_comparative(manager):
    selected = manager.select_template("compare difference")

    assert selected == "comparative"

def test_select_template_educational(manager):
    selected = manager.select_template("explain learning")

    assert selected == "educational"

def test_format_prompt_with_instructions(manager):
    instructions = "Be concise"
    query = "test"
    context = "context"

    prompt = manager.format_prompt_with_instructions(query, context, instructions)

    assert instructions in prompt
    assert query in prompt
