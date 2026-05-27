from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.factory import get_ai_provider
from app.config import get_settings, resolve_path
from app.models.discipline import Discipline
from app.models.experiment import DocumentType, Experiment, ExperimentStatus, ExperimentStep
from app.models.template import ExperimentTemplate
from app.services.document_parser import (
    extract_text_from_docx,
    extract_text_from_image,
    extract_text_from_pdf,
    fetch_url_text,
    truncate_text,
)
from app.schemas.literature import DocumentRead
from app.services.image_analysis import ensure_image_documents_ready

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_BYTES = 15 * 1024 * 1024


def build_document_read(doc, experiment_id: str) -> DocumentRead:
    preview_url = None
    if doc.doc_type == DocumentType.IMAGE and doc.stored_path:
        preview_url = f"/api/files/{experiment_id}/documents/{Path(doc.stored_path).name}"
    return DocumentRead(
        id=doc.id,
        filename=doc.filename,
        doc_type=doc.doc_type.value,
        is_handout=doc.is_handout,
        source_url=doc.source_url,
        created_at=doc.created_at,
        has_text=bool(doc.parsed_text and doc.parsed_text.strip()),
        preview_url=preview_url,
    )


def _upload_dir(experiment_id: str) -> Path:
    settings = get_settings()
    base = resolve_path(settings.storage.uploads_dir) / experiment_id
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_uploaded_file(
    db: Session,
    experiment: Experiment,
    file: UploadFile,
    is_handout: bool,
) -> Experiment:
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS and ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"不支持的文件格式 {ext}，请上传 PDF、DOCX 或图片（JPG/PNG/WebP）"
        )

    content = file.file.read()
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("文件大小不能超过 15MB")

    if ext in ALLOWED_IMAGE_EXTENSIONS:
        doc_type = DocumentType.IMAGE
    elif ext == ".pdf":
        doc_type = DocumentType.PDF
    else:
        doc_type = DocumentType.DOCX

    dest_dir = _upload_dir(experiment.id)
    safe_name = f"{len(experiment.documents) + 1}_{Path(filename).name}"
    dest_path = dest_dir / safe_name
    dest_path.write_bytes(content)

    if doc_type == DocumentType.PDF:
        parsed = extract_text_from_pdf(dest_path)
    elif doc_type == DocumentType.DOCX:
        parsed = extract_text_from_docx(dest_path)
    else:
        try:
            parsed = extract_text_from_image(dest_path)
        except RuntimeError:
            raise
        except Exception as exc:
            raise ValueError(f"图片文字识别失败：{exc}") from exc

    from app.models.experiment import UploadedDocument

    doc = UploadedDocument(
        experiment_id=experiment.id,
        filename=filename,
        doc_type=doc_type,
        is_handout=is_handout,
        stored_path=str(dest_path),
        parsed_text=truncate_text(parsed),
    )
    db.add(doc)
    db.commit()
    db.refresh(experiment)
    return experiment


async def add_url_document(
    db: Session,
    experiment: Experiment,
    url: str,
    is_handout: bool,
) -> Experiment:
    text, hint = await fetch_url_text(url)
    if not text.strip():
        raise ValueError("无法从该网址提取有效文本")

    from app.models.experiment import UploadedDocument

    doc = UploadedDocument(
        experiment_id=experiment.id,
        filename=hint,
        doc_type=DocumentType.URL,
        is_handout=is_handout,
        source_url=url,
        parsed_text=truncate_text(text),
    )
    db.add(doc)
    db.commit()
    db.refresh(experiment)
    return experiment


def _collect_texts(experiment: Experiment) -> tuple[str, Optional[str]]:
    handout_parts: list[str] = []
    literature_parts: list[str] = []

    for doc in experiment.documents:
        if not doc.parsed_text:
            continue
        kind = "图片" if doc.doc_type == DocumentType.IMAGE else "文献"
        header = f"[{kind}: {doc.filename}]"
        if doc.source_url:
            header += f" ({doc.source_url})"
        block = f"{header}\n{doc.parsed_text}"
        if doc.is_handout:
            handout_parts.append(block)
        else:
            literature_parts.append(block)

    if not handout_parts and not literature_parts:
        if experiment.documents:
            raise ValueError(
                "已添加的资料中没有可读取的文本（可能网址抓取失败、PDF 为纯扫描图，或图片不清晰）。"
                "请删除无效项后，重新上传含文字层的 PDF/DOCX，或更清晰的实验讲义/板书照片。"
            )
        raise ValueError(
            "请先上传文献（PDF/DOCX）、实验相关图片，或添加可公开访问的网址"
        )

    literature = "\n\n".join(literature_parts) if literature_parts else "\n\n".join(handout_parts)
    handout = "\n\n".join(handout_parts) if handout_parts and literature_parts else None
    if handout_parts and not literature_parts:
        literature = "\n\n".join(handout_parts)
        handout = None

    return literature, handout


