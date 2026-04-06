import sqlite3
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Cliente, Cobro, Documento, Orden, OrdenDetalle


def importar(sqlite_path: str, postgres_url: str) -> None:
    sqlite_path = str(Path(sqlite_path).expanduser().resolve())
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    engine = create_engine(postgres_url, future=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        clientes_map: dict[int, Cliente] = {}
        documentos_map: dict[int, Documento] = {}
        ordenes_map: dict[int, Orden] = {}

        for row in sqlite_conn.execute("SELECT id, nombre, telefono, rnc, direccion FROM clientes ORDER BY id"):
            cliente = Cliente(
                id=row["id"],
                nombre=row["nombre"],
                telefono=row["telefono"],
                rnc=row["rnc"],
                direccion=row["direccion"],
            )
            session.add(cliente)
            clientes_map[cliente.id] = cliente

        for row in sqlite_conn.execute(
            """
            SELECT id, tipo, numero_doc, cliente_id, fecha, COALESCE(fecha_entrega, '') AS fecha_entrega,
                   subtotal, descuento, itbis, total_final, cerrado, metodo_pago, retirado
            FROM documentos
            ORDER BY id
            """
        ):
            documento = Documento(
                id=row["id"],
                tipo=row["tipo"],
                numero_doc=row["numero_doc"],
                cliente_id=row["cliente_id"],
                fecha=row["fecha"],
                fecha_entrega=row["fecha_entrega"],
                subtotal=row["subtotal"] or 0,
                descuento=row["descuento"] or 0,
                itbis=row["itbis"] or 0,
                total_final=row["total_final"] or 0,
                cerrado=bool(row["cerrado"]),
                metodo_pago=row["metodo_pago"] or "Pendiente",
                retirado=bool(row["retirado"]),
            )
            session.add(documento)
            documentos_map[documento.id] = documento

        for row in sqlite_conn.execute(
            """
            SELECT id, COALESCE(documento_id, factura_id) AS documento_real, a_enmarcar,
                   COALESCE(notas, '') AS notas, ancho, largo, total_orden
            FROM ordenes
            ORDER BY id
            """
        ):
            orden = Orden(
                id=row["id"],
                documento_id=row["documento_real"],
                a_enmarcar=row["a_enmarcar"],
                notas=row["notas"],
                ancho=row["ancho"] or 0,
                largo=row["largo"] or 0,
                total_orden=row["total_orden"] or 0,
            )
            session.add(orden)
            ordenes_map[orden.id] = orden

        for row in sqlite_conn.execute(
            """
            SELECT id, orden_id, cantidad, codigo_material, descripcion_material, ancho, largo, pies, precio, subtotal, total
            FROM orden_detalles
            ORDER BY id
            """
        ):
            session.add(
                OrdenDetalle(
                    id=row["id"],
                    orden_id=row["orden_id"],
                    cantidad=row["cantidad"] or 0,
                    codigo_material=row["codigo_material"],
                    descripcion_material=row["descripcion_material"],
                    ancho=row["ancho"] or 0,
                    largo=row["largo"] or 0,
                    pies=row["pies"] or 0,
                    precio=row["precio"] or 0,
                    subtotal=row["subtotal"] or 0,
                    total=row["total"] or 0,
                )
            )

        for row in sqlite_conn.execute(
            """
            SELECT id, documento_id, numero_doc, cliente_nombre, fecha, monto, metodo_pago, referencia, pagado_total
            FROM cobros
            ORDER BY id
            """
        ):
            session.add(
                Cobro(
                    id=row["id"],
                    documento_id=row["documento_id"],
                    numero_doc=row["numero_doc"],
                    cliente_nombre=row["cliente_nombre"],
                    fecha=row["fecha"],
                    monto=row["monto"] or 0,
                    metodo_pago=row["metodo_pago"] or "Pendiente",
                    referencia=row["referencia"],
                    pagado_total=bool(row["pagado_total"]),
                )
            )

        session.commit()

    sqlite_conn.close()


if __name__ == "__main__":
    import os

    sqlite_path = os.getenv("SQLITE_PATH", "facturacion.db")
    postgres_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/enmarcados_pf",
    )
    importar(sqlite_path, postgres_url)
    print("Importacion completada.")
