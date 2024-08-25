import click

from llmhub_lib.actions import start_model, stop_model
from llmhub_lib.app_dependency_container import AppDependencyContainer

process_manager = AppDependencyContainer.get("process_manager")


@click.command()
@click.argument('model_name', required=False)
def start(model_name=None):
    """Start a specific model process or all processes if no model_name is provided."""
    start_model(model_name)

@click.command()
@click.argument('model_name', required=False)
def stop(model_name=None):
    """Stop a specific process or all processes if no model_name is provided."""
    stop_model(model_name)

@click.command()
@click.argument('model_name', required=False)
def restart(model_name=None):
    """Restart a specific process or all processes if no model_name is provided."""
    if model_name:
        stop_model(model_name)
        start_model(model_name)
    else:
        process_manager.stop_all_processes()
        process_manager.update_processes()


@click.command()
def update():
    """Update and restart all configured processes."""
    process_manager.update_processes()