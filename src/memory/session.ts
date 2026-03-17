import { ExecutionContext } from '../types';

export class SessionManager {
  private sessions: Map<string, ExecutionContext> = new Map();

  createSession(userId?: string): string {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const context: ExecutionContext = {
      sessionId,
      userId,
      variables: {},
      history: [],
    };
    this.sessions.set(sessionId, context);
    return sessionId;
  }

  getSession(sessionId: string): ExecutionContext | undefined {
    return this.sessions.get(sessionId);
  }

  updateSession(sessionId: string, updates: Partial<ExecutionContext>): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      this.sessions.set(sessionId, { ...session, ...updates });
    }
  }

  destroySession(sessionId: string): void {
    this.sessions.delete(sessionId);
  }

  getVariable(sessionId: string, key: string): unknown {
    return this.sessions.get(sessionId)?.variables[key];
  }

  setVariable(sessionId: string, key: string, value: unknown): void {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.variables[key] = value;
    }
  }

  listSessions(): string[] {
    return Array.from(this.sessions.keys());
  }
}
