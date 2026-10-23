# m2-api-base

API REST de usuarios usada como base en el **Módulo 2 · Clase 1 — Generación de código con IA**.

Es un proyecto pequeño pero completo: tiene convenciones, capas separadas, catálogo
de errores y una suite de tests que pasa. Le falta **una** feature — la que vas a
construir en el laboratorio.

## Requisitos

- Python 3.10 o superior
- (Recomendado) Claude Code instalado

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
uvicorn main:app --reload          # http://127.0.0.1:8000  ·  Swagger en /docs
```

Endpoints actuales:

| Método | Ruta              | Descripción                     |
|--------|-------------------|---------------------------------|
| GET    | `/health`         | Estado del servicio             |
| GET    | `/users`          | Lista de usuarios               |
| GET    | `/users/{id}`     | Un usuario por id (404 si no existe) |
| POST   | `/users`          | Crea un usuario (409 si el email ya existe) |
| GET    | `/reports`        | Lista de reportes; `?user_id=` filtra por usuario |
| GET    | `/reports/{id}`   | Un reporte por id (404 si no existe) |
| POST   | `/reports`        | Crea un reporte en estado `open` (404 si el usuario no existe, 422 si el body supera 500 caracteres) |
| PATCH  | `/reports/{id}/status` | Cambia el estado del reporte (ver abajo) |
| GET    | `/reports/export` | Exporta los reportes a CSV en el servidor; requiere la cabecera `X-Export-Token` (401 si falta o es inválida, 422 si `fmt` no es `csv`) |

### Estados de un reporte

Todo reporte nace en `open` y avanza un paso a la vez:

```
open → in_progress → closed
```

```bash
curl -X PATCH http://127.0.0.1:8000/reports/1/status \
     -H "Content-Type: application/json" \
     -d '{"status": "in_progress"}'
```

- **200** con el reporte actualizado
- **404** si el reporte no existe
- **409** si la transición no está permitida (saltar un paso, retroceder, salir de `closed`
  o repetir el estado actual), o si otro cambio simultáneo ganó
- **422** si el estado no es `open`, `in_progress` ni `closed`

## Configuración

La exportación (`GET /reports/export`) usa dos variables de entorno:

| Variable           | Uso |
|--------------------|-----|
| `EXPORT_API_TOKEN` | Token que se espera en `X-Export-Token`. Si no está definida, toda exportación responde 401. |
| `EXPORT_DIR`       | Directorio donde se escribe el archivo (por defecto `exports/`). |

## Tests y calidad

```bash
pytest                                       # correr la suite
pytest --cov=. --cov-report=term-missing     # con cobertura
ruff check .                                 # linter
```

Los tests de `reports` están en `tests/test_reports.py`, `tests/test_valida_report.py`
(validaciones y concurrencia) y `tests/test_export.py`.

## Tarea del laboratorio

Añadir `GET /users/search?email=<email>`:

- **200** con el usuario si existe
- **422** si el formato del email es inválido
- **404** si no hay ningún usuario con ese email
- con su test en `tests/test_users.py`, siguiendo el estilo del archivo

Lee `CLAUDE.md` antes de empezar: ahí están las convenciones que tu código debe respetar.
