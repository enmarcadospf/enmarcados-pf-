from sqlalchemy import cast, select, String, or_, text
from sqlalchemy.orm import Session, selectinload

from backend import models


def _sync_sequence(db: Session, table_name: str, pk_name: str = "id"):
    bind = db.get_bind()
    if bind is None or bind.dialect.name != "postgresql":
        return
    db.execute(
        text(
            f"""
            SELECT setval(
                pg_get_serial_sequence('{table_name}', '{pk_name}'),
                COALESCE((SELECT MAX({pk_name}) FROM {table_name}), 0) + 1,
                false
            )
            """
        )
    )


def listar_clientes(db: Session):
    stmt = select(models.Cliente).order_by(models.Cliente.nombre.asc())
    return db.scalars(stmt).all()


def listar_tarifas(db: Session):
    stmt = select(models.Tarifa).order_by(models.Tarifa.codigo.asc())
    return db.scalars(stmt).all()


def obtener_tarifa_por_codigo(db: Session, codigo: int):
    stmt = select(models.Tarifa).where(models.Tarifa.codigo == codigo)
    return db.scalars(stmt).first()


def obtener_cliente_por_nombre(db: Session, nombre: str):
    stmt = select(models.Cliente).where(models.Cliente.nombre == nombre)
    return db.scalars(stmt).first()


def eliminar_cliente_por_nombre(db: Session, nombre: str):
    cliente = obtener_cliente_por_nombre(db, nombre)
    if not cliente:
        return {"ok": False, "error": "Cliente no encontrado"}
    if cliente.documentos:
        return {"ok": False, "error": "El cliente tiene documentos asociados"}
    db.delete(cliente)
    db.commit()
    return {"ok": True}


