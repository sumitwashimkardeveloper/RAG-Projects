import os
from pathlib import Path
from modules.utils import get_logger, get_config

LOG_FILE = Path("logs") / "agentic_rag.log"
logger = get_logger(__name__, log_file=str(LOG_FILE))

def initialize_app():
    config = get_config()
    logger.info("Application initialized")
    logger.info(f"LLM Provider: {config.get('llm.provider')}")
    logger.info(f"Vector DB Provider: {config.get('vector_db.provider')}")
    return config

def main():
    try:
        config = initialize_app()
        logger.info("Agentic RAG system started")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
