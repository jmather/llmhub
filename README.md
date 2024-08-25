# LLMHub CLI

LLMHub CLI is a command-line interface tool designed to manage and interact with various LLM (Large Language Model) servers. It allows you to start, stop, update, and manage LLM processes easily and efficiently.

## Features

- Manage LLM servers
- Start, stop, and update LLM processes
- List available models and their statuses
- OpenAI-compatible API endpoints for completions and models
- Easily configurable via YAML files
- Supports different engines and quantization formats

## Installation

You can install LLMHub CLI directly from PyPI:

```bash
pip install llmhub-cli
```

## Usage

After installation, you can use the `llmhub` command to interact with the tool. Below are some example commands:

### Start a Process

```bash
llmhub start MythoMax-L2-13B
```

### Stop a Process

```bash
llmhub stop MythoMax-L2-13B
```

### Update All Processes

```bash
llmhub update
```

### List All Models

```bash
llmhub list-models
```

### Check Status

```bash
llmhub status
```

## Configuration

The configuration is handled via YAML files. You can place your `config.yaml` file in the `~/.llmhub/` directory or specify a custom path when initializing the ConfigManager.

### Example Configuration

```yaml
on_start:
  MythoMax-L2-13B:
    quant: Q5_K_M
    engine: llamacppserver
    context_size: [512, 1024, 2048]

port: 8080
enable_proxy: true
engine_port_min: 8081
engine_port_max: 10000

engines:
  llamacppserver:
    path: /path/to/llamacppserver
    arguments: --color -t 20 --parallel 2 --mlock --metrics --verbose
    model_flag: "-m"
    context_size_flag: "-c"
    port_flag: "--port"
    api_key_flag: "--api-key"
    file_types: [gguf]
```

## API Endpoints

LLMHub CLI also provides OpenAI-compatible API endpoints:

- `/v1/completions`: Handle completion requests.
- `/v1/chat/completions`: Handle chat completion requests.
- `/v1/models`: List available models.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Contact

For any questions or issues, please open an issue on the [GitHub repository](https://github.com/your-username/llmhub-cli).

