"""Lógica de negocio del recurso `reports`."""
from typing import get_args

from core import errors
from reports import repository
from reports.schemas import Report, ReportCreate, ReportStatus, ReportStatusUpdate

MAX_BODY_LEN = 500

VALID_STATUSES = set(get_args(ReportStatus))

# Transiciones permitidas: open → in_progress → closed.
ALLOWED_TRANSITIONS = {
    "open": "in_progress",
    "in_progress": "closed",
}


def create_report(data: ReportCreate) -> Report:
    if len(data.body) > MAX_BODY_LEN:
        raise errors.invalid_request(
            f"el cuerpo no puede exceder {MAX_BODY_LEN} caracteres"
        )
    return repository.add(user_id=data.user_id, title=data.title, body=data.body)


def get_report(report_id: int) -> Report:
    report = repository.get(report_id)
    if report is None:
        raise errors.not_found("reporte", report_id)
    return report


def add_status(report_id: int, data: ReportStatusUpdate) -> Report:
    report = get_report(report_id)  # 404 si no existe
    if data.status not in VALID_STATUSES:
        raise errors.not_found("estado", data.status)
    if ALLOWED_TRANSITIONS.get(report.status) != data.status:
        raise errors.conflict(
            f"transición de estado inválida: {report.status} → {data.status}"
        )
    return repository.update_status(report_id, data.status)


def list_reports(user_id: int | None = None) -> list[Report]:
    reports = repository.list_all()
    if user_id is not None:
        reports = [r for r in reports if r.user_id == user_id]
    return reports
