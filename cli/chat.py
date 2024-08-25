import click
from llmhub_lib.app_dependency_container import AppDependencyContainer

process_manager = AppDependencyContainer.get("process_manager")

@click.command()
@click.argument('model_name', required=False)
@click.option('--one-shot', is_flag=True, help='Execute as a one-shot command.')
@click.option('--messages', help='Provide messages as a JSON array.')
@click.option('--messages-file', type=click.Path(), help='Provide messages from a file.')
@click.option('--context-size', default=4096, help='Context size for the chat session.')
def chat(model_name=None, one_shot=False, messages=None, messages_file=None, context_size=4096):
    """Open a chat interface or execute a one-shot command."""
    if one_shot:
        process_manager.execute_one_shot(model_name, messages, messages_file, context_size)
    else:
        process_manager.start_chat_interface(model_name, context_size)


@click.command()
@click.argument('prompt', required=False)
@click.option('--prompt-file', type=click.Path(), help='Provide a prompt from a file.')
def instruct(prompt=None, prompt_file=None):
    """Execute a one-shot instruct command."""
    process_manager.execute_instruct(prompt, prompt_file)