import { Goal, Plan, PlanStep, Skill } from '../types';
import { SkillRegistry } from '../skill-library/registry';

export class Planner {
  constructor(private registry: SkillRegistry) {}

  createPlan(goal: Goal, availableSkills: Skill[]): Plan {
    const keywords = goal.description
      .split(/\s+/)
      .map(w => w.toLowerCase().replace(/[^a-z0-9]/g, ''))
      .filter(w => w.length > 2);

    const matchedSkills = availableSkills.filter(skill =>
      keywords.some(
        kw =>
          skill.name.toLowerCase().includes(kw) ||
          skill.tags.some(t => t.toLowerCase().includes(kw))
      )
    );

    const steps: PlanStep[] = matchedSkills.map((skill, i) => ({
      id: `step-${i + 1}`,
      skillId: skill.id,
      inputs: {},
      dependsOn: i > 0 ? [`step-${i}`] : [],
    }));

    return { goalId: goal.id, steps };
  }

  validatePlan(plan: Plan): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const stepIds = new Set(plan.steps.map(s => s.id));

    for (const step of plan.steps) {
      if (!this.registry.get(step.skillId)) {
        errors.push(`Skill not found: ${step.skillId}`);
      }
      for (const dep of step.dependsOn) {
        if (!stepIds.has(dep)) {
          errors.push(`Step ${step.id} depends on unknown step: ${dep}`);
        }
      }
    }

    // Check for cycles
    if (this.hasCycle(plan.steps)) {
      errors.push('Plan has circular dependencies');
    }

    return { valid: errors.length === 0, errors };
  }

  private hasCycle(steps: PlanStep[]): boolean {
    const visited = new Set<string>();
    const stack = new Set<string>();

    const dfs = (stepId: string): boolean => {
      if (stack.has(stepId)) return true;
      if (visited.has(stepId)) return false;
      visited.add(stepId);
      stack.add(stepId);
      const step = steps.find(s => s.id === stepId);
      if (step) {
        for (const dep of step.dependsOn) {
          if (dfs(dep)) return true;
        }
      }
      stack.delete(stepId);
      return false;
    };

    return steps.some(s => dfs(s.id));
  }

  optimizePlan(plan: Plan): Plan {
    return plan;
  }
}
