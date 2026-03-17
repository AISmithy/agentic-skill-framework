import { ReflectionManager } from '../../src/orchestration/reflection-manager';
import { SkillResult, RetryPolicy } from '../../src/types';

const makeResult = (skillId: string, success: boolean): SkillResult => ({ skillId, success, outputs: {}, duration: 10, ...(success ? {} : { error: 'failed' }) });

describe('ReflectionManager', () => {
  let manager: ReflectionManager;
  beforeEach(() => { manager = new ReflectionManager(); });

  it('should reflect success', () => { expect(manager.reflect([makeResult('s1', true)]).success).toBe(true); });
  it('should reflect failures', () => { const r = manager.reflect([makeResult('s1', false)]); expect(r.success).toBe(false); expect(r.shouldRetry).toBe(true); });
  it('should determine retry', () => {
    const policy: RetryPolicy = { maxAttempts: 3, backoffMs: 100 };
    expect(manager.shouldRetry(makeResult('s1', false), policy, 1)).toBe(true);
    expect(manager.shouldRetry(makeResult('s1', false), policy, 3)).toBe(false);
  });
  it('should compute backoff', () => {
    const policy: RetryPolicy = { maxAttempts: 3, backoffMs: 100, backoffMultiplier: 2 };
    expect(manager.computeBackoff(policy, 1)).toBe(100); expect(manager.computeBackoff(policy, 2)).toBe(200);
  });
  it('should retry with policy', async () => {
    let n = 0;
    const result = await manager.retryWithPolicy(async () => { n++; if (n < 3) throw new Error('x'); return 'done'; }, { maxAttempts: 3, backoffMs: 10 });
    expect(result).toBe('done');
  }, 10000);
});
