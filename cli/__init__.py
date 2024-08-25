from .core import status, list_models, memoryusage
from .manage import start, stop, restart, update
from .logs import logs
from .models import refresh_models
from .config import load_config, save_config, update_config
from .chat import chat, instruct
import click

@click.group()
def cli():
    """LLMHub CLI for managing LLM servers."""
    pass

# Add the commands here
cli.add_command(status)
cli.add_command(list_models)
cli.add_command(memoryusage)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(restart)
cli.add_command(update)
cli.add_command(logs)
cli.add_command(refresh_models)  # Ensure this is included
cli.add_command(load_config)
cli.add_command(save_config)
cli.add_command(update_config)
cli.add_command(chat)
cli.add_command(instruct)