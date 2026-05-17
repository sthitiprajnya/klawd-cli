import os
import ast
import logging

logger = logging.getLogger("SkillManager")

class SkillManager:
    def __init__(self, skills_dir: str = "src/infrastructure/skills"):
        self.skills_dir = skills_dir
        self.loaded_skills = {}
        os.makedirs(self.skills_dir, exist_ok=True)

    def list_skills(self):
        skills_context = {}
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                skill_name = filename[:-3]
                skills_context[skill_name] = self.loaded_skills.get(skill_name, {}).get("functions", "Unparsed")
        return skills_context

    def load_skill(self, skill_name: str, source_code: str = None) -> bool:
        module_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        try:
            if source_code:
                with open(module_path, "w") as f:
                    f.write(source_code)

            with open(module_path, "r") as f:
                source = f.read()

            tree = ast.parse(source)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            self.loaded_skills[skill_name] = {"functions": functions}
            return True
        except Exception as e:
            logger.error(f"Failed to parse skill {skill_name}: {e}")
            return False

skill_manager = SkillManager()
