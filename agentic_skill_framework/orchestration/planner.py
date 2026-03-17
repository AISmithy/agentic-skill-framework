import re
from ..models import Goal, Plan, PlanStep, SkillMetadata

class Planner:
    def create_plan(self, goal: Goal, available_skills: list[SkillMetadata]) -> Plan:
        words = set(re.split(r'[\s\W]+', goal.description.lower()))
        words.discard('')
        matched = []
        for skill in available_skills:
            skill_words = set(re.split(r'[\s\W]+', skill.name.lower()))
            skill_words.discard('')
            if words & skill_words:
                matched.append(skill)
                continue
            if any(tag.lower() in goal.description.lower() for tag in skill.tags):
                matched.append(skill)
        
        if matched:
            steps = [
                PlanStep(step_id=f"step_{i}", skill_name=s.name, inputs={}, depends_on=[])
                for i, s in enumerate(matched)
            ]
        else:
            steps = [PlanStep(step_id="step_0", skill_name="noop", inputs={}, depends_on=[])]
        
        return Plan(goal_id=goal.id, steps=steps)
