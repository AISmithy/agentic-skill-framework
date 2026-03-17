import { ContextManager } from '../../src/orchestration/context-manager';
import { SessionManager } from '../../src/memory/session';

describe('ContextManager', () => {
  let sessionManager: SessionManager; let contextManager: ContextManager; let sessionId: string;
  beforeEach(() => { sessionManager = new SessionManager(); contextManager = new ContextManager(sessionManager); sessionId = sessionManager.createSession('user-1'); });

  it('should get context', () => { expect(contextManager.getContext(sessionId)?.sessionId).toBe(sessionId); });
  it('should return undefined for unknown', () => { expect(contextManager.getContext('unknown')).toBeUndefined(); });
  it('should merge context', () => { expect(contextManager.mergeContext(sessionId, { planId: 'p1' }).planId).toBe('p1'); });
  it('should set and get variables', () => { contextManager.setVariable(sessionId, 'k', 'v'); expect(contextManager.getVariable(sessionId, 'k')).toBe('v'); });
  it('should snapshot and restore', () => {
    contextManager.setVariable(sessionId, 'x', 10);
    const snap = contextManager.snapshotContext(sessionId)!;
    contextManager.setVariable(sessionId, 'x', 99);
    contextManager.restoreContext(sessionId, snap);
    expect(contextManager.getVariable(sessionId, 'x')).toBe(10);
  });
});
