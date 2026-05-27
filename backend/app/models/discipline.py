import enum


class Discipline(str, enum.Enum):
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    BIOLOGY = "biology"


def subject_label(discipline: Discipline) -> str:
    return {
        Discipline.CHEMISTRY: "化学实验",
        Discipline.PHYSICS: "物理实验",
        Discipline.BIOLOGY: "生物实验",
    }[discipline]


def materials_label(discipline: Discipline) -> str:
    return {
        Discipline.CHEMISTRY: "试剂与仪器",
        Discipline.PHYSICS: "器材与材料",
        Discipline.BIOLOGY: "材料、试剂与仪器",
    }[discipline]
