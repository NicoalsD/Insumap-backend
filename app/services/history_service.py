"""History pagination over the doubly linked list (E5) and exports (R17-R19, R26)."""

import csv
import io
import uuid
from collections.abc import Iterator
from datetime import date
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.errors import bad_request, conflict
from app.db.models import Patient
from app.domain.models import MACRO_LABELS, SIDE_LABELS, InjectionStatus, InjectionView
from app.services import state_service
from app.services.injection_service import view_out

STATUS_LABELS = {InjectionStatus.REGISTERED: "Registrada", InjectionStatus.UNDONE: "Deshecha"}
HEADERS = ["Fecha", "Hora", "Microzona", "Zona macro", "Lado", "Estado"]


def _matches(v: InjectionView, macro: str | None, date_from: date | None, date_to: date | None, tz: ZoneInfo) -> bool:
    day = v.applied_at.astimezone(tz).date()
    return (
        (macro is None or v.macro == macro)
        and (date_from is None or day >= date_from)
        and (date_to is None or day <= date_to)
    )


def page(
    db: Session,
    patient: Patient,
    cursor: str | None,
    limit: int,
    order: str,
    macro: str | None,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    tz = ZoneInfo(patient.timezone)
    with state_service.lock:
        state = state_service.get_state(db, patient)
        after = None
        if cursor:
            if not state.history_nodes.contains(cursor):
                raise bad_request("INVALID_CURSOR", "El cursor de paginación no es válido.")
            after = state.history_nodes.get(cursor)
        items: list[InjectionView] = []
        has_more = False
        # Head of the list = most recent registration, so "desc" walks forward.
        for node in state.history.iter_from(after, forward=(order == "desc")):
            v = node.data()
            if not _matches(v, macro, date_from, date_to, tz):
                continue
            if len(items) == limit:
                has_more = True
                break
            items.append(v)
        return {"items": [view_out(v) for v in items], "next_cursor": items[-1].id if has_more else None}


def _chronological(
    db: Session, patient: Patient, date_from: date | None, date_to: date | None
) -> Iterator[InjectionView]:
    tz = ZoneInfo(patient.timezone)
    with state_service.lock:
        state = state_service.get_state(db, patient)
        rows = [v for v in state.history.iter_backward() if _matches(v, None, date_from, date_to, tz)]
    return iter(rows)


def _rows(views: Iterator[InjectionView], tz: ZoneInfo) -> list[list[str]]:
    out = []
    for v in views:
        local = v.applied_at.astimezone(tz)
        out.append(
            [
                local.strftime("%Y-%m-%d"),
                local.strftime("%H:%M"),
                v.microzone_id,
                MACRO_LABELS[v.macro],
                SIDE_LABELS[v.side],
                STATUS_LABELS[v.status],
            ]
        )
    return out


def export(
    db: Session, patient: Patient, fmt: str, date_from: date | None, date_to: date | None
) -> tuple[bytes, str, str]:
    """Return (content, media_type, filename)."""
    tz = ZoneInfo(patient.timezone)
    rows = _rows(_chronological(db, patient, date_from, date_to), tz)
    if not rows:
        raise conflict("EMPTY_HISTORY", "No hay aplicaciones registradas para exportar.")
    name = f"insumap-historial-{uuid.uuid4().hex[:6]}"
    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(HEADERS)
        writer.writerows(rows)
        return buf.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8", f"{name}.csv"
    if fmt == "xlsx":
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        assert ws is not None
        ws.title = "Historial"
        ws.append(HEADERS)
        for r in rows:
            ws.append(r)
        out = io.BytesIO()
        wb.save(out)
        return (
            out.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            f"{name}.xlsx",
        )
    return _pdf(patient, rows), "application/pdf", f"{name}.pdf"


def _pdf(patient: Patient, rows: list[list[str]]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, title="Historial de aplicaciones - Insumap")
    styles = getSampleStyleSheet()
    table = Table([HEADERS, *rows], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16A34A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    name = patient.user.name if patient.user else ""
    doc.build(
        [
            Paragraph("Historial de aplicaciones de insulina", styles["Title"]),
            Paragraph(f"Paciente: {name}", styles["Normal"]),
            Paragraph("Generado por Insumap. No reemplaza la valoración médica.", styles["Italic"]),
            Spacer(1, 12),
            table,
        ]
    )
    return out.getvalue()
