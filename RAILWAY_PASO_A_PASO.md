# Railway Paso A Paso

Este es el camino mas simple para dejar `Enmarcados PF` funcionando en nube con 2 computadoras.

## 1. Crear cuenta y proyecto

1. Entra a Railway.
2. Crea un proyecto nuevo.
3. Elige `Deploy from GitHub repo` o sube este proyecto a un repositorio y conectalo.

## 2. Agregar PostgreSQL

1. Dentro del proyecto, pulsa `+ New`.
2. Agrega `PostgreSQL`.
3. Railway te dara automaticamente variables como `DATABASE_URL`.

## 3. Configurar el backend web

En el servicio web, en `Variables`, agrega esto:

```env
APP_NAME=Enmarcados PF API
APP_ENV=production
APP_DEBUG=false
CORS_ORIGINS=*
```

`DATABASE_URL` normalmente ya aparece cuando conectas el servicio PostgreSQL al servicio web.

## 4. Archivos ya listos

Este proyecto ya tiene:

- [railway.json](/Users/elianpaniagua/Documents/Facturacion%20PF/railway.json)
- [backend_requirements.txt](/Users/elianpaniagua/Documents/Facturacion%20PF/backend_requirements.txt)
- [backend/main.py](/Users/elianpaniagua/Documents/Facturacion%20PF/backend/main.py)

El arranque queda asi:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## 5. Hacer publica la API

Cuando el deploy termine:

1. Entra al servicio web.
2. Ve a `Settings` > `Networking`.
3. Pulsa `Generate Domain`.

Esa sera la URL publica del backend.

## 6. Importar tus datos actuales

Cuando ya tengas la `DATABASE_URL` real de Railway, crea tu archivo `.env.backend` local copiando:

- [`.env.backend.railway.example`](/Users/elianpaniagua/Documents/Facturacion%20PF/.env.backend.railway.example)

y luego ejecuta:

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
./run_backend_db_setup.sh
```

Eso crea tablas e importa lo que hoy tienes en `facturacion.db`.

## 7. Conectar las 2 computadoras

En cada computadora crea `.env.cloud` con la URL publica:

```env
DATA_MODE=cloud
API_BASE_URL=https://tu-app.up.railway.app
```

Abres la app normal en las dos computadoras y ambas trabajaran sobre la misma base.

## 8. Prueba minima recomendada

1. Crear un cliente en una computadora.
2. Abrir `Clientes` en la otra.
3. Crear una factura en una.
4. Abrir `Historial` en la otra.
5. Registrar un abono y confirmar que se refleja en ambas.
