# test_model_manager.py

import pytest
from flask import Flask
from unittest.mock import MagicMock
from llmhub_lib.model_manager import ModelManager
from llmhub_lib.state_manager import StateManager


# Test the get_model_port method
def test_get_model_port():
    state_manager = MagicMock(spec=StateManager)
    state_manager.load_state.return_value = {"port": 8081}

    model_manager = ModelManager(config_manager=None, state_manager=state_manager)

    process_name = "test-model-Q5_K_M-4096"
    port = model_manager.get_model_port(process_name)

    state_manager.load_state.assert_called_once_with(process_name)
    assert port == 8081


def test_handle_chat_completion(monkeypatch):
    from llmhub_lib.web_server import handle_chat_completion

    # Set up the Flask app context
    app = Flask(__name__)
    with app.app_context():
        state_manager = MagicMock(spec=StateManager)
        state_manager.load_state.return_value = {"port": 8081}

        model_manager = MagicMock(spec=ModelManager)
        model_manager.match_model.return_value = ("test-model-Q5_K_M-4096", None)
        model_manager.get_model_port.return_value = 8081

        # Mock the request to the model server
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test"}
        mock_response.status_code = 200

        monkeypatch.setattr("requests.post", MagicMock(return_value=mock_response))

        # Prepare the request data
        data = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello, how are you?"}],
            "max_tokens": 100,
            "temperature": 0.7,
        }

        # Call the function under test
        response, status_code = handle_chat_completion(data)

        # Validate the response
        assert status_code == 200
        assert response.json == {"response": "test"}