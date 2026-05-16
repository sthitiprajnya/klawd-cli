import os
import ast
import logging

logger = logging.getLogger("SkillManager")

class SkillManager:
    def __init__(self, skills_dir: str = "omni_agent/skills"):
        self.skills_dir = skills_dir
        self.loaded_skills = {}

    def list_skills(self):
        """Returns a list of currently absorbed skills."""
        if not os.path.exists(self.skills_dir):
            return []

        skills = []
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                skills.append(filename[:-3])
        return skills

    def load_skill(self, skill_name: str):
        """
        Safely parses the skill to extract metadata and function signatures
        WITHOUT executing arbitrary code, preventing RCE vulnerabilities.
        """
        module_path = os.path.join(self.skills_dir, f"{skill_name}.py")
        try:
            with open(module_path, "r") as f:
                source = f.read()

            # Parse the AST to extract function definitions safely
            tree = ast.parse(source)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            # Store the signatures/metadata rather than executing the module
            self.loaded_skills[skill_name] = {
                "functions": functions,
                "source": source
            }
            logger.info(f"Successfully absorbed skill context: {skill_name} providing {functions}")
            return True
        except Exception as e:
            logger.error(f"Failed to parse skill {skill_name}: {e}")
            return False

skill_manager = SkillManager()
