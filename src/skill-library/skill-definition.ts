import { Skill, ParameterDef } from '../types';

export class SkillDefinition implements Skill {
  id: string;
  name: string;
  version: string;
  description: string;
  tags: string[];
  owner: string;
  dependencies: string[];
  inputs: Record<string, ParameterDef>;
  outputs: Record<string, ParameterDef>;
  metadata?: Record<string, unknown>;

  constructor(data: Partial<Skill>) {
    this.id = data.id ?? '';
    this.name = data.name ?? '';
    this.version = data.version ?? '1.0.0';
    this.description = data.description ?? '';
    this.tags = data.tags ?? [];
    this.owner = data.owner ?? '';
    this.dependencies = data.dependencies ?? [];
    this.inputs = data.inputs ?? {};
    this.outputs = data.outputs ?? {};
    this.metadata = data.metadata;
  }

  validate(): boolean {
    return !!(this.id && this.name && this.version && this.owner);
  }

  toJSON(): Skill {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      description: this.description,
      tags: this.tags,
      owner: this.owner,
      dependencies: this.dependencies,
      inputs: this.inputs,
      outputs: this.outputs,
      metadata: this.metadata,
    };
  }

  static fromJSON(data: unknown): SkillDefinition {
    if (typeof data !== 'object' || data === null) {
      throw new Error('Invalid skill data');
    }
    return new SkillDefinition(data as Partial<Skill>);
  }
}
