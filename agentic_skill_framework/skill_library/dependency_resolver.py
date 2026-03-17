from collections import deque
from .registry import SkillRegistry

class DependencyResolver:
    def resolve(self, skill_name: str, registry: SkillRegistry) -> list[str]:
        # Topological sort (Kahn's algorithm) including skill_name itself
        # Build full graph of all reachable skills
        all_skills = set()
        
        def collect(name):
            if name in all_skills:
                return
            all_skills.add(name)
            skill = registry.get(name)
            if skill:
                for dep in skill.metadata.dependencies:
                    collect(dep)
        
        collect(skill_name)
        
        # Build in-degree and adjacency
        in_degree = {s: 0 for s in all_skills}
        adj = {s: [] for s in all_skills}  # dep -> [skills that depend on dep]
        
        for s in all_skills:
            skill = registry.get(s)
            if skill:
                for dep in skill.metadata.dependencies:
                    if dep in all_skills:
                        adj[dep].append(s)
                        in_degree[s] += 1
        
        queue = deque([s for s in all_skills if in_degree[s] == 0])
        result = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(all_skills):
            raise ValueError(f"Circular dependency detected for skill: {skill_name}")
        
        return result

    def validate(self, skill_name: str, registry: SkillRegistry) -> bool:
        skill = registry.get(skill_name)
        if not skill:
            return False
        for dep in skill.metadata.dependencies:
            if not registry.get(dep):
                return False
        return True
