# llmhub_lib/dependency_container.py
class DependencyContainer:
    def __init__(self):
        self.params = {}
        self._services = {}
        self._instances = {}

    def set(self, name, value):
        """Set a parameter by name."""
        self.params[name] = value

    def register(self, name, cls, *args, **kwargs):
        """Register a service by name with its dependencies."""
        self._services[name] = (cls, args, kwargs)

    def get(self, name):
        """Get the service instance, initializing it if necessary."""
        if name not in self._instances:
            if name not in self._services:
                raise ValueError(f"Service '{name}' is not registered.")
            service_cls, args, kwargs = self._services[name]
            self._instances[name] = service_cls(*args, **kwargs)
        return self._instances[name]