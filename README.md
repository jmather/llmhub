
# LLMHub Project

## Overview

LLMHub is a lightweight management platform designed to streamline the operation and interaction with various language models (LLMs). It provides an intuitive command-line interface (CLI) and a RESTful API to manage, start, stop, and interact with LLMs. The platform supports running multiple models with different configurations and context sizes, allowing dynamic scaling and efficient use of resources.

## Features

- **Model Management**: Start, stop, and monitor multiple LLM processes with different configurations.
- **Dynamic Context Management**: Automatically route requests to the most suitable model instance based on the required context size.
- **API Gateway**: Provides OpenAI-compatible endpoints for completions and chat completions, making it easy to integrate with existing applications.
- **Modular Design**: Extensible architecture with clear separation of concerns, allowing easy modification and expansion.
- **Persistent State Management**: Keeps track of running processes, allowing for smooth restarts and state recovery.
- **Logging**: Detailed logging for process management and interactions.

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jmather/llmhub.git
   cd llmhub
   ```

2. **Set Up the Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure LLMHub**
   - Edit the `config.yaml` file to define your models, engines, and other settings. You can define multiple models, each with different quantizations and context sizes.

   Example:
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
       path: /path/to/llama-server
       arguments: --color -t 20 --parallel 2 --mlock --metrics --verbose
       model_flag: "-m"
       context_size_flag: "-c"
       port_flag: "--port"
       file_types: [gguf]
   ```

## Usage

### Command-Line Interface (CLI)

LLMHub provides a set of commands to manage models and interact with them:

1. **Start a Model**
   ```bash
   python llmhub.py start MythoMax-L2-13B
   ```

2. **Stop a Model**
   ```bash
   python llmhub.py stop MythoMax-L2-13B
   ```

3. **List Running Models**
   ```bash
   python llmhub.py list_models
   ```

4. **Update Processes**
   ```bash
   python llmhub.py update
   ```

5. **View Logs**
   ```bash
   python llmhub.py logs MythoMax-L2-13B
   ```

### REST API

LLMHub exposes a RESTful API with endpoints compatible with OpenAI's API, allowing seamless integration into existing applications.

- **List Models**
  ```bash
  GET /v1/models
  ```

- **Create a Completion**
  ```bash
  POST /v1/completions
  ```

  Example Payload:
  ```json
  {
      "model": "MythoMax-L2-13B",
      "prompt": "Once upon a time,",
      "max_tokens": 100,
      "temperature": 0.7
  }
  ```

- **Create a Chat Completion**
  ```bash
  POST /v1/chat/completions
  ```

## Development

### Directory Structure

- **`llmhub_lib/`**: Contains the core libraries for configuration management, state management, process management, and model management.
- **`cli/`**: Contains CLI commands that interact with the core libraries.
- **`web_server.py`**: Flask-based web server that provides the REST API.
- **`config.yaml`**: Configuration file for defining models, engines, and other settings.

### Extending LLMHub

LLMHub's modular design allows easy extension. You can add new engines, modify process management logic, or integrate additional logging or monitoring tools. The `AppDependencyContainer` makes it easy to inject dependencies and add new components.

## Testing

You can use tools like Postman to test the API. Import the provided Postman configuration to get started quickly.

### Running Tests

Ensure that your environment is set up correctly with all dependencies installed. Use the CLI to start the necessary processes, then run tests against the API endpoints using Postman or cURL.

## Troubleshooting

- **Model Not Found**: Ensure that the model is defined correctly in `config.yaml` and that the required files are in place.
- **Port Conflicts**: Adjust the `engine_port_min` and `engine_port_max` settings in `config.yaml` to avoid conflicts.
- **Process Failures**: Check the logs for detailed error messages. Logs are stored in `~/.llmhub/logs`.

## Contributions

Contributions are welcome! Feel free to submit issues, feature requests, or pull requests to improve LLMHub.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides an overview and instructions for getting started with LLMHub. For more detailed documentation, refer to the code comments and configuration files.
