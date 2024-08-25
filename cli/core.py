import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

config_manager = AppDependencyContainer.get("config_manager")
process_manager = AppDependencyContainer.get("process_manager")

@click.command()
def status():
    """Display the current status of the LLM servers."""
    expected_processes = process_manager.generate_expected_processes(config_manager.get_merged_config())
    process_manager.display_status(expected_processes)


@click.command()
def list_models():
    """List available models and their quantizations."""
    models = config_manager.list_models()
    for model in models:
        click.echo(model)


@click.command()
def memoryusage():
    """Estimate memory usage for the defined models."""
    memory_usage, total_memory = process_manager.estimate_memory_usage(config_manager.get_merged_config())
    for process_name, usage in memory_usage.items():
        click.echo(f"{process_name}: Model {usage[0]:.2f} MB + Context {usage[1]:.2f} MB")
    click.echo(f"\nTotal Estimated Memory Usage: {total_memory:.2f} MB")