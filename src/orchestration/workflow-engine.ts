import { Plan, PlanStep, ExecutionContext, SkillResult } from '../types';
import { SkillExecutor } from '../runtime/executor';
import { SkillRouter } from './skill-router';

export class WorkflowEngine {
  constructor(private executor: SkillExecutor, private _router: SkillRouter) {}

  async execute(
    plan: Plan,
    _context: ExecutionContext,
    handlers: Map<string, (inputs: Record<string, unknown>) => Promise<Record<string, unknown>>>
  ): Promise<SkillResult[]> {
    const sortedSteps = this.topologicalSort(plan.steps);
    const results: SkillResult[] = [];
    const resultMap = new Map<string, SkillResult>();

    for (const step of sortedSteps) {
      const handler = handlers.get(step.skillId);
      if (!handler) {
        const result: SkillResult = {
          skillId: step.skillId,
          outputs: {},
          success: false,
          error: `No handler for skill: ${step.skillId}`,
          duration: 0,
        };
        results.push(result);
        resultMap.set(step.id, result);
        continue;
      }

      // Merge inputs from context variables and previous step outputs
      const resolvedInputs: Record<string, unknown> = { ...step.inputs };
      for (const depId of step.dependsOn) {
        const depResult = resultMap.get(depId);
        if (depResult?.success) {
          Object.assign(resolvedInputs, depResult.outputs);
        }
      }

      const result = await this.executor.execute(
        { skillId: step.skillId, inputs: resolvedInputs, timeout: undefined },
        handler
      );
      results.push(result);
      resultMap.set(step.id, result);
    }

    return results;
  }

  private topologicalSort(steps: PlanStep[]): PlanStep[] {
    const sorted: PlanStep[] = [];
    const visited = new Set<string>();
    const stepMap = new Map(steps.map(s => [s.id, s]));

    const visit = (stepId: string) => {
      if (visited.has(stepId)) return;
      visited.add(stepId);
      const step = stepMap.get(stepId);
      if (step) {
        for (const dep of step.dependsOn) {
          visit(dep);
        }
        sorted.push(step);
      }
    };

    for (const step of steps) {
      visit(step.id);
    }

    return sorted;
  }
}
