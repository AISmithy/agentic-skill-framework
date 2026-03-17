import time
from typing import Any, Optional

class ArtifactStore:
    def __init__(self):
        self._artifacts: dict[str, dict] = {}

    def save(self, artifact_id: str, data: Any, artifact_type: str, metadata: dict = None) -> None:
        self._artifacts[artifact_id] = {
            "artifact_id": artifact_id,
            "data": data,
            "artifact_type": artifact_type,
            "metadata": metadata or {},
            "saved_at": time.time()
        }

    def load(self, artifact_id: str) -> Optional[dict]:
        return self._artifacts.get(artifact_id)

    def list_artifacts(self, artifact_type: str = None) -> list[dict]:
        if artifact_type:
            return [a for a in self._artifacts.values() if a["artifact_type"] == artifact_type]
        return list(self._artifacts.values())

    def delete(self, artifact_id: str) -> bool:
        if artifact_id in self._artifacts:
            del self._artifacts[artifact_id]
            return True
        return False
