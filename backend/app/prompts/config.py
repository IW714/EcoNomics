# prompts/config.py

from typing import Dict, Any
from pathlib import Path
import yaml

class PromptConfig:
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.prompts = self._load_prompts()
        self.templates = self._load_templates()

    def _load_prompts(self) -> Dict[str, str]:
        with open(self.config_dir / "prompts.yaml", "r") as f:
            return yaml.safe_load(f)

    def _load_templates(self) -> Dict[str, str]:
        with open(self.config_dir / "templates.yaml", "r") as f:
            return yaml.safe_load(f)

    def get_system_prompt(self) -> str:
        return self.prompts["system_prompt"]

    def get_assessment_prompt(self) -> str:
        return self.prompts["assessment_prompt"]

    def get_template(self, template_name: str) -> str:
        return self.templates.get(template_name, "")

    def format_energy_assessment_prompt(self, **kwargs) -> str:
        template = self.get_template("energy_assessment")
        return template.format(**kwargs)
