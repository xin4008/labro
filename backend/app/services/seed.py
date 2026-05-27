from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.template import ExperimentTemplate

DEFAULT_TEMPLATES: list[dict] = [
    {
        "name": "有机合成实验",
        "fields": [
            {"label": "投料量", "type": "text", "unit": "g/mL"},
            {"label": "反应温度", "type": "number", "unit": "°C"},
            {"label": "反应时间", "type": "text", "unit": "h/min"},
            {"label": "TLC监测结果", "type": "image"},
            {"label": "Rf值", "type": "number"},
            {"label": "后处理步骤", "type": "text"},
            {"label": "产物质量", "type": "number", "unit": "g"},
            {"label": "产率", "type": "number", "unit": "%"},
            {"label": "现象描述", "type": "text"},
        ],
    },
    {
        "name": "无机合成实验",
        "fields": [
            {"label": "投料量", "type": "text", "unit": "g/mL"},
            {"label": "反应条件", "type": "text"},
            {"label": "沉淀/结晶观察", "type": "text"},
            {"label": "产物外观", "type": "image"},
            {"label": "产物质量", "type": "number", "unit": "g"},
            {"label": "产率", "type": "number", "unit": "%"},
        ],
    },
    {
        "name": "分析化学实验",
        "fields": [
            {"label": "滴定体积", "type": "number", "unit": "mL"},
            {"label": "标准溶液浓度", "type": "number", "unit": "mol/L"},
            {"label": "待测溶液浓度", "type": "number", "unit": "mol/L"},
            {"label": "平行实验数据", "type": "text"},
            {"label": "相对标准偏差", "type": "number", "unit": "%"},
        ],
    },
    {
        "name": "物理化学实验",
        "fields": [
            {"label": "温度序列", "type": "text"},
            {"label": "吸光度/电导率", "type": "number"},
            {"label": "时间记录", "type": "text"},
            {"label": "数据处理", "type": "text"},
            {"label": "图表", "type": "image"},
        ],
    },
]


def seed_experiment_templates(db: Session) -> None:
    existing = {row.name for row in db.scalars(select(ExperimentTemplate)).all()}
    for item in DEFAULT_TEMPLATES:
        if item["name"] in existing:
            continue
        db.add(ExperimentTemplate(name=item["name"], fields=item["fields"]))
    db.commit()
