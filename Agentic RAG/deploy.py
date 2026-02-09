import os
import sys
import subprocess
from pathlib import Path
from modules.utils import get_logger, get_config

logger = get_logger(__name__)

class DeploymentManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.project_root = Path(__file__).parent

    def setup_environment(self):
        self.logger.info("Setting up environment")

        required_dirs = ["logs", "cache", "data", "cache/queries", "cache/embeddings"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {dir_name}")

        env_file = self.project_root / ".env"
        if not env_file.exists():
            self.logger.info("Creating .env file from template")
            template_file = self.project_root / ".env.template"
            if template_file.exists():
                template_file.read_text()
                env_file.write_text(template_file.read_text())

        return True

    def install_dependencies(self):
        self.logger.info("Installing dependencies")

        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                subprocess.run(
                    ["pip", "install", "-r", str(req_file)],
                    check=True,
                    capture_output=True
                )
                self.logger.info("Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error installing dependencies: {e}")
                return False

        return False

    def run_tests(self):
        self.logger.info("Running tests")

        try:
            result = subprocess.run(
                ["pytest", "tests/", "-v", "--tb=short"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )

            self.logger.info("Tests completed")
            if result.returncode == 0:
                self.logger.info("All tests passed")
                return True
            else:
                self.logger.warning(f"Some tests failed: {result.stdout}")
                return False
        except FileNotFoundError:
            self.logger.error("pytest not found")
            return False

    def start_docker_compose(self):
        self.logger.info("Starting Docker Compose")

        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd=str(self.project_root),
                check=True,
                capture_output=True
            )
            self.logger.info("Docker Compose started successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error starting Docker Compose: {e}")
            return False

    def build_docker_image(self):
        self.logger.info("Building Docker image")

        try:
            subprocess.run(
                ["docker", "build", "-t", "agentic-rag:latest", "."],
                cwd=str(self.project_root),
                check=True,
                capture_output=True
            )
            self.logger.info("Docker image built successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error building Docker image: {e}")
            return False

    def verify_deployment(self):
        self.logger.info("Verifying deployment")

        try:
            import requests

            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                self.logger.info("API is healthy")
                return True
            else:
                self.logger.warning(f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error verifying deployment: {e}")
            return False

    def generate_deployment_report(self):
        self.logger.info("Generating deployment report")

        report = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "project": "Agentic RAG",
            "version": "1.0.0",
            "components": [
                "Query Planner",
                "Retriever",
                "Critic",
                "Query Rewriter",
                "Answer Generator"
            ],
            "configuration": {
                "max_iterations": self.config.get("loop.max_iterations", 5),
                "timeout_seconds": self.config.get("loop.iteration_timeout", 60),
                "api_host": self.config.get("api.host", "0.0.0.0"),
                "api_port": self.config.get("api.port", 8000)
            }
        }

        return report

    def full_deployment(self):
        self.logger.info("Starting full deployment process")

        steps = [
            ("Environment Setup", self.setup_environment),
            ("Install Dependencies", self.install_dependencies),
            ("Run Tests", self.run_tests),
            ("Build Docker", self.build_docker_image),
            ("Start Services", self.start_docker_compose),
            ("Verify Deployment", self.verify_deployment)
        ]

        results = {}
        for step_name, step_func in steps:
            self.logger.info(f"Executing: {step_name}")
            try:
                results[step_name] = step_func()
            except Exception as e:
                self.logger.error(f"Error in {step_name}: {e}")
                results[step_name] = False

        report = self.generate_deployment_report()
        self.logger.info(f"Deployment report: {report}")

        return results

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agentic RAG Deployment Manager")
    parser.add_argument("--setup", action="store_true", help="Setup environment")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--docker-build", action="store_true", help="Build Docker image")
    parser.add_argument("--docker-start", action="store_true", help="Start Docker Compose")
    parser.add_argument("--verify", action="store_true", help="Verify deployment")
    parser.add_argument("--full", action="store_true", help="Full deployment")

    args = parser.parse_args()

    manager = DeploymentManager()

    if args.setup:
        manager.setup_environment()
    elif args.install:
        manager.install_dependencies()
    elif args.test:
        manager.run_tests()
    elif args.docker_build:
        manager.build_docker_image()
    elif args.docker_start:
        manager.start_docker_compose()
    elif args.verify:
        manager.verify_deployment()
    elif args.full:
        manager.full_deployment()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
