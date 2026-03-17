import { SkillRouter } from '../../src/orchestration/skill-router';
import { SkillRegistry } from '../../src/skill-library/registry';
import { Skill } from '../../src/types';

const makeSkill = (id: string, tags: string[], version = '1.0.0'): Skill => ({ id, name: `Skill-${id}`, version, description: 'test', tags, owner: 'team', dependencies: [], inputs: {}, outputs: {} });

describe('SkillRouter', () => {
  let registry: SkillRegistry; let router: SkillRouter;
  beforeEach(() => { registry = new SkillRegistry(); router = new SkillRouter(registry); });

  it('should route by id', () => { const skill = makeSkill('s1', ['tag1']); registry.register(skill); expect(router.route('s1')).toEqual(skill); });
  it('should return undefined for unknown', () => { expect(router.route('unknown')).toBeUndefined(); });
  it('should return undefined on version mismatch', () => { registry.register(makeSkill('s1', [], '1.0.0')); expect(router.route('s1', '2.0.0')).toBeUndefined(); });
  it('should find best match', () => {
    registry.register(makeSkill('s1', ['a', 'b'])); registry.register(makeSkill('s2', ['a', 'b', 'c']));
    expect(router.findBestMatch(['a', 'b', 'c'])?.id).toBe('s2');
  });
  it('should return undefined when no skills', () => { expect(router.findBestMatch(['a'])).toBeUndefined(); });
});
