# Despliegue en Nube

Este proyecto ya quedo preparado para subir el backend y luego conectar la app de escritorio.

## Opcion 1: Railway

Ya te deje una guia dedicada:

- [RAILWAY_PASO_A_PASO.md](/Users/elianpaniagua/Documents/Facturacion%20PF/RAILWAY_PASO_A_PASO.md)

Y tambien los archivos listos:

- [railway.json](/Users/elianpaniagua/Documents/Facturacion%20PF/railway.json)
- [`.env.backend.railway.example`](/Users/elianpaniagua/Documents/Facturacion%20PF/.env.backend.railway.example)

Resumen rapido:

1. Crea un proyecto nuevo en Railway.
2. Sube esta carpeta o conectala a un repositorio.
3. Agrega una base de datos PostgreSQL en Railway.
4. En las variables del servicio web configura:

```env
APP_NAME=Enmarcados PF API
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql+psycopg://...
CORS_ORIGINS=*
```

5. Como comando de inicio usa:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

6. Como comando de instalacion usa:

```bash
pip install -r backend_requirements.txt
```

## Opcion 2: Render

Ya tienes un archivo [render.yaml](/Users/elianpaniagua/Documents/Facturacion%20PF/render.yaml) listo.

Solo necesitas:

1. Crear el servicio web en Render.
2. Crear la base PostgreSQL en Render o usar una externa.
3. Completar `DATABASE_URL`.

## Despues del despliegue

Cuando tengas la URL publica del backend, crea el archivo `.env.cloud` con algo asi:

```env
DATA_MODE=cloud
API_BASE_URL=https://tu-backend-publico.onrender.com
```

o:

```env
DATA_MODE=cloud
API_BASE_URL=https://tu-backend-publico.up.railway.app
```

## Importar tus datos actuales

Primero configura `.env.backend` con la `DATABASE_URL` real y luego ejecuta:

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
./run_backend_db_setup.sh
```

Eso crea las tablas e importa los datos de tu `facturacion.db` actual.

## Probar desde las 2 computadoras

1. En cada computadora usa el mismo `.env.cloud`.
2. Abre la app normal.
3. Todo lo nuevo debe leerse y guardarse contra la misma base en nube.
