from pathlib import Path

from app.ai.base import AIProvider
from app.models.discipline import Discipline
from app.models.experiment import DocumentType, Experiment
from app.services.document_parser import extract_text_from_image, truncate_text

MIN_OCR_LEN_FOR_REFINE = 15


async def ensure_image_documents_ready(
    ai: AIProvider,
    experiment: Experiment,
    discipline: Discipline,
) -> None:
    """上传的图片在解析前经 OCR + DeepSeek 整理，便于生成实验步骤。"""
    for doc in experiment.documents:
        if doc.doc_type != DocumentType.IMAGE:
            continue
        path = Path(doc.stored_path) if doc.stored_path else None
        if not path or not path.exists():
            continue

        ocr = (doc.parsed_text or "").strip()
        if len(ocr) < MIN_OCR_LEN_FOR_REFINE:
            ocr = extract_text_from_image(path).strip()

        if len(ocr) < MIN_OCR_LEN_FOR_REFINE:
            doc.parsed_text = (
                "【图片中未识别到足够文字】请上传更清晰的实验讲义、指导书页面或板书照片。"
            )
            continue

        try:
            refined = await ai.refine_image_ocr_text(ocr, discipline, doc.filename)
            doc.parsed_text = truncate_text(refined.strip() or ocr)
        except RuntimeError:
            doc.parsed_text = truncate_text(ocr)
