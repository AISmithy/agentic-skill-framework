import { MetadataCatalog } from '../../src/skill-library/metadata-catalog';

describe('MetadataCatalog', () => {
  let catalog: MetadataCatalog;

  beforeEach(() => {
    catalog = new MetadataCatalog();
  });

  it('should add and retrieve metadata', () => {
    catalog.addMetadata('skill-1', { author: 'Alice' });
    expect(catalog.getMetadata('skill-1')).toEqual({ author: 'Alice' });
  });

  it('should return undefined for missing metadata', () => {
    expect(catalog.getMetadata('unknown')).toBeUndefined();
  });

  it('should update metadata', () => {
    catalog.addMetadata('skill-1', { author: 'Alice' });
    catalog.updateMetadata('skill-1', { version: 2 });
    expect(catalog.getMetadata('skill-1')).toEqual({ author: 'Alice', version: 2 });
  });

  it('should update metadata when not existing', () => {
    catalog.updateMetadata('skill-1', { author: 'Bob' });
    expect(catalog.getMetadata('skill-1')).toEqual({ author: 'Bob' });
  });

  it('should remove metadata', () => {
    catalog.addMetadata('skill-1', { author: 'Alice' });
    catalog.removeMetadata('skill-1');
    expect(catalog.getMetadata('skill-1')).toBeUndefined();
  });

  it('should find by metadata key/value', () => {
    catalog.addMetadata('skill-1', { category: 'ml' });
    catalog.addMetadata('skill-2', { category: 'data' });
    catalog.addMetadata('skill-3', { category: 'ml' });
    const found = catalog.findByMetadata('category', 'ml');
    expect(found).toHaveLength(2);
    expect(found).toContain('skill-1');
    expect(found).toContain('skill-3');
  });

  it('should return empty array when no match', () => {
    expect(catalog.findByMetadata('category', 'nonexistent')).toEqual([]);
  });
});
