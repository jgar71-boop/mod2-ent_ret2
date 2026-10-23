"""Almacén en memoria del recurso `reports`.

Sustituye a una base de datos real para que el proyecto sea ejecutable sin
infraestructura. No decide errores de dominio: devuelve ``None`` cuando algo no
está, y `service.py` decide qué responder. Las escrituras se protegen con un lock
para que sean seguras frente a peticiones concurrentes.
"""
import threading
import time
from datetime import datetime, timezone

from reports.schemas import Report

_reports: dict[int, Report] = {}
_next_id: int = 1
_lock = threading.Lock()


def add(*, user_id: int, title: str, body: str) -> Report:
    """Guarda un reporte nuevo y le asigna el siguiente id.

    El reporte nace en el estado por defecto del esquema (``open``).

    Args:
        user_id: Id del usuario autor. No se valida aquí.
        title: Título del reporte.
        body: Cuerpo del reporte.

    Returns:
        El reporte guardado, con ``id`` y ``created_at`` (UTC) asignados.
    """
    global _next_id
    # La asignación de id es una sección crítica: leer el contador, usarlo y
    # actualizarlo debe ocurrir de forma atómica frente a llamadas concurrentes.
    with _lock:
        new_id = _next_id
        time.sleep(0.001)  # simula el trabajo real entre leer y escribir
        report = Report(
            id=new_id,
            user_id=user_id,
            title=title,
            body=body,
            created_at=datetime.now(timezone.utc),
        )
        _reports[new_id] = report
        _next_id = new_id + 1
    return report


def get(report_id: int) -> Report | None:
    """Devuelve el reporte con ese id, o ``None`` si no existe."""
    return _reports.get(report_id)


def update_status(report_id: int, *, expected: str, new: str) -> Report | None:
    """Cambia el estado solo si el actual sigue siendo ``expected`` (compare-and-set).

    La lectura y la escritura ocurren dentro del mismo lock, así que dos cambios
    simultáneos no pueden aplicarse a la vez sobre el mismo estado de partida.

    Args:
        report_id: Id de un reporte que debe existir (lo verifica el servicio).
        expected: Estado que el llamador leyó y validó.
        new: Estado destino.

    Returns:
        El reporte actualizado, o ``None`` si el estado ya no era ``expected``
        porque otro cambio ganó entre la lectura y la escritura.
    """
    with _lock:
        current = _reports[report_id]
        if current.status != expected:
            return None
        report = current.model_copy(update={"status": new})
        _reports[report_id] = report
    return report


def list_all() -> list[Report]:
    """Devuelve todos los reportes en orden de creación."""
    return list(_reports.values())


def reset() -> None:
    """Vacía el almacén y reinicia el contador de ids. Uso exclusivo de los tests."""
    global _next_id
    _reports.clear()
    _next_id = 1
