"""Schemas Pydantic del recurso `reports`."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ReportStatus = Literal["open", "in_progress", "closed"]


class ReportBase(BaseModel):
    user_id: int
    title: str = Field(min_length=1, max_length=120)
    body: str = Field(default="")


class ReportCreate(ReportBase):
    """Cuerpo de entrada para crear un reporte."""


class ReportStatusUpdate(BaseModel):
    """Cuerpo de entrada para cambiar el estado de un reporte."""

    status: ReportStatus


class Report(ReportBase):
    """Reporte tal como lo devuelve la API."""

    id: int
    created_at: datetime
    status: ReportStatus = "open"
