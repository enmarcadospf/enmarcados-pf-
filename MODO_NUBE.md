# Activar Modo Nube

La app puede trabajar en `local` o conectarse al backend API en `cloud`.

## 1. Crear `.env.cloud`

Toma [`.env.cloud.example`](/Users/elianpaniagua/Documents/Facturacion%20PF/.env.cloud.example) y guardalo como `.env.cloud`.

## 2. Prueba local primero

Usa este contenido:

```env
DATA_MODE=cloud
API_BASE_URL=http://127.0.0.1:8000
```

## 3. Levantar el backend

```bash
cd "/Users/elianpaniagua/Documents/Facturacion PF"
./run_backend.sh
```

## 4. Abrir la app

Abre tu app normal. Si encuentra `.env.cloud` con `DATA_MODE=cloud`, empezara a usar la API.

## 5. Cuando tengas URL publica

Cambia solo esta linea:

```env
API_BASE_URL=https://tu-backend-publico.onrender.com
```

o:

```env
API_BASE_URL=https://tu-backend-publico.up.railway.app
```

## Que ya funciona en modo nube

- leer clientes
- guardar clientes
- leer documentos
- leer documento por ID o numero
- crear documentos
- crear ordenes
- crear detalles de orden
- actualizar totales del documento
- actualizar metodo de pago
- actualizar recogida
- registrar y editar cobros
- abono automatico desde facturacion
- eliminar documento desde historial

## Siguiente paso real

Cuando quieras subirlo de verdad, sigue [DEPLOY_NUBE.md](/Users/elianpaniagua/Documents/Facturacion%20PF/DEPLOY_NUBE.md).
