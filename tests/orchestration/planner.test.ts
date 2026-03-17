import { Planner } from '../../src/orchestration/planner';
import { SkillRegistry } from '../../src/skill-library/registry';
import { Goal, Skill } from '../../src/types';

const makeSkill = (id: string, name: string, tags: string[]): Skill => ({ id, name, version: '1.0.0', description: `${name} skill`, tags, owner: 'team', dependencies: [], inputs: {}, outputs: {} });

describe('Planner', () => {
  let registry: SkillRegistry; let planner: Planner;
  beforeEach(() => { registry = new SkillRegistry(); planner = new Planner(registry); });

  it('should create a plan with matching skills', () => {
    const skill = makeSkill('s1', 'DataProcessor', ['data']);
    registry.register(skill);
    const plan = planner.createPlan({ id: 'g1', description: 'Process data' }, [skill]);
    expect(plan.steps.length).toBeGreaterThan(0);
  });

  it('should create empty plan when no skills match', () => {
    expect(planner.createPlan({ id: 'g1', description: 'xyz' }, []).steps).toHaveLength(0);
  });

  it('should validate a valid plan', () => {
    registry.register(makeSkill('s1', 'Skill1', ['tag']));
    expect(planner.validatePlan({ goalId: 'g1', steps: [{ id: 'step-1', skillId: 's1', inputs: {}, dependsOn: [] }] }).valid).toBe(true);
  });

  it('should detect missing skill', () => {
    const result = planner.validatePlan({ goalId: 'g1', steps: [{ id: 'step-1', skillId: 'missing', inputs: {}, dependsOn: [] }] });
    expect(result.valid).toBe(false);
  });
});