def listar_documentos(db: Session, limit: int = 100):
    stmt = (
        select(models.Documento)
        .options(selectinload(models.Documento.cliente))
        .order_by(models.Documento.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def buscar_documentos(db: Session, filtro: str, limit: int = 100):
    filtro = (filtro or "").strip().lower()
    if not filtro:
        return listar_documentos(db, limit=limit)

    like = f"%{filtro}%"
    stmt = (
        select(models.Documento)
        .join(models.Documento.cliente)
        .options(selectinload(models.Documento.cliente))
        .where(
            or_(
                models.Cliente.nombre.ilike(like),
                models.Documento.tipo.ilike(like),
                cast(models.Documento.numero_doc, String).ilike(like),
                models.Documento.fecha.ilike(like),
            )
        )
        .order_by(models.Documento.id.desc())
        .limit(limit)
    )
    return db.scalars(stmt).all()


def obtener_documento(db: Session, documento_id: int):
    stmt = (
        select(models.Documento)
        .where(models.Documento.id == documento_id)
        .options(
            selectinload(models.Documento.cliente),
            selectinload(models.Documento.ordenes).selectinload(models.Orden.detalles),
            selectinload(models.Documento.cobros),
        )
    )
    return db.scalars(stmt).first()


def obtener_documento_por_numero(db: Session, numero_doc: int):
    stmt = (
        select(models.Documento)
        .where(models.Documento.numero_doc == numero_doc)
        .options(
            selectinload(models.Documento.cliente),
            selectinload(models.Documento.ordenes).selectinload(models.Orden.detalles),
            selectinload(models.Documento.cobros),
        )
        .order_by(models.Documento.id.desc())
    )
    return db.scalars(stmt).first()


def upsert_cliente(db: Session, nombre: str, telefono: str | None, rnc: str | None, direccion: str | None):
    cliente = obtener_cliente_por_nombre(db, nombre)
    if cliente:
        cliente.telefono = telefono
        cliente.rnc = rnc
        cliente.direccion = direccion
    else:
        _sync_sequence(db, "clientes")
        cliente = models.Cliente(nombre=nombre, telefono=telefono, rnc=rnc, direccion=direccion)
        db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def upsert_tarifa(db: Session, codigo: int, nombre: str, precio: float, extra: float = 0):
    tarifa = obtener_tarifa_por_codigo(db, codigo)
    if tarifa:
        tarifa.nombre = nombre
        tarifa.precio = precio
        tarifa.extra = extra
    else:
        tarifa = models.Tarifa(codigo=codigo, nombre=nombre, precio=precio, extra=extra)
        db.add(tarifa)
    db.commit()
    db.refresh(tarifa)
    return tarifa


def siguiente_numero_documento(db: Session, tipo: str) -> int:
    stmt = select(models.Documento).where(models.Documento.tipo == tipo).order_by(models.Documento.numero_doc.desc())
    ultimo = db.scalars(stmt).first()
    return (ultimo.numero_doc or 0) + 1 if ultimo else 1


def crear_documento(db: Session, tipo: str, cliente_id: int, fecha: str, fecha_entrega: str = "", numero_doc: int | None = None):
    _sync_sequence(db, "documentos")
    documento = models.Documento(
        tipo=tipo,
        numero_doc=numero_doc or siguiente_numero_documento(db, tipo),
        cliente_id=cliente_id,
        fecha=fecha,
        fecha_entrega=fecha_entrega or "",
    )
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento


def actualizar_documento(db: Session, documento_id: int, **campos):
    documento = obtener_documento(db, documento_id)
    if not documento:
        return None
    for clave, valor in campos.items():
        if valor is not None and hasattr(documento, clave):
            setattr(documento, clave, valor)
    db.commit()
    db.refresh(documento)
    return documento


def crear_orden(db: Session, documento_id: int, a_enmarcar: str, notas: str, ancho: float, largo: float, total_orden: float):
    _sync_sequence(db, "ordenes")
    orden = models.Orden(
        documento_id=documento_id,
        a_enmarcar=a_enmarcar,
        notas=notas or "",
        ancho=ancho,
        largo=largo,
        total_orden=total_orden,
    )
    db.add(orden)
    db.commit()
    db.refresh(orden)
    return orden


def crear_detalle_orden(db: Session, **payload):
    _sync_sequence(db, "orden_detalles")
    detalle = models.OrdenDetalle(**payload)
    db.add(detalle)
    db.commit()
    db.refresh(detalle)
    return detalle


def crear_cobro(db: Session, **payload):
    _sync_sequence(db, "cobros")
    cobro = models.Cobro(**payload)
    db.add(cobro)
    db.commit()
    db.refresh(cobro)
    return cobro


def actualizar_cobro(db: Session, cobro_id: int, **campos):
    cobro = db.get(models.Cobro, cobro_id)
    if not cobro:
        return None
    for clave, valor in campos.items():
        if valor is not None and hasattr(cobro, clave):
            setattr(cobro, clave, valor)
    db.commit()
    db.refresh(cobro)
    return cobro


def eliminar_documento(db: Session, documento_id: int) -> bool:
    documento = obtener_documento(db, documento_id)
    if not documento:
        return False
    db.delete(documento)
    db.commit()
    return True


def eliminar_todos_documentos(db: Session) -> int:
    documentos = db.scalars(select(models.Documento)).all()
    total = len(documentos)
    for documento in documentos:
        db.delete(documento)
    db.commit()
    return total


def eliminar_cobro(db: Session, cobro_id: int) -> bool:
    cobro = db.get(models.Cobro, cobro_id)
    if not cobro:
        return False
    db.delete(cobro)
    db.commit()
    return True


def eliminar_tarifa(db: Session, codigo: int) -> bool:
    tarifa = db.get(models.Tarifa, codigo)
    if not tarifa:
        return False
    db.delete(tarifa)
    db.commit()
    return True


def eliminar_todas_tarifas(db: Session) -> int:
    borradas = db.query(models.Tarifa).delete()
    db.commit()
    return borradas
