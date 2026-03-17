export interface Skill {
  id: string;
  name: string;
  version: string;
  description: string;
  tags: string[];
  owner: string;
  dependencies: string[];
  inputs: Record<string, ParameterDef>;
  outputs: Record<string, ParameterDef>;
  metadata?: Record<string, unknown>;
}

export interface ParameterDef {
  type: 'string' | 'number' | 'boolean' | 'object' | 'array';
  required: boolean;
  description?: string;
  default?: unknown;
}

export interface SkillExecution {
  skillId: string;
  inputs: Record<string, unknown>;
  timeout?: number;
}

export interface SkillResult {
  skillId: string;
  outputs: Record<string, unknown>;
  success: boolean;
  error?: string;
  duration: number;
}

export interface Goal {
  id: string;
  description: string;
  context?: Record<string, unknown>;
}

export interface Plan {
  goalId: string;
  steps: PlanStep[];
  estimatedDuration?: number;
}

export interface PlanStep {
  id: string;
  skillId: string;
  inputs: Record<string, unknown>;
  dependsOn: string[];
  retryPolicy?: RetryPolicy;
}

export interface RetryPolicy {
  maxAttempts: number;
  backoffMs: number;
  backoffMultiplier?: number;
}

export interface ExecutionContext {
  sessionId: string;
  userId?: string;
  planId?: string;
  variables: Record<string, unknown>;
  history: SkillResult[];
}

export interface AuditEntry {
  id: string;
  timestamp: Date;
  action: string;
  actor: string;
  resource: string;
  outcome: 'success' | 'failure' | 'denied';
  details?: Record<string, unknown>;
}

export interface Policy {
  id: string;
  name: string;
  rules: PolicyRule[];
}

export interface PolicyRule {
  action: string;
  resource: string;
  effect: 'allow' | 'deny';
  conditions?: Record<string, unknown>;
}
