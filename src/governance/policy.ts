import { Policy, PolicyRule } from '../types';

export class PolicyEngine {
  private policies: Map<string, Policy> = new Map();

  addPolicy(policy: Policy): void {
    this.policies.set(policy.id, policy);
  }

  removePolicy(policyId: string): void {
    this.policies.delete(policyId);
  }

  evaluate(action: string, resource: string, _context?: Record<string, unknown>): 'allow' | 'deny' {
    for (const policy of this.policies.values()) {
      for (const rule of policy.rules) {
        if (this.ruleMatches(rule, action, resource)) {
          return rule.effect;
        }
      }
    }
    return 'deny';
  }

  private ruleMatches(rule: PolicyRule, action: string, resource: string): boolean {
    const actionMatch = rule.action === '*' || rule.action === action;
    const resourceMatch = rule.resource === '*' || rule.resource === resource;
    return actionMatch && resourceMatch;
  }

  getEffectivePolicies(action: string, resource: string): Policy[] {
    return Array.from(this.policies.values()).filter(policy =>
      policy.rules.some(rule => this.ruleMatches(rule, action, resource))
    );
  }
}
