import { AuditEntry } from '../types';

export class AuditLogger {
  private entries: AuditEntry[] = [];

  log(entry: Omit<AuditEntry, 'id' | 'timestamp'>): AuditEntry {
    const fullEntry: AuditEntry = {
      ...entry,
      id: `audit-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      timestamp: new Date(),
    };
    this.entries.push(fullEntry);
    return fullEntry;
  }

  getEntries(filter?: { actor?: string; action?: string; outcome?: string }): AuditEntry[] {
    if (!filter) return [...this.entries];
    return this.entries.filter(e => {
      if (filter.actor && e.actor !== filter.actor) return false;
      if (filter.action && e.action !== filter.action) return false;
      if (filter.outcome && e.outcome !== filter.outcome) return false;
      return true;
    });
  }

  clear(): void {
    this.entries = [];
  }

  exportJSON(): string {
    return JSON.stringify(this.entries, null, 2);
  }
}
