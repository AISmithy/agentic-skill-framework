import { SkillResult } from '../types';

export class HistoryManager {
  private history: Map<string, SkillResult[]> = new Map();

  record(sessionId: string, result: SkillResult): void {
    const existing = this.history.get(sessionId) ?? [];
    existing.push(result);
    this.history.set(sessionId, existing);
  }

  getHistory(sessionId: string): SkillResult[] {
    return this.history.get(sessionId) ?? [];
  }

  clearHistory(sessionId: string): void {
    this.history.delete(sessionId);
  }

  getLastResult(sessionId: string): SkillResult | undefined {
    const h = this.history.get(sessionId);
    return h && h.length > 0 ? h[h.length - 1] : undefined;
  }

  summarize(sessionId: string): { total: number; succeeded: number; failed: number } {
    const h = this.history.get(sessionId) ?? [];
    const succeeded = h.filter(r => r.success).length;
    return { total: h.length, succeeded, failed: h.length - succeeded };
  }
}
