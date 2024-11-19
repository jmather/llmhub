# llmhub_lib/service_manager.py

class ServiceManager:
    def __init__(self, process_manager, model_manager, config_manager, state_manager):
        self.process_manager = process_manager
        self.model_manager = model_manager
        self.config_manager = config_manager
        self.state_manager = state_manager

    def start_service(self, model_name, quant, context_size=4096, port=None):
        """Start a model service with the given parameters."""
        model_info, available_models = self.model_manager.match_model_name(model_name)
        if model_info:
            port = port or self.process_manager.get_available_port()
            self.process_manager.start_process(model_info, quant, context_size, port)
        else:
            raise ValueError(f"Model {model_name} not found. Available models: {available_models}")

    def stop_service(self, model_name):
        """Stop a model service by its name."""
        self.process_manager.stop_process(model_name)

    def stop_all_services(self):
        """Stop all running services."""
        self.process_manager.stop_all_processes()

    def update_services(self):
        """Update and restart all configured services."""
        self.process_manager.update_processes()

    def get_service_status(self):
        """Get the status of all running services."""
        return {
            "processes": self.process_manager.get_running_processes(),
            "models": self.model_manager.list_models(),
        }
