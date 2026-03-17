import fnmatch
from ..models import PolicyDecision

class PolicyEngine:
    def __init__(self):
        self._policies: dict[str, dict] = {}

    def add_policy(self, policy_id: str, rules: dict) -> None:
        self._policies[policy_id] = {"policy_id": policy_id, "rules": rules}

    def evaluate(self, user_id: str, resource: str, action: str, context: dict = None) -> PolicyDecision:
        for policy_id, policy in self._policies.items():
            for pattern, allowed_actions in policy["rules"].items():
                if fnmatch.fnmatch(resource, pattern):
                    if action in allowed_actions:
                        return PolicyDecision(allowed=True, reason=f"Allowed by policy {policy_id}", policy_id=policy_id)
        return PolicyDecision(allowed=False, reason="No matching policy allows this action", policy_id="")

    def list_policies(self) -> list[dict]:
        return list(self._policies.values())

    def remove_policy(self, policy_id: str) -> bool:
        if policy_id in self._policies:
            del self._policies[policy_id]
            return True
        return False