MIN_TEXT_LEN = 80


async def parse_and_generate_steps(db: Session, experiment: Experiment) -> Experiment:
    settings = get_settings()
    if not settings.ai.api_key.strip():
        raise RuntimeError("未配置 DeepSeek API 密钥，请检查 backend/config.yaml")

    ai = get_ai_provider(settings)
    discipline = experiment.discipline or Discipline.CHEMISTRY
    await ensure_image_documents_ready(ai, experiment, discipline)
    db.commit()
    db.refresh(experiment)

    literature, handout = _collect_texts(experiment)
    combined_len = len(literature) + (len(handout) if handout else 0)
    if combined_len < MIN_TEXT_LEN:
        raise ValueError(
            f"资料有效文字过少（约 {combined_len} 字），AI 无法解析。"
            "请确认已上传含文字层的 PDF、清晰的实验图片，或换用教师讲义 DOCX。"
        )

    try:
        parsed = await ai.parse_literature(literature, handout, discipline)
    except RuntimeError as exc:
        raise RuntimeError(str(exc)) from exc
    except Exception as exc:
        msg = str(exc).strip() or type(exc).__name__
        raise RuntimeError(f"DeepSeek 调用异常：{msg}") from exc

    for step in list(experiment.steps):
        db.delete(step)

    template = _resolve_template(
        db, experiment, parsed.get("suggested_template_name"), experiment.discipline
    )
    field_schema = template.fields if template else None
    if template and experiment.template_id is None:
        experiment.template_id = template.id

    experiment.purpose = parsed.get("purpose")
    experiment.reagents_instruments = parsed.get("reagents_instruments")
    experiment.global_safety_notes = parsed.get("global_safety_notes")
    experiment.parsed_metadata = {
        "suggested_template_name": parsed.get("suggested_template_name"),
        "ai_provider": settings.ai.provider,
    }
    experiment.status = ExperimentStatus.IN_PROGRESS
    experiment.current_step_index = 0

    steps_data = parsed.get("steps") or []
    if not steps_data:
        raise ValueError(
            "AI 未能从资料中识别出实验步骤。可能原因：内容与实验无关、文本过少，或图片/PDF 不清晰。"
            "请换用实验讲义 PDF 或更清晰的图片后重试。"
        )

    for index, item in enumerate(steps_data):
        instructions = item.get("instructions") or ""
        unclear = item.get("unclear_notes")
        if unclear and unclear not in instructions:
            instructions = f"{instructions}\n{unclear}".strip()

        db.add(
            ExperimentStep(
                experiment_id=experiment.id,
                order_index=index,
                title=item.get("title") or f"步骤 {index + 1}",
                instructions=instructions,
                expected_phenomenon=item.get("expected_phenomenon"),
                phenomenon_source=item.get("phenomenon_source"),
                safety_notes=item.get("safety_notes"),
                field_schema=field_schema,
            )
        )

    db.commit()
    db.refresh(experiment)
    return experiment


def _resolve_template(
    db: Session,
    experiment: Experiment,
    suggested_name: Optional[str],
    discipline: Discipline,
) -> Optional[ExperimentTemplate]:
    if experiment.template_id:
        return db.get(ExperimentTemplate, experiment.template_id)

    if not suggested_name:
        return None

    template = db.scalar(
        select(ExperimentTemplate).where(
            ExperimentTemplate.name == suggested_name,
            ExperimentTemplate.discipline == discipline,
        )
    )
    if template:
        return template

    for row in db.scalars(
        select(ExperimentTemplate).where(ExperimentTemplate.discipline == discipline)
    ).all():
        if suggested_name in row.name or row.name in suggested_name:
            return row
    return None


def delete_document(db: Session, experiment: Experiment, document_id: int) -> None:
    doc = next((d for d in experiment.documents if d.id == document_id), None)
    if not doc:
        raise ValueError("文档不存在")
    if doc.stored_path:
        path = Path(doc.stored_path)
        if path.exists():
            path.unlink()
    db.delete(doc)
    db.commit()
