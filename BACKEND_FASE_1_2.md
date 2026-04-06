# Fase 1.2: Conexion Real a PostgreSQL

Esta fase deja preparado el proyecto para conectar la API con una base PostgreSQL real y subir tu informacion actual.

## Archivos agregados

- `backend/test_connection.py`
- `backend/create_tables.py`
- `run_backend_db_setup.sh`
- `.env.backend.local.example`

## Flujo recomendado

### 1. Crear tu base PostgreSQL

Puedes usar:

- Supabase
- Railway
- Render
- PostgreSQL local

Cuando la tengas, copia la URL de conexion.

### 2. Crear tu archivo de entorno

Haz una copia de:

- `.env.backend.local.example`

y guardala como:

- `.env.backend`

Luego cambia `DATABASE_URL` por la URL real de tu base PostgreSQL.

## 3. Probar conexion

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
set -a
source .env.backend
set +a
.venv/bin/python backend/test_connection.py
```

Si sale `Conexion OK`, ya esta lista.

## 4. Crear tablas e importar tu sistema actual

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
./run_backend_db_setup.sh
```

Ese script hace:

1. prueba la conexion a PostgreSQL
2. crea las tablas
3. importa tu `facturacion.db` actual

## 5. Levantar la API

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
./run_backend.sh
```

Pruebas:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Notas importantes

- La app vieja todavia no usa este backend automaticamente.
- Esta fase deja lista la base profesional y el proceso de importacion.
- La siguiente fase conecta `app.py` con esta API para que las 2 computadoras vean lo mismo.

## Recomendacion para tu caso

Para 2 computadoras, las opciones mas practicas son:

- Railway
- Supabase

Ambas te dan una URL `DATABASE_URL` que puedes pegar directamente en `.env.backend`.
