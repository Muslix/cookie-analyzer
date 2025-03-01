"""
Service Provider für die Dependency Injection.
"""

from typing import Dict, Any

class ServiceProvider:
    """A service provider container for dependency injection."""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, service_type: str, implementation) -> None:
        """Registers a service implementation."""
        cls._instances[service_type] = implementation
    
    @classmethod
    def get(cls, service_type: str):
        """Gets a service implementation."""
        if service_type not in cls._instances:
            raise KeyError(f"Service {service_type} not registered")
        return cls._instances[service_type]
    
    @classmethod
    def has(cls, service_type: str) -> bool:
        """Checks if a service is registered."""
        return service_type in cls._instances