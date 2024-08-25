import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

model_manager = AppDependencyContainer.get("model_manager")

@click.command()
def refresh_models():
    """Update the models list in the models.yaml file."""
    model_manager.find_and_update_models()
