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


def obtener_orden(db: Session, orden_id: int):
    stmt = (
        select(models.Orden)
        .where(models.Orden.id == orden_id)
        .options(
            selectinload(models.Orden.detalles),
            selectinload(models.Orden.documento).selectinload(models.Documento.cobros),
        )
    )
    return db.scalars(stmt).first()


def _resolver_descuento(subtotal: float, descuento_valor: float):
    descuento_valor = max(0.0, float(descuento_valor or 0))
    if descuento_valor <= 100:
        descuento_pct = descuento_valor
        descuento_monto = subtotal * (descuento_pct / 100.0)
    else:
        descuento_monto = min(subtotal, descuento_valor)
        descuento_pct = (descuento_monto / subtotal * 100.0) if subtotal else 0.0
    return descuento_pct, descuento_monto


def recalcular_documento_desde_ordenes(db: Session, documento_id: int):
    documento = obtener_documento(db, documento_id)
    if not documento:
        return None

    subtotal = sum(float(orden.total_orden or 0) for orden in documento.ordenes)
    descuento_pct, descuento_monto = _resolver_descuento(subtotal, documento.descuento or 0)
    base_imponible = max(0.0, subtotal - descuento_monto)
    itbis = base_imponible * 0.18
    total_final = base_imponible + itbis

    documento.subtotal = subtotal
    documento.descuento = descuento_pct
    documento.itbis = itbis
    documento.total_final = total_final

    acumulado = sum(float(cobro.monto or 0) for cobro in documento.cobros)
    pagado_total = acumulado >= total_final and total_final > 0
    for cobro in documento.cobros:
        cobro.pagado_total = pagado_total

    db.commit()
    db.refresh(documento)
    return documento


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


def actualizar_orden(db: Session, orden_id: int, **campos):
    orden = obtener_orden(db, orden_id)
    if not orden:
        return None

    for clave in ("a_enmarcar", "notas", "ancho", "largo", "total_orden"):
        if clave in campos and campos[clave] is not None and hasattr(orden, clave):
            setattr(orden, clave, campos[clave])

    detalles = campos.get("detalles")
    if detalles is not None:
        for detalle in list(orden.detalles):
            db.delete(detalle)
        db.flush()
        for item in detalles:
            _sync_sequence(db, "orden_detalles")
            db.add(
                models.OrdenDetalle(
                    orden_id=orden.id,
                    cantidad=item["cantidad"],
                    codigo_material=item["codigo_material"],
                    descripcion_material=item["descripcion_material"],
                    ancho=item["ancho"],
                    largo=item["largo"],
                    pies=item["pies"],
                    precio=item["precio"],
                    subtotal=item["subtotal"],
                    total=item["total"],
                )
            )

    db.commit()
    db.refresh(orden)
    recalcular_documento_desde_ordenes(db, orden.documento_id)
    return obtener_orden(db, orden_id)


def eliminar_orden(db: Session, orden_id: int) -> bool:
    orden = obtener_orden(db, orden_id)
    if not orden:
        return False
    documento_id = orden.documento_id
    db.delete(orden)
    db.commit()
    recalcular_documento_desde_ordenes(db, documento_id)
    return True


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
