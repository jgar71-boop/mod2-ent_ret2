"""Lógica de negocio del recurso `reports`."""
from core import errors
from reports import repository
from reports.schemas import Report, ReportCreate, ReportStatusUpdate

MAX_BODY_LEN = 500


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
    # TODO: buscar el reporte; si no existe → errors.not_found("reporte", report_id).
    # TODO: validar que data.status sea un estado permitido → errors.invalid_request(...).
    # TODO: validar la transición desde el estado actual (¿hay transiciones prohibidas?).
    # TODO: persistir el cambio vía repository (falta una función de actualización).
    raise NotImplementedError


def list_reports(user_id: int | None = None) -> list[Report]:
    reports = repository.list_all()
    if user_id is not None:
        reports = [r for r in reports if r.user_id == user_id]
    return reports
