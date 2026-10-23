"""Lógica de negocio del recurso `reports`.

Las rutas no acceden al repositorio directamente: pasan por aquí. Esta capa es la
única que conoce `repository.py` y la que decide cuándo algo es un error de
dominio (usando `core.errors`).
"""
from core import errors
from reports import repository
from reports.schemas import Report, ReportCreate, ReportStatusUpdate
from users import service as users_service

MAX_BODY_LEN = 500

# Transiciones permitidas: open → in_progress → closed.
ALLOWED_TRANSITIONS = {
    "open": "in_progress",
    "in_progress": "closed",
}


def create_report(data: ReportCreate) -> Report:
    """Crea un reporte nuevo en estado ``open``.

    Args:
        data: Datos de entrada del reporte.

    Returns:
        El reporte creado, con ``id`` y ``created_at`` asignados.

    Raises:
        HTTPException: 404 (``not_found``) si ``data.user_id`` no corresponde a
            ningún usuario; 422 (``invalid_request``) si el cuerpo supera
            ``MAX_BODY_LEN`` caracteres.
    """
    users_service.get_user(data.user_id)  # 404 si el usuario no existe
    if len(data.body) > MAX_BODY_LEN:
        raise errors.invalid_request(
            f"el cuerpo no puede exceder {MAX_BODY_LEN} caracteres"
        )
    return repository.add(user_id=data.user_id, title=data.title, body=data.body)


def get_report(report_id: int) -> Report:
    """Devuelve un reporte por su id.

    Args:
        report_id: Id del reporte.

    Returns:
        El reporte encontrado.

    Raises:
        HTTPException: 404 (``not_found``) si no existe.
    """
    report = repository.get(report_id)
    if report is None:
        raise errors.not_found("reporte", report_id)
    return report


def update_report_status(report_id: int, data: ReportStatusUpdate) -> Report:
    """Avanza el estado de un reporte siguiendo ``ALLOWED_TRANSITIONS``.

    El cambio se guarda con compare-and-set: si otro cambio simultáneo modificó el
    estado entre la lectura y la escritura, este no se aplica.

    Args:
        report_id: Id del reporte.
        data: Estado destino.

    Returns:
        El reporte con el estado actualizado.

    Raises:
        HTTPException: 404 (``not_found``) si el reporte no existe; 409
            (``conflict``) si la transición no está permitida o si otro cambio
            simultáneo ganó.
    """
    report = get_report(report_id)  # 404 si no existe
    if ALLOWED_TRANSITIONS.get(report.status) != data.status:
        raise errors.conflict(
            f"transición de estado inválida: {report.status} → {data.status}"
        )
    updated = repository.update_status(report_id, expected=report.status, new=data.status)
    if updated is None:  # otro cambio ganó entre la lectura y la escritura
        raise errors.conflict("el estado del reporte cambió; vuelve a intentarlo")
    return updated


def list_reports(user_id: int | None = None) -> list[Report]:
    """Lista los reportes, opcionalmente filtrados por usuario.

    Args:
        user_id: Si se indica, solo se devuelven los reportes de ese usuario. No se
            valida que el usuario exista: un id desconocido devuelve una lista vacía.

    Returns:
        Los reportes en orden de creación.
    """
    reports = repository.list_all()
    if user_id is not None:
        reports = [r for r in reports if r.user_id == user_id]
    return reports
