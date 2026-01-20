import json
import re
from dataclasses import dataclass
from typing import Any


PLACEHOLDER_RE = re.compile(r"\{=(@[a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)=\}")


@dataclass
class Scenario:
    name: str
    code: list[dict]


def load_scenario(path: str) -> Scenario:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "name" not in data or "code" not in data:
        raise ValueError("Scenario JSON must contain 'name' and 'code'")
    return Scenario(name=data["name"], code=data["code"])


def render_text(text: str, tool_results: dict[str, dict[str, Any]]) -> str:
    """
    Подстановка плейсхолдеров формата:
      {=@get_user_data.name=}
    tool_results:
      {"@get_user_data": {"name":"Антон", "age":"25"}}
    """
    def repl(match: re.Match) -> str:
        tool_name = match.group(1)      # например @get_user_data
        var_name = match.group(2)       # например name
        val = tool_results.get(tool_name, {}).get(var_name)
        return "" if val is None else str(val)

    return PLACEHOLDER_RE.sub(repl, text)