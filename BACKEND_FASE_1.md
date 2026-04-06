# Fase 1: Base Profesional en Nube

Esta fase deja listo el backend para que luego las 2 computadoras trabajen contra la misma base.

## Lo que ya queda creado

- API en `FastAPI`
- Modelos `PostgreSQL` para:
  - `clientes`
  - `documentos`
  - `ordenes`
  - `orden_detalles`
  - `cobros`
- Importador desde tu `sqlite` actual a `PostgreSQL`
- Archivo de variables ejemplo `.env.backend.example`

## Archivos principales

- `backend/main.py`
- `backend/database.py`
- `backend/models.py`
- `backend/crud.py`
- `backend/import_sqlite.py`
- `backend_requirements.txt`

## Instalar dependencias del backend

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
.venv/bin/pip install -r backend_requirements.txt
```

## Crear tablas en PostgreSQL

Primero configura `DATABASE_URL` en un archivo `.env` o exportalo en terminal.

Luego ejecuta:

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
.venv/bin/uvicorn backend.main:app --reload
```

Y abre:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Importar tu base actual

Con PostgreSQL ya creado:

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/enmarcados_pf" \
.venv/bin/python backend/import_sqlite.py
```

## Siguiente fase

La fase 2 sería conectar `app.py` a esta API para que ambas computadoras vean lo mismo en tiempo real.
