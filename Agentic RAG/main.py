import os
from pathlib import Path
from modules.utils import get_logger, get_config, get_database_manager

LOG_FILE = Path("logs") / "agentic_rag.log"
logger = get_logger(__name__, log_file=str(LOG_FILE))

def initialize_app():
    config = get_config()
    logger.info("Application initialized")
    logger.info(f"LLM Provider: {config.get('llm.provider')}")
    logger.info(f"Vector DB Provider: {config.get('vector_db.provider')}")

    db_manager = get_database_manager(config)
    health = db_manager.health_check()
    logger.info(f"Database health: {health}")

    return config, db_manager

def main():
    try:
        config, db_manager = initialize_app()
        logger.info("Agentic RAG system started")

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
