import json
from pathlib import Path


def load_default_template():
    template_path = Path("app/template/default_agent.json")

    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)