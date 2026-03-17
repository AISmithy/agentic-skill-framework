import { SkillRegistry } from '../../src/skill-library/registry';
import { Skill } from '../../src/types';

const makeSkill = (overrides?: Partial<Skill>): Skill => ({
  id: 'skill-1',
  name: 'TestSkill',
  version: '1.0.0',
  description: 'A test skill',
  tags: ['test', 'demo'],
  owner: 'team-a',
  dependencies: [],
  inputs: {},
  outputs: {},
  ...overrides,
});

describe('SkillRegistry', () => {
  let registry: SkillRegistry;

  beforeEach(() => {
    registry = new SkillRegistry();
  });

  it('should register and retrieve a skill', () => {
    const skill = makeSkill();
    registry.register(skill);
    expect(registry.get('skill-1')).toEqual(skill);
  });

  it('should return undefined for unknown skill', () => {
    expect(registry.get('unknown')).toBeUndefined();
  });

  it('should unregister a skill', () => {
    registry.register(makeSkill());
    registry.unregister('skill-1');
    expect(registry.get('skill-1')).toBeUndefined();
  });

  it('should get skills by tag', () => {
    registry.register(makeSkill({ id: 'a', tags: ['tag1'] }));
    registry.register(makeSkill({ id: 'b', tags: ['tag2'] }));
    expect(registry.getByTag('tag1')).toHaveLength(1);
    expect(registry.getByTag('tag1')[0].id).toBe('a');
  });

  it('should get all skills', () => {
    registry.register(makeSkill({ id: 'a' }));
    registry.register(makeSkill({ id: 'b' }));
    expect(registry.getAll()).toHaveLength(2);
  });

  it('should search by name', () => {
    registry.register(makeSkill({ id: 'a', name: 'FooSkill' }));
    registry.register(makeSkill({ id: 'b', name: 'BarSkill' }));
    expect(registry.search('Foo')).toHaveLength(1);
    expect(registry.search('Foo')[0].id).toBe('a');
  });

  it('should search by description', () => {
    registry.register(makeSkill({ id: 'a', description: 'processes data' }));
    registry.register(makeSkill({ id: 'b', description: 'sends emails' }));
    expect(registry.search('email')).toHaveLength(1);
  });

  it('should list versions', () => {
    registry.register(makeSkill({ id: 'v1', name: 'MySkill', version: '1.0.0' }));
    registry.register(makeSkill({ id: 'v2', name: 'MySkill', version: '2.0.0' }));
    const versions = registry.listVersions('MySkill');
    expect(versions).toContain('1.0.0');
    expect(versions).toContain('2.0.0');
  });

  it('should get latest version', () => {
    registry.register(makeSkill({ id: 'v1', name: 'MySkill', version: '1.0.0' }));
    registry.register(makeSkill({ id: 'v2', name: 'MySkill', version: '2.0.0' }));
    const latest = registry.getLatestVersion('MySkill');
    expect(latest?.version).toBe('2.0.0');
  });

  it('should return undefined for latest version of unknown skill', () => {
    expect(registry.getLatestVersion('Unknown')).toBeUndefined();
  });
});
