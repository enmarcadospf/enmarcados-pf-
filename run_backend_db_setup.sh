#!/bin/zsh
set -e

cd "$(dirname "$0")"

if [ -f ".env.backend" ]; then
  set -a
  source .env.backend
  set +a
fi

echo "Probando conexion a PostgreSQL..."
.venv/bin/python backend/test_connection.py

echo "Creando tablas..."
.venv/bin/python backend/create_tables.py

echo "Importando datos desde SQLite..."
.venv/bin/python backend/import_sqlite.py

echo "Proceso completado."
