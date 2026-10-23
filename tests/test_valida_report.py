"""Tests de validaciones de `reports`: usuario existente y cambios de estado simultáneos."""
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from reports import service as reports_service


def _payload(user_id: int = 1, title: str = "Incidencia", body: str = "algo pasó") -> dict:
    return {"user_id": user_id, "title": title, "body": body}


def test_create_report_usuario_existente_devuelve_201(client: TestClient) -> None:
    response = client.post("/reports", json=_payload(user_id=1))

    assert response.status_code == 201
    assert response.json()["user_id"] == 1


def test_create_report_usuario_inexistente_devuelve_404(client: TestClient) -> None:
    response = client.post("/reports", json=_payload(user_id=999))

    assert response.status_code == 404
    assert client.get("/reports").json() == []


def test_create_report_user_id_cero_devuelve_404(client: TestClient) -> None:
    response = client.post("/reports", json=_payload(user_id=0))

    assert response.status_code == 404


def test_update_status_simultaneo_solo_uno_gana(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Dos PATCH open → in_progress a la vez: uno responde 200 y el otro 409."""
    report_id = client.post("/reports", json=_payload()).json()["id"]

    # Ambas peticiones leen el reporte (en `open`) antes de que cualquiera escriba.
    barrera = threading.Barrier(2, timeout=5)
    get_report_original = reports_service.get_report

    def get_report_sincronizado(rid: int):
        report = get_report_original(rid)
        barrera.wait()
        return report

    monkeypatch.setattr(reports_service, "get_report", get_report_sincronizado)

    def patch(_: int) -> int:
        response = client.patch(f"/reports/{report_id}/status", json={"status": "in_progress"})
        return response.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        codigos = sorted(pool.map(patch, range(2)))

    monkeypatch.undo()  # el GET de abajo no debe esperar en la barrera
    assert codigos == [200, 409]
    assert client.get(f"/reports/{report_id}").json()["status"] == "in_progress"
