import { SkillResult, RetryPolicy } from '../types';

export interface ReflectionReport {
  success: boolean;
  failedSteps: string[];
  suggestions: string[];
  shouldRetry: boolean;
}

export class ReflectionManager {
  reflect(results: SkillResult[]): ReflectionReport {
    const failedSteps = results.filter(r => !r.success).map(r => r.skillId);
    const suggestions = failedSteps.map(id => `Consider retrying or replacing skill: ${id}`);
    return {
      success: failedSteps.length === 0,
      failedSteps,
      suggestions,
      shouldRetry: failedSteps.length > 0,
    };
  }

  shouldRetry(result: SkillResult, policy: RetryPolicy, attempt: number): boolean {
    return !result.success && attempt < policy.maxAttempts;
  }

  computeBackoff(policy: RetryPolicy, attempt: number): number {
    const multiplier = policy.backoffMultiplier ?? 1;
    return policy.backoffMs * Math.pow(multiplier, attempt - 1);
  }

  async retryWithPolicy<T>(fn: () => Promise<T>, policy: RetryPolicy): Promise<T> {
    let lastError: unknown;
    for (let attempt = 1; attempt <= policy.maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (err) {
        lastError = err;
        if (attempt < policy.maxAttempts) {
          const backoff = this.computeBackoff(policy, attempt);
          await new Promise(resolve => setTimeout(resolve, backoff));
        }
      }
    }
    throw lastError;
  }
}
