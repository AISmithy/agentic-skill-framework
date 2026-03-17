import { SessionManager } from '../../src/memory/session';

describe('SessionManager', () => {
  let manager: SessionManager;

  beforeEach(() => {
    manager = new SessionManager();
  });

  it('should create a session and return an id', () => {
    const id = manager.createSession();
    expect(id).toBeTruthy();
    expect(typeof id).toBe('string');
  });

  it('should create session with userId', () => {
    const id = manager.createSession('user-123');
    const session = manager.getSession(id);
    expect(session?.userId).toBe('user-123');
  });

  it('should return undefined for unknown session', () => {
    expect(manager.getSession('unknown')).toBeUndefined();
  });

  it('should update a session', () => {
    const id = manager.createSession();
    manager.updateSession(id, { planId: 'plan-1' });
    expect(manager.getSession(id)?.planId).toBe('plan-1');
  });

  it('should destroy a session', () => {
    const id = manager.createSession();
    manager.destroySession(id);
    expect(manager.getSession(id)).toBeUndefined();
  });

  it('should set and get variables', () => {
    const id = manager.createSession();
    manager.setVariable(id, 'foo', 42);
    expect(manager.getVariable(id, 'foo')).toBe(42);
  });

  it('should return undefined for missing variable', () => {
    const id = manager.createSession();
    expect(manager.getVariable(id, 'missing')).toBeUndefined();
  });

  it('should list sessions', () => {
    const id1 = manager.createSession();
    const id2 = manager.createSession();
    const list = manager.listSessions();
    expect(list).toContain(id1);
    expect(list).toContain(id2);
  });
});
