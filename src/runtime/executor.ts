import { SkillExecution, SkillResult } from '../types';

interface ExecutorOptions {
  defaultTimeoutMs?: number;
}

export class SkillExecutor {
  private readonly defaultTimeoutMs: number;

  constructor(options?: ExecutorOptions) {
    this.defaultTimeoutMs = options?.defaultTimeoutMs ?? 30000;
  }

  async execute(
    execution: SkillExecution,
    handler: (inputs: Record<string, unknown>) => Promise<Record<string, unknown>>
  ): Promise<SkillResult> {
    const start = Date.now();
    const timeoutMs = execution.timeout ?? this.defaultTimeoutMs;

    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error(`Execution timed out after ${timeoutMs}ms`)), timeoutMs)
    );

    try {
      const outputs = await Promise.race([handler(execution.inputs), timeoutPromise]);
      return {
        skillId: execution.skillId,
        outputs,
        success: true,
        duration: Date.now() - start,
      };
    } catch (err) {
      return {
        skillId: execution.skillId,
        outputs: {},
        success: false,
        error: err instanceof Error ? err.message : String(err),
        duration: Date.now() - start,
      };
    }
  }
}
