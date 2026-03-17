import { WorkflowEngine } from '../../src/orchestration/workflow-engine';
import { SkillExecutor } from '../../src/runtime/executor';
import { SkillRouter } from '../../src/orchestration/skill-router';
import { SkillRegistry } from '../../src/skill-library/registry';
import { Plan, ExecutionContext, Skill } from '../../src/types';

const makeSkill = (id: string): Skill => ({ id, name: id, version: '1.0.0', description: 'test', tags: [], owner: 'team', dependencies: [], inputs: {}, outputs: {} });
const makeContext = (): ExecutionContext => ({ sessionId: 'sess-1', variables: {}, history: [] });

describe('WorkflowEngine', () => {
  let engine: WorkflowEngine; let registry: SkillRegistry;
  beforeEach(() => { registry = new SkillRegistry(); engine = new WorkflowEngine(new SkillExecutor(), new SkillRouter(registry)); });

  it('should execute a simple plan', async () => {
    registry.register(makeSkill('s1'));
    const results = await engine.execute({ goalId: 'g1', steps: [{ id: 'step-1', skillId: 's1', inputs: {}, dependsOn: [] }] }, makeContext(), new Map([['s1', async () => ({ result: 'done' })]]));
    expect(results[0].success).toBe(true);
  });

  it('should fail gracefully when handler missing', async () => {
    const results = await engine.execute({ goalId: 'g1', steps: [{ id: 'step-1', skillId: 'missing', inputs: {}, dependsOn: [] }] }, makeContext(), new Map());
    expect(results[0].success).toBe(false);
  });

  it('should execute steps in dependency order', async () => {
    const order: string[] = [];
    const plan: Plan = { goalId: 'g1', steps: [{ id: 'step-2', skillId: 's2', inputs: {}, dependsOn: ['step-1'] }, { id: 'step-1', skillId: 's1', inputs: {}, dependsOn: [] }] };
    await engine.execute(plan, makeContext(), new Map([['s1', async () => { order.push('s1'); return {}; }], ['s2', async () => { order.push('s2'); return {}; }]]));
    expect(order).toEqual(['s1', 's2']);
  });
});
