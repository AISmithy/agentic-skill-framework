from typing import Optional
from ..models import SkillMetadata

class MetadataCatalog:
    def __init__(self):
        self._catalog: dict[str, SkillMetadata] = {}

    def add(self, metadata: SkillMetadata) -> None:
        self._catalog[metadata.name] = metadata

    def get(self, name: str) -> Optional[SkillMetadata]:
        return self._catalog.get(name)

    def search(self, query: str) -> list[SkillMetadata]:
        q = query.lower()
        results = []
        for m in self._catalog.values():
            if (q in m.name.lower() or q in m.description.lower() or
                    any(q in t.lower() for t in m.tags)):
                results.append(m)
        return results

    def list_versions(self, name: str) -> list[str]:
        m = self._catalog.get(name)
        return [m.version] if m else []

    def list_by_owner(self, owner: str) -> list[SkillMetadata]:
        return [m for m in self._catalog.values() if m.owner == owner]

    def list_by_tag(self, tag: str) -> list[SkillMetadata]:
        return [m for m in self._catalog.values() if tag in m.tags]
