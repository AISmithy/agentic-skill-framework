import { SkillExecutor } from '../../src/runtime/executor';

describe('SkillExecutor', () => {
  let executor: SkillExecutor;
  beforeEach(() => { executor = new SkillExecutor(); });

  it('should execute successfully', async () => {
    const result = await executor.execute({ skillId: 'skill-1', inputs: { x: 1 } }, async (inputs) => ({ result: (inputs.x as number) * 2 }));
    expect(result.success).toBe(true);
    expect(result.outputs.result).toBe(2);
  });

  it('should catch handler errors', async () => {
    const result = await executor.execute({ skillId: 'skill-1', inputs: {} }, async () => { throw new Error('handler error'); });
    expect(result.success).toBe(false);
    expect(result.error).toBe('handler error');
  });

  it('should handle timeout', async () => {
    const result = await executor.execute({ skillId: 'skill-1', inputs: {}, timeout: 50 }, async () => { await new Promise(r => setTimeout(r, 200)); return {}; });
    expect(result.success).toBe(false);
    expect(result.error).toContain('timed out');
  }, 5000);
});
