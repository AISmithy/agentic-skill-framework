export interface MetricData {
  name: string;
  type: 'counter' | 'gauge' | 'histogram';
  value: number;
  count?: number;
  sum?: number;
}

export class MetricsCollector {
  private metrics: Map<string, MetricData> = new Map();

  increment(metric: string, value = 1): void {
    const existing = this.metrics.get(metric);
    if (existing && existing.type === 'counter') {
      existing.value += value;
    } else {
      this.metrics.set(metric, { name: metric, type: 'counter', value });
    }
  }

  gauge(metric: string, value: number): void {
    this.metrics.set(metric, { name: metric, type: 'gauge', value });
  }

  histogram(metric: string, value: number): void {
    const existing = this.metrics.get(metric);
    if (existing && existing.type === 'histogram') {
      existing.count = (existing.count ?? 0) + 1;
      existing.sum = (existing.sum ?? 0) + value;
      existing.value = existing.sum / existing.count;
    } else {
      this.metrics.set(metric, { name: metric, type: 'histogram', value, count: 1, sum: value });
    }
  }

  getMetric(metric: string): MetricData | undefined {
    return this.metrics.get(metric);
  }

  getAllMetrics(): MetricData[] {
    return Array.from(this.metrics.values());
  }

  reset(): void {
    this.metrics.clear();
  }
}
