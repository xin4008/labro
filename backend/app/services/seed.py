from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.discipline import Discipline
from app.models.template import ExperimentTemplate

CHEMISTRY_TEMPLATES: list[dict] = [
    {
        "name": "有机合成实验",
        "discipline": Discipline.CHEMISTRY,
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
        "discipline": Discipline.CHEMISTRY,
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
        "discipline": Discipline.CHEMISTRY,
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
        "discipline": Discipline.CHEMISTRY,
        "fields": [
            {"label": "温度序列", "type": "text"},
            {"label": "吸光度/电导率", "type": "number"},
            {"label": "时间记录", "type": "text"},
            {"label": "数据处理", "type": "text"},
            {"label": "图表", "type": "image"},
        ],
    },
]

PHYSICS_TEMPLATES: list[dict] = [
    {
        "name": "力学实验",
        "discipline": Discipline.PHYSICS,
        "fields": [
            {"label": "测量值记录", "type": "text"},
            {"label": "质量", "type": "number", "unit": "kg/g"},
            {"label": "长度/位移", "type": "number", "unit": "m/cm"},
            {"label": "时间", "type": "number", "unit": "s"},
            {"label": "速度/加速度", "type": "number"},
            {"label": "重复测量数据", "type": "text"},
            {"label": "不确定度/相对误差", "type": "number", "unit": "%"},
            {"label": "现象描述", "type": "text"},
            {"label": "图表", "type": "image"},
        ],
    },
    {
        "name": "电磁学实验",
        "discipline": Discipline.PHYSICS,
        "fields": [
            {"label": "电压", "type": "number", "unit": "V"},
            {"label": "电流", "type": "number", "unit": "A"},
            {"label": "电阻/电容", "type": "number"},
            {"label": "磁感应强度", "type": "number", "unit": "T/mT"},
            {"label": "示波器读数", "type": "text"},
            {"label": "电路连接记录", "type": "image"},
            {"label": "现象描述", "type": "text"},
        ],
    },
    {
        "name": "光学实验",
        "discipline": Discipline.PHYSICS,
        "fields": [
            {"label": "波长", "type": "number", "unit": "nm"},
            {"label": "折射率/干涉条纹", "type": "text"},
            {"label": "光强/偏振角", "type": "number"},
            {"label": "几何参数", "type": "text", "unit": "cm"},
            {"label": "光路/条纹照片", "type": "image"},
            {"label": "现象描述", "type": "text"},
        ],
    },
    {
        "name": "热学实验",
        "discipline": Discipline.PHYSICS,
        "fields": [
            {"label": "温度", "type": "number", "unit": "°C"},
            {"label": "加热/冷却时间", "type": "text", "unit": "min/s"},
            {"label": "比热容/热量", "type": "number"},
            {"label": "物态变化观察", "type": "text"},
            {"label": "温度-时间数据", "type": "text"},
            {"label": "图表", "type": "image"},
        ],
    },
]

BIOLOGY_TEMPLATES: list[dict] = [
    {
        "name": "细胞生物学实验",
        "discipline": Discipline.BIOLOGY,
        "fields": [
            {"label": "样本来源/处理", "type": "text"},
            {"label": "显微镜倍数", "type": "text"},
            {"label": "细胞密度/计数", "type": "text"},
            {"label": "染色方法", "type": "text"},
            {"label": "显微观察记录", "type": "text"},
            {"label": "显微照片", "type": "image"},
            {"label": "现象描述", "type": "text"},
        ],
    },
    {
        "name": "微生物实验",
        "discipline": Discipline.BIOLOGY,
        "fields": [
            {"label": "培养基类型", "type": "text"},
            {"label": "接种量", "type": "text"},
            {"label": "培养温度", "type": "number", "unit": "°C"},
            {"label": "培养时间", "type": "text", "unit": "h"},
            {"label": "菌落计数", "type": "number"},
            {"label": "平板/菌落照片", "type": "image"},
            {"label": "无菌操作记录", "type": "text"},
        ],
    },
    {
        "name": "生物化学实验",
        "discipline": Discipline.BIOLOGY,
        "fields": [
            {"label": "样品浓度", "type": "number"},
            {"label": "吸光度", "type": "number"},
            {"label": "酶活力/反应速率", "type": "number"},
            {"label": "标准曲线数据", "type": "text"},
            {"label": "平行测定", "type": "text"},
            {"label": "图表", "type": "image"},
        ],
    },
    {
        "name": "分子生物学实验",
        "discipline": Discipline.BIOLOGY,
        "fields": [
            {"label": "PCR/反应条件", "type": "text"},
            {"label": "电泳电压/时间", "type": "text"},
            {"label": "Marker 条带对照", "type": "text"},
            {"label": "目标条带位置", "type": "text"},
            {"label": "凝胶照片", "type": "image"},
            {"label": "现象描述", "type": "text"},
        ],
    },
]

DEFAULT_TEMPLATES = CHEMISTRY_TEMPLATES + PHYSICS_TEMPLATES + BIOLOGY_TEMPLATES


def seed_experiment_templates(db: Session) -> None:
    existing_by_name = {
        row.name: row for row in db.scalars(select(ExperimentTemplate)).all()
    }
    for item in DEFAULT_TEMPLATES:
        if item["name"] in existing_by_name:
            row = existing_by_name[item["name"]]
            if not getattr(row, "discipline", None):
                row.discipline = item["discipline"]
            continue
        db.add(
            ExperimentTemplate(
                name=item["name"],
                discipline=item["discipline"],
                fields=item["fields"],
            )
        )
    db.commit()
