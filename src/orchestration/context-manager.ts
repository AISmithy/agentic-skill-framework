import { ExecutionContext } from '../types';
import { SessionManager } from '../memory/session';

export class ContextManager {
  constructor(private sessionManager: SessionManager) {}

  getContext(sessionId: string): ExecutionContext | undefined {
    return this.sessionManager.getSession(sessionId);
  }

  mergeContext(sessionId: string, updates: Partial<ExecutionContext>): ExecutionContext {
    this.sessionManager.updateSession(sessionId, updates);
    return this.sessionManager.getSession(sessionId)!;
  }

  setVariable(sessionId: string, key: string, value: unknown): void {
    this.sessionManager.setVariable(sessionId, key, value);
  }

  getVariable(sessionId: string, key: string): unknown {
    return this.sessionManager.getVariable(sessionId, key);
  }

  snapshotContext(sessionId: string): ExecutionContext | undefined {
    const ctx = this.sessionManager.getSession(sessionId);
    if (!ctx) return undefined;
    return JSON.parse(JSON.stringify(ctx)) as ExecutionContext;
  }

  restoreContext(sessionId: string, snapshot: ExecutionContext): void {
    this.sessionManager.updateSession(sessionId, snapshot);
  }
}
