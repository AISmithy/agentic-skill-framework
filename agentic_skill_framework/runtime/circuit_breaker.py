import time
from typing import Callable, Any

class CircuitBreakerOpenError(Exception):
    pass

class CircuitBreaker:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self._state == self.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = self.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self._state == self.HALF_OPEN:
                self.reset()
            elif self._state == self.CLOSED:
                self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._state == self.HALF_OPEN or self._failure_count >= self.failure_threshold:
                self._state = self.OPEN
            raise

    def get_state(self) -> str:
        return self._state

    def reset(self) -> None:
        self._state = self.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
