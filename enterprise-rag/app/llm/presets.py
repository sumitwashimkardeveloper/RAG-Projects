LLM_PRESETS = {
    "gpt4-accurate": {
        "model": "gpt-4-turbo-preview",
        "temperature": 0.3,
        "max_tokens": 2048,
        "description": "Accurate GPT-4 for precise answers"
    },
    "gpt4-creative": {
        "model": "gpt-4-turbo-preview",
        "temperature": 0.9,
        "max_tokens": 3000,
        "description": "Creative GPT-4 for brainstorming"
    },
    "gpt35-balanced": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 2048,
        "description": "Balanced GPT-3.5 for general use"
    },
    "gpt35-fast": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 1024,
        "description": "Fast GPT-3.5 for quick responses"
    },
    "claude-accurate": {
        "model": "claude-3-opus-20240229",
        "temperature": 0.2,
        "max_tokens": 2048,
        "description": "Accurate Claude Opus"
    },
    "claude-balanced": {
        "model": "claude-3-sonnet-20240229",
        "temperature": 0.7,
        "max_tokens": 2048,
        "description": "Balanced Claude Sonnet"
    },
    "summary-concise": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 500,
        "description": "Concise summarization"
    },
    "summary-detailed": {
        "model": "gpt-4-turbo-preview",
        "temperature": 0.5,
        "max_tokens": 1500,
        "description": "Detailed summarization"
    }
}


def get_preset(name: str) -> dict:
    if name not in LLM_PRESETS:
        raise ValueError(f"Unknown preset: {name}")
    return LLM_PRESETS[name].copy()


def list_presets() -> dict:
    return {name: config["description"] for name, config in LLM_PRESETS.items()}
