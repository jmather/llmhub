import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

log_manager = AppDependencyContainer.get("log_manager")

@click.command()
@click.argument('service_name', required=False)
@click.option('-f', '--follow', is_flag=True, help='Follow the log output')
@click.option('-n', default=50, help='Number of lines to show')
def logs(service_name=None, follow=False, n=50):
    """Show the logs for a specific process or all processes if no model_name is provided."""
    if not service_name:
        # throw error
        print("Target service name is required.")
        return
    if follow:
        log_manager.follow_log(service_name)
    else:
        log_manager.tail_log(service_name, n)
