export class ArtifactStore {
  private store: Map<string, Map<string, unknown>> = new Map();

  private getOrCreate(sessionId: string): Map<string, unknown> {
    if (!this.store.has(sessionId)) {
      this.store.set(sessionId, new Map());
    }
    return this.store.get(sessionId)!;
  }

  save(sessionId: string, key: string, data: unknown): void {
    this.getOrCreate(sessionId).set(key, data);
  }

  load(sessionId: string, key: string): unknown {
    return this.store.get(sessionId)?.get(key);
  }

  delete(sessionId: string, key: string): void {
    this.store.get(sessionId)?.delete(key);
  }

  list(sessionId: string): string[] {
    return Array.from(this.store.get(sessionId)?.keys() ?? []);
  }

  clear(sessionId: string): void {
    this.store.delete(sessionId);
  }
}
