import json
import os
import re
import requests

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def _get_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


SYSTEM_PROMPT = """你是一个化学实验教学助手。用户会提供实验目的和参考文献，你需要生成一份结构化的实验步骤。

严格按以下JSON格式输出（不要输出其他内容）：

```json
{
  "steps": [
    {
      "title": "步骤标题（简短，如：称量与配料）",
      "instruction": "详细操作说明，包含具体的试剂用量、仪器、操作手法",
      "data_fields": [
        {"label": "数据名称", "value": "", "unit": "单位"}
      ],
      "precautions": "本步骤的操作注意点和常见错误",
      "prediction": "预期的实验现象（颜色变化、状态变化等）",
      "safety": "安全提醒（化学品危险性、防护措施等）"
    }
  ]
}
```

要求：
- 步骤数量4-10步
- data_fields 自动推断该步骤需要记录的实验数据，每项包含 label/value/unit，value 初始为空字符串
- precautions 要具体实用，不是泛泛而谈
- prediction 要基于化学反应原理，准确描述预期现象
- safety 必须提及具体危险化学品名称和防护措施
- 步骤之间要有逻辑递进关系"""


def generate_steps(objective, references):
    """Call DeepSeek API to generate experiment steps."""
    config = _get_config()
    api_key = config.get("deepseek_api_key", "").strip()
    if not api_key:
        raise ValueError("请先在 config.json 中填写 deepseek_api_key")

    base_url = config.get("deepseek_base_url", "https://api.deepseek.com").rstrip("/")
    model = config.get("deepseek_model", "deepseek-chat")

    user_msg = f"实验目的：\n{objective}\n\n参考文献：\n{references}"

    resp = requests.post(
        f"{base_url}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
        },
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    # Extract JSON from response (handle markdown code fences)
    json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
    if json_match:
        content = json_match.group(1).strip()

    parsed = json.loads(content)
    steps = parsed["steps"]

    # Assign sequential IDs and add ai_notes
    for i, step in enumerate(steps):
        step["id"] = i + 1
        step["completed"] = False
        step["observation"] = ""
        step["photos"] = []
        step["ai_notes"] = {
            "precautions": step.pop("precautions", ""),
            "prediction": step.pop("prediction", ""),
            "safety": step.pop("safety", ""),
        }

    return steps
