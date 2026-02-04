import pytest
import os
from pathlib import Path
from modules.utils import get_config, get_logger

@pytest.fixture(scope="session")
def config():
    os.environ["CONFIG_PATH"] = "configs/config.yaml"
    return get_config()

@pytest.fixture(scope="session")
def logger():
    return get_logger(__name__)

@pytest.fixture(autouse=True)
def setup_test_env():
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)
    Path("cache").mkdir(exist_ok=True)
    yield
