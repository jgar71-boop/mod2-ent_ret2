# API de usuarios — guía del proyecto

API REST de ejemplo (FastAPI + Pydantic v2). Almacén en memoria, sin base de datos:
el proyecto corre sin infraestructura.

## Estructura

- `main.py` — crea la app y monta los routers.
- `users/` — recurso de ejemplo. Cada recurso sigue el mismo patrón:
  - `routes.py` — rutas HTTP. Sin lógica de negocio: delega en `service.py`.
  - `service.py` — lógica de negocio. Única capa que habla con `repository.py`.
  - `schemas.py` — modelos Pydantic de entrada (`*Create`) y salida.
  - `repository.py` — acceso a datos (aquí, un `dict` en memoria).
- `core/errors.py` — catálogo de errores. Toda respuesta de error sale de aquí.
- `tests/` — un archivo por recurso: `test_<recurso>.py`.
  Excepción: `tests/test_valida_report.py` reúne los tests de validaciones de `reports`
  (usuario existente al crear, cambios de estado simultáneos); el resto de los tests de
  `reports` sigue en `tests/test_reports.py`.

## Convenciones

- Las rutas declaran `response_model=` y devuelven modelos Pydantic, nunca `dict` crudos.
- Los errores se levantan con las funciones de `core/errors.py`
  (`not_found`, `invalid_request`, `already_exists`, `conflict`, `unauthorized`),
  no con `HTTPException` a mano. `already_exists` es solo para duplicados al crear;
  un 409 porque la operación choca con el estado actual del recurso usa `conflict`.
- Los valores cerrados (p. ej. estados) se definen una vez en `schemas.py` como `Literal`
  y se usan en los modelos de entrada y salida. Un valor fuera de la lista lo rechaza
  Pydantic (422); el servicio no lo vuelve a validar.
- Los campos que decide el servidor (`id`, `created_at`, el estado inicial) van solo en
  el modelo de salida, nunca en `*Create`.
- Las transiciones de estado permitidas se declaran como tabla en `service.py`
  (p. ej. `ALLOWED_TRANSITIONS`); una transición inválida responde 409 (`conflict`).
  Orden de chequeo en el servicio: existe el recurso (404, reutilizando `get_<recurso>`)
  → transición válida (409) → persistir.
- La ruta delega en `service.py`; la lógica y las decisiones de error viven ahí.
- Identificadores en inglés y `snake_case`, sin abreviaturas. Mensajes de error en español.
- Cada endpoint nuevo lleva su test en el archivo del recurso, con al menos un caso
  feliz y un caso de error.
- Rutas específicas antes que rutas con parámetro: `/users/search` debe declararse
  **antes** de `/users/{user_id}`.

## Cómo ejecutar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload          # API en http://127.0.0.1:8000  ·  /docs para el Swagger
pytest                             # tests
pytest --cov=. --cov-report=term-missing   # cobertura
ruff check .                       # linter
```

## Fuera de límites

- `migrations/` y `legacy/` — no modificar.
