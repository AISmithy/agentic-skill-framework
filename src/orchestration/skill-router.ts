import { Skill } from '../types';
import { SkillRegistry } from '../skill-library/registry';

export class SkillRouter {
  constructor(private registry: SkillRegistry) {}

  route(skillId: string, version?: string): Skill | undefined {
    const skill = this.registry.get(skillId);
    if (!skill) return undefined;
    if (version && skill.version !== version) return undefined;
    return skill;
  }

  routeByCapability(capability: string): Skill[] {
    return this.registry.getByTag(capability);
  }

  findBestMatch(requirements: string[]): Skill | undefined {
    const skills = this.registry.getAll();
    if (skills.length === 0) return undefined;

    let best: Skill | undefined;
    let bestScore = -1;

    for (const skill of skills) {
      const score = requirements.filter(r => skill.tags.includes(r)).length;
      if (score > bestScore) {
        bestScore = score;
        best = skill;
      }
    }

    return best;
  }
}
