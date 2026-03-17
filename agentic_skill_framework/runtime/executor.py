import time
import concurrent.futures
from typing import Optional
from ..models import SkillResult
from ..skill_library.skill_definition import Skill
from .circuit_breaker import CircuitBreaker

class Executor:
    def __init__(self, circuit_breaker: CircuitBreaker = None, default_timeout: float = 30.0, default_max_retries: int = 3):
        self.circuit_breaker = circuit_breaker
        self.default_timeout = default_timeout
        self.default_max_retries = default_max_retries

    def execute(self, skill: Skill, inputs: dict, timeout: float = None, max_retries: int = None) -> SkillResult:
        timeout = timeout if timeout is not None else self.default_timeout
        max_retries = max_retries if max_retries is not None else self.default_max_retries
        
        last_error = None
        start_time = time.time()
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    time.sleep(0.01 * (2 ** attempt))
                
                def _run():
                    if self.circuit_breaker:
                        return self.circuit_breaker.call(skill.execute, inputs)
                    return skill.execute(inputs)
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run)
                    try:
                        result = future.result(timeout=timeout)
                        duration_ms = (time.time() - start_time) * 1000
                        result.duration_ms = duration_ms
                        return result
                    except concurrent.futures.TimeoutError:
                        duration_ms = (time.time() - start_time) * 1000
                        return SkillResult(
                            skill_name=skill.metadata.name,
                            status="error",
                            output=None,
                            error="Execution timed out",
                            duration_ms=duration_ms
                        )
            except Exception as e:
                last_error = e
                continue
        
        duration_ms = (time.time() - start_time) * 1000
        return SkillResult(
            skill_name=skill.metadata.name,
            status="error",
            output=None,
            error=str(last_error),
            duration_ms=duration_ms
        )
