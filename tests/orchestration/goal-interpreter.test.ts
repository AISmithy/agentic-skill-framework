import { GoalInterpreter } from '../../src/orchestration/goal-interpreter';

describe('GoalInterpreter', () => {
  let interpreter: GoalInterpreter;
  beforeEach(() => { interpreter = new GoalInterpreter(); });

  it('should interpret a raw goal string', () => {
    const goal = interpreter.interpret('Process customer data');
    expect(goal.id).toBeTruthy();
    expect(goal.description).toBe('Process customer data');
  });

  it('should trim whitespace', () => { expect(interpreter.interpret('  hello  ').description).toBe('hello'); });

  it('should generate unique IDs', () => {
    const g1 = interpreter.interpret('goal one'); const g2 = interpreter.interpret('goal two');
    expect(g1.id).not.toBe(g2.id);
  });

  it('should extract keywords', () => {
    const keywords = interpreter.extractKeywords(interpreter.interpret('Process and analyze customer data'));
    expect(keywords).toContain('process'); expect(keywords).toContain('analyze');
    expect(keywords).not.toContain('and');
  });

  it('should clarify goal with context', () => {
    const clarified = interpreter.clarify(interpreter.interpret('Do something'), { priority: 'high' });
    expect(clarified.context?.priority).toBe('high');
  });
});
