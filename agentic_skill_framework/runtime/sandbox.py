from typing import Callable, Any

class Sandbox:
    DEFAULT_ALLOWED = ["os", "sys", "json", "math", "datetime", "collections", "itertools", "functools", "typing", "dataclasses"]

    def __init__(self, allowed_modules: list[str] = None, max_memory_mb: int = 512):
        self.allowed_modules = allowed_modules if allowed_modules is not None else list(self.DEFAULT_ALLOWED)
        self.max_memory_mb = max_memory_mb

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        return func(*args, **kwargs)

    def is_allowed_module(self, module_name: str) -> bool:
        return module_name in self.allowed_modules
