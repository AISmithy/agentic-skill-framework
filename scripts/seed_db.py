"""Seed the database with built-in skills from their manifests."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main() -> None:
    from agentic.core.config import get_settings
    from agentic.layer3_skill_library.metadata_catalog import MetadataCatalog
    from agentic.layer3_skill_library.models.skill import SkillDefinition

    settings = get_settings()
    catalog = MetadataCatalog(db_path=settings.db_path)
    await catalog.initialize()

    skills_dir = Path(__file__).parent.parent / "skills"
    manifests = list(skills_dir.rglob("manifest.json"))

    for manifest_path in manifests:
        try:
            data = json.loads(manifest_path.read_text())
            skill = SkillDefinition.model_validate(data)
            await catalog.save(skill)
            print(f"  Seeded: {skill.skill_id}")
        except Exception as exc:
            print(f"  Failed {manifest_path}: {exc}", file=sys.stderr)

    print(f"\nSeeded {len(manifests)} skill(s) into {settings.db_path}")


if __name__ == "__main__":
    asyncio.run(main())
