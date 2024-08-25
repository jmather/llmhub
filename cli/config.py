import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

config_manager = AppDependencyContainer.get("config_manager")

@click.command()
def load_config():
    """Load the current configuration."""
    config_manager.load_config()


@click.command()
def save_config():
    """Save the current configuration."""
    config_manager.save_config()


@click.command()
def update_config():
    """Update the configuration file."""
    config_manager.update_config()