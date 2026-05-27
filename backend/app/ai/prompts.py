from typing import Optional

from app.models.discipline import Discipline, subject_label

_CHEMISTRY_TEMPLATE_OPTIONS = (
    "有机合成实验|无机合成实验|分析化学实验|物理化学实验 四选一"
)
_PHYSICS_TEMPLATE_OPTIONS = "力学实验|电磁学实验|光学实验|热学实验 四选一"
_BIOLOGY_TEMPLATE_OPTIONS = (
    "细胞生物学实验|微生物实验|生物化学实验|分子生物学实验 四选一"
)

_COMMON_RULES = """
规则（必须遵守）：
1. 只提取文献中明确写出的内容，不要预测或编造实验现象、用量、时间。
2. 预期现象必须来自文献原文表述，并在 phenomenon_source 中标注来源（如"讲义第3页"、"实验指导书 步骤2"）。
3. 若关键参数文献未写明，在 instructions 末尾追加：【文献未明确，建议咨询指导教师】
4. 安全注意事项单独提取，尽量使用文献原文；常识性警示标注 phenomenon_source 为"常识性提示（文献未载明）"。
5. 若同时提供讲义与文献，以讲义内容为准；冲突处在 instructions 中注明。
6. 输出必须是合法 JSON，不要包含 markdown 代码块。
"""

_JSON_SCHEMA = """
JSON 结构：
{
  "purpose": "实验目的",
  "reagents_instruments": ["试剂或器材条目1", "条目2"],
  "global_safety_notes": ["安全注意事项1"],
  "suggested_template_name": "<从候选模板名中选一>",
  "steps": [
    {
      "title": "步骤标题",
      "instructions": "操作说明（含未明确标注）",
      "expected_phenomenon": "预期现象原文或null",
      "phenomenon_source": "来源标注",
      "safety_notes": "该步骤安全注意或null"
    }
  ]
}
"""


def get_literature_parse_system(discipline: Discipline) -> str:
    if discipline == Discipline.PHYSICS:
        role = "你是一位严谨的**大学物理实验**教学助手，从实验指导书/教材/讲义中提取物理实验信息。"
        extra = (
            "物理实验特别关注：测量方法、仪器读数、控制变量、重复测量与误差分析。"
            f" suggested_template_name 只能从：{_PHYSICS_TEMPLATE_OPTIONS}。"
            " reagents_instruments 填写实验器材与材料（如游标卡尺、光电门、电源、透镜等）。"
        )
    elif discipline == Discipline.BIOLOGY:
        role = "你是一位严谨的**大学生物实验**教学助手，从实验指导书/教材/讲义中提取生物实验信息。"
        extra = (
            "生物实验特别关注：样本处理、培养/反应条件、无菌操作、观察记录与生物安全。"
            f" suggested_template_name 只能从：{_BIOLOGY_TEMPLATE_OPTIONS}。"
            " reagents_instruments 填写培养基、试剂、菌种/样本与仪器（如显微镜、培养箱、离心机等）。"
        )
    else:
        role = "你是一位严谨的**化学实验**教学助手，从文献/教材/讲义中提取化学实验信息。"
        extra = (
            f" suggested_template_name 只能从：{_CHEMISTRY_TEMPLATE_OPTIONS}。"
            " reagents_instruments 填写试剂与仪器清单。"
        )
    return f"{role}\n{extra}\n{_COMMON_RULES}\n{_JSON_SCHEMA}"


def build_literature_user_prompt(
    literature_text: str,
    handout_text: Optional[str] = None,
    discipline: Discipline = Discipline.CHEMISTRY,
) -> str:
    subject = subject_label(discipline)
    parts = []
    if handout_text:
        parts.append("=== 教师讲义（优先参考）===\n")
        parts.append(handout_text)
        parts.append("\n\n=== 参考文献/实验指导 ===\n")
    parts.append(literature_text)
    parts.append(f"\n\n请根据以上内容提取{subject}信息，输出 JSON。")
    return "".join(parts)


def get_image_ocr_refine_system(discipline: Discipline) -> str:
    subject = subject_label(discipline)
    return (
        f"你是严谨的{subject}教学助手。用户上传了实验相关照片（讲义、指导书、板书、"
        "仪器标签或数据记录等），以下为 OCR 识别文字，可能有错字、断行或乱序。"
        "请整理为连贯、便于提取实验步骤的纯文本。"
        "规则：只保留图片中实际出现的含义，不要编造用量、现象或步骤；"
        "若几乎无有效文字，只输出一行：【图片中未识别到足够文字，请拍摄更清晰的照片】"
        "不要输出 JSON 或 markdown 代码块。"
    )


def build_image_ocr_refine_user_prompt(ocr_text: str, filename: str) -> str:
    return f"图片文件名：{filename}\n\n=== OCR 原文 ===\n{ocr_text}\n\n请整理为连贯正文。"
