from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from app.llm.client import LLMClient
from app.scenario import tools


PLACEHOLDER_RE = re.compile(r"\{=(@[a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)=\}")


def render_text(text: str, tool_results: dict[str, dict[str, Any]]) -> str:
    def repl(m: re.Match) -> str:
        tool_name = m.group(1)   # @get_user_data
        var_name = m.group(2)    # name
        val = tool_results.get(tool_name, {}).get(var_name)
        return "" if val is None else str(val)

    return PLACEHOLDER_RE.sub(repl, text)


@dataclass
class ScenarioRunResult:
    context_text: str             
    user_name: str                
    last_step_scenario: str        
    is_birthday: bool | None       


class ScenarioRunner:
    def __init__(self, scenario_path: str = "data/test_scenario.json"):
        self.scenario_path = scenario_path
        self.llm = LLMClient()

    def _load(self) -> dict:
        with open(self.scenario_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _call_tool(self, tool_name: str) -> dict:
        # tool_name ожидаем как "get_user_data"
        if tool_name == "get_user_data":
            return tools.get_user_data()
        raise ValueError(f"Unknown tool: {tool_name}")

    def _llm_decide_if(self, user_message: str, condition: str) -> bool:
        """
        По ТЗ: решение делает LLM.
        Чтобы было стабильнее, используем LLM, но просим ответить строго TRUE/FALSE.
        """
        prompt = (
            "Ответь строго одним словом: TRUE или FALSE.\n"
            f"Условие: {condition}\n"
            f"Сообщение пользователя: {user_message}\n"
        )
        ans = self.llm.chat([{"role": "user", "content": prompt}], max_tokens=10, temperature=0)
        ans = (ans or "").strip().upper()
        return ans.startswith("TRUE")

    def run_first_message(self, user_message: str) -> ScenarioRunResult:
        data = self._load()
        code = data.get("code", [])

        tool_results: dict[str, dict[str, Any]] = {}
        context_lines: list[str] = []
        last_step = ""
        is_birthday: bool | None = None

        for node in code:
            ntype = node.get("type")
            nid = node.get("id", "")
            last_step = nid or last_step

            if ntype == "text":
                raw = node.get("text", "")
                rendered = render_text(raw, tool_results)
                context_lines.append(rendered)

            elif ntype == "tool":
                tname = node.get("tool")
                result = self._call_tool(tname)
                # по формату плейсхолдера: @get_user_data.name
                tool_results[f"@{tname}"] = result

            elif ntype == "if":
                condition = node.get("condition", "")
                decision = self._llm_decide_if(user_message, condition)
                is_birthday = decision

                branch = node.get("children", []) if decision else node.get("else_children", [])
                for child in branch:
                    cid = child.get("id", "")
                    last_step = cid or last_step
                    if child.get("type") == "text":
                        raw = child.get("text", "")
                        rendered = render_text(raw, tool_results)
                        context_lines.append(rendered)

            elif ntype == "end":
                last_step = nid or "end"
                break

            else:
                raise ValueError(f"Unknown node type: {ntype}")

        user_name = tool_results.get("@get_user_data", {}).get("name", "")
        return ScenarioRunResult(
            context_text="\n".join(context_lines).strip(),
            user_name=str(user_name),
            last_step_scenario=last_step,
            is_birthday=is_birthday,
        )