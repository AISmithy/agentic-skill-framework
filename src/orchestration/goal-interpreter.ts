import { Goal } from '../types';

export class GoalInterpreter {
  interpret(rawGoal: string): Goal {
    return {
      id: `goal-${Math.random().toString(36).slice(2)}-${Date.now()}`,
      description: rawGoal.trim(),
    };
  }

  extractKeywords(goal: Goal): string[] {
    return goal.description
      .split(/\s+/)
      .map(w => w.toLowerCase().replace(/[^a-z0-9]/g, ''))
      .filter(w => w.length > 3);
  }

  clarify(goal: Goal, context: Record<string, unknown>): Goal {
    return {
      ...goal,
      context: { ...goal.context, ...context },
    };
  }
}
