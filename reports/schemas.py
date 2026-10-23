"""Schemas Pydantic del recurso `reports`.

Los modelos ``*Create`` / ``*Update`` describen lo que entra; ``Report`` describe lo
que sale. Los campos que decide el servidor (``id``, ``created_at``, el estado
inicial) solo existen en el modelo de salida.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReportStatus = Literal["open", "in_progress", "closed"]
"""Estados posibles de un reporte. Las transiciones válidas viven en `service.py`."""


class ReportBase(BaseModel):
    """Campos comunes a la entrada y la salida de un reporte."""

    user_id: int
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="")


class ReportCreate(ReportBase):
    """Cuerpo de entrada para crear un reporte."""


class ReportStatusUpdate(BaseModel):
    """Cuerpo de entrada para cambiar el estado de un reporte.

    Un valor que no sea uno de ``ReportStatus`` lo rechaza Pydantic con 422.
    """

    status: ReportStatus


class Report(ReportBase):
    """Reporte tal como lo devuelve la API."""

    id: int
    created_at: datetime
    status: ReportStatus = "open"
