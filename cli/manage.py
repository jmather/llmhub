import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

service_manager = AppDependencyContainer.get("service_manager")

@click.command()
@click.argument('model_name', required=False)
def start(model_name=None):
    """Start a specific model process or all processes if no model_name is provided."""
    if model_name:
        service_manager.start_service(model_name, quant="Q5_K_M")  # Example quant value
    else:
        service_manager.update_services()

@click.command()
@click.argument('model_name', required=False)
def stop(model_name=None):
    """Stop a specific process or all processes if no model_name is provided."""
    if model_name:
        service_manager.stop_service(model_name)
    else:
        service_manager.stop_all_services()

@click.command()
@click.argument('model_name', required=False)
def restart(model_name=None):
    """Restart a specific process or all processes if no model_name is provided."""
    if model_name:
        service_manager.stop_service(model_name)
        service_manager.start_service(model_name, quant="Q5_K_M")  # Example quant value
    else:
        service_manager.stop_all_services()
        service_manager.update_services()

@click.command()
def update():
    """Update and restart all configured processes."""
    service_manager.update_services()
