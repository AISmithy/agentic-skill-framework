import { Skill } from '../types';

export class SkillRegistry {
  private skills: Map<string, Skill> = new Map();

  register(skill: Skill): void {
    this.skills.set(skill.id, skill);
  }

  unregister(skillId: string): void {
    this.skills.delete(skillId);
  }

  get(skillId: string): Skill | undefined {
    return this.skills.get(skillId);
  }

  getByTag(tag: string): Skill[] {
    return Array.from(this.skills.values()).filter(s => s.tags.includes(tag));
  }

  getAll(): Skill[] {
    return Array.from(this.skills.values());
  }

  search(query: string): Skill[] {
    const q = query.toLowerCase();
    return Array.from(this.skills.values()).filter(
      s => s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q)
    );
  }

  listVersions(skillName: string): string[] {
    return Array.from(this.skills.values())
      .filter(s => s.name === skillName)
      .map(s => s.version);
  }

  getLatestVersion(skillName: string): Skill | undefined {
    const versions = Array.from(this.skills.values()).filter(s => s.name === skillName);
    if (versions.length === 0) return undefined;
    return versions.sort((a, b) => b.version.localeCompare(a.version, undefined, { numeric: true }))[0];
  }
}
