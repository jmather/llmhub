from .dependency_container import DependencyContainer
from .config_manager import ConfigManager
from .model_manager import ModelManager
from .state_manager import StateManager
from .log_manager import LogManager
from .process_manager import ProcessManager
from .service_manager import ServiceManager  # New import
import os

# Initialize the dependency container
AppDependencyContainer = DependencyContainer()

AppDependencyContainer.set("global_config_path", "~/.llmhub/config.yaml")
AppDependencyContainer.set("overlay_config_path", os.path.join(os.getcwd(), "config.yaml"))

# Register services with their dependencies passed in via constructor
AppDependencyContainer.register("config_manager", lambda: ConfigManager(
    global_config_path=AppDependencyContainer.params.get("global_config_path", None),
    overlay_config_path=AppDependencyContainer.params.get("overlay_config_path", None)
))
AppDependencyContainer.register("state_manager", lambda: StateManager())
AppDependencyContainer.register("log_manager", lambda: LogManager(
    state_manager=AppDependencyContainer.get("state_manager")
))
AppDependencyContainer.register("process_manager", lambda: ProcessManager(
    config_manager=AppDependencyContainer.get("config_manager"),
    state_manager=AppDependencyContainer.get("state_manager"),
    log_manager=AppDependencyContainer.get("log_manager"),
))
AppDependencyContainer.register("model_manager", lambda: ModelManager(
    config_manager=AppDependencyContainer.get("config_manager"),
    state_manager=AppDependencyContainer.get("state_manager")
))
AppDependencyContainer.register("service_manager", lambda: ServiceManager(  # Register ServiceManager
    process_manager=AppDependencyContainer.get("process_manager"),
    model_manager=AppDependencyContainer.get("model_manager"),
    config_manager=AppDependencyContainer.get("config_manager"),
    state_manager=AppDependencyContainer.get("state_manager")
))
