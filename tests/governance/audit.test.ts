import { AuditLogger } from '../../src/governance/audit';

describe('AuditLogger', () => {
  let logger: AuditLogger;
  beforeEach(() => { logger = new AuditLogger(); });

  it('should log an entry', () => {
    const entry = logger.log({ action: 'read', actor: 'user-1', resource: '/data', outcome: 'success' });
    expect(entry.id).toBeTruthy(); expect(entry.timestamp).toBeInstanceOf(Date);
  });
  it('should get all entries', () => {
    logger.log({ action: 'read', actor: 'user-1', resource: '/data', outcome: 'success' });
    logger.log({ action: 'write', actor: 'user-2', resource: '/data', outcome: 'success' });
    expect(logger.getEntries()).toHaveLength(2);
  });
  it('should filter by actor', () => {
    logger.log({ action: 'read', actor: 'user-1', resource: '/data', outcome: 'success' });
    logger.log({ action: 'write', actor: 'user-2', resource: '/data', outcome: 'success' });
    expect(logger.getEntries({ actor: 'user-1' })).toHaveLength(1);
  });
  it('should clear entries', () => { logger.log({ action: 'read', actor: 'u', resource: '/d', outcome: 'success' }); logger.clear(); expect(logger.getEntries()).toHaveLength(0); });
  it('should export JSON', () => {
    logger.log({ action: 'read', actor: 'u', resource: '/d', outcome: 'success' });
    expect(Array.isArray(JSON.parse(logger.exportJSON()))).toBe(true);
  });
});
