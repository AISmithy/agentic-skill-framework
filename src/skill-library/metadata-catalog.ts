export class MetadataCatalog {
  private catalog: Map<string, Record<string, unknown>> = new Map();

  addMetadata(skillId: string, metadata: Record<string, unknown>): void {
    this.catalog.set(skillId, { ...metadata });
  }

  getMetadata(skillId: string): Record<string, unknown> | undefined {
    return this.catalog.get(skillId);
  }

  updateMetadata(skillId: string, updates: Record<string, unknown>): void {
    const existing = this.catalog.get(skillId) ?? {};
    this.catalog.set(skillId, { ...existing, ...updates });
  }

  removeMetadata(skillId: string): void {
    this.catalog.delete(skillId);
  }

  findByMetadata(key: string, value: unknown): string[] {
    const result: string[] = [];
    for (const [skillId, metadata] of this.catalog) {
      if (metadata[key] === value) {
        result.push(skillId);
      }
    }
    return result;
  }
}
