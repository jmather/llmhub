# web_server.py
import re

from flask import Flask, request, jsonify
from llmhub_lib.actions import update_processes, start_specific_process, stop_all_processes, stop_specific_process, start_proxy_process, stop_proxy_process
from llmhub_lib.app_dependency_container import AppDependencyContainer
import requests

app = Flask(__name__)

# Initialize model manager from the dependency container
model_manager = AppDependencyContainer.get("model_manager")
state_manager = AppDependencyContainer.get("state_manager")

# LLM Management Endpoints

@app.route('/llms/update', methods=['POST'])
def update():
    update_processes()
    return jsonify({"message": "Processes updated."}), 200

@app.route('/llms/start', methods=['POST'])
def start():
    data = request.json
    model_name = data.get('model_name')
    quant = data.get('quant')
    engine = data.get('engine')
    context_size = data.get('context_size', 4096)
    port = data.get('port', 8081)

    if not model_name:
        return jsonify({"error": "model_name is required"}), 400

    start_specific_process(model_name, quant, engine, context_size, port)
    return jsonify({"message": f"Started process for {model_name} with quant {quant} and context size {context_size}."}), 200

@app.route('/llms/stop', methods=['POST'])
def stop():
    data = request.json
    model_name = data.get('model_name')

    if model_name:
        stop_specific_process(model_name)
        return jsonify({"message": f"Stopped process {model_name}."}), 200
    else:
        stop_all_processes()
        return jsonify({"message": "Stopped all processes."}), 200

@app.route('/llms/status', methods=['GET'])
def status():
    model_list = model_manager.list_models()
    return jsonify({"data": model_list}), 200

# OpenAI-Compatible Completion Endpoints

@app.route('/v1/completions', methods=['POST'])
def completion():
    return handle_completion(request.json, '/v1/completions')

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completion():
    return handle_chat_completion(request.json)


def clean_response_data(response_data, matched_process):
    # Replace the model path in the 'generation_settings' with the process name
    if 'generation_settings' in response_data:
        if 'model' in response_data['generation_settings']:
            response_data['generation_settings']['model'] = matched_process

    # Replace the model path in the top-level 'model' key
    if 'model' in response_data:
        response_data['model'] = matched_process

    return response_data

def handle_completion(data, endpoint):
    model_name = data.get('model')
    prompt = data.get('prompt')
    max_tokens = data.get('max_tokens', 100)
    temperature = data.get('temperature', 0.7)

    if not model_name or not prompt:
        return jsonify({"error": "Both model and prompt are required"}), 400

    # Estimate the required context size
    prompt_tokens = len(prompt.split())  # Rough estimate using word count
    required_context_size = prompt_tokens + max_tokens

    # Fetch available processes for the model
    matched_processes = [p for p in model_manager.get_running_processes() if p.startswith(model_name)]

    if not matched_processes:
        return jsonify({
            "error": "No suitable process found.",
            "available_models": model_manager.list_models()
        }), 404

    # Select the smallest context size that is >= required_context_size
    suitable_process = None
    for process in matched_processes:
        context_size = int(process.split('-')[-1])  # Assumes process name format includes context size
        if context_size >= required_context_size:
            if suitable_process is None or context_size < int(suitable_process.split('-')[-1]):
                suitable_process = process

    if not suitable_process:
        return jsonify({
            "error": "No suitable process found with required context size.",
            "required_context_size": required_context_size
        }), 404

    # Extract the port for the matched process
    state = state_manager.load_state(suitable_process)
    port = state['port']
    url = f"http://localhost:{port}{endpoint}"

    # Forward the request to the LLM process
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "context_size": required_context_size  # Include the estimated context size
    }
    response = requests.post(url, json=payload)

    response_data = response.json()
    response_data = clean_response_data(response_data, suitable_process)

    return jsonify(response_data), response.status_code

def handle_chat_completion(data):
    model_name = data.get('model')
    messages = data.get('messages')
    max_tokens = data.get('max_tokens', 100)
    temperature = data.get('temperature', 0.7)

    if not model_name or not messages:
        return jsonify({"error": "Both model and messages are required"}), 400

    matched_process, available_models = model_manager.match_model(model_name)

    if not matched_process:
        return jsonify({
            "error": "Model not found.",
            "available_models": available_models
        }), 404

    # Extract the port for the matched process
    port = model_manager.get_model_port(matched_process)
    url = f"http://localhost:{port}/v1/chat/completions"

    # Forward the request to the LLM process
    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    response = requests.post(url, json=payload)

    response_data = response.json()
    response_data = clean_response_data(response_data, matched_process)

    return jsonify(response_data), response.status_code

# OpenAI-Compatible Models Endpoint

@app.route('/v1/models', methods=['GET'])
def list_openai_models():
    models = list(state_manager.list_states())
    # we need to filter out the proxy processes
    # real_models = [model for model in models if not model.startswith("proxy-")]

    all_models = []
    last_model = None
    for model in models:
        if model.startswith("proxy-"):
            continue

        base_model = re.sub(r'-[0-9]+$', '', model)
        print(f"Base model: {base_model} of model: {model}")
        if base_model != last_model:
            last_model = base_model
            all_models.append(base_model)

        all_models.append(model)
    return jsonify({"data": all_models}), 200

if __name__ == '__main__':
    config = AppDependencyContainer.get("config_manager").get_merged_config()
    web_port = config.get('port', 5000)  # Default to 5000 if not specified in the config
    app.run(host='0.0.0.0', port=web_port)
