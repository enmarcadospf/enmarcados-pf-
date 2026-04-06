from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.crud import (
    listar_tarifas,
    buscar_documentos,
    actualizar_cobro,
    actualizar_documento,
    eliminar_cobro,
    eliminar_documento,
    eliminar_todos_documentos,
    eliminar_tarifa,
    eliminar_todas_tarifas,
    listar_clientes,
    listar_documentos,
    crear_cobro,
    crear_detalle_orden,
    crear_documento,
    crear_orden,
    obtener_cliente_por_nombre,
    obtener_documento,
    obtener_documento_por_numero,
    obtener_tarifa_por_codigo,
    upsert_cliente,
    upsert_tarifa,
)
from backend.database import Base, engine, get_db
from backend.schemas import (
    ClienteIn,
    CobroIn,
    CobroUpdateIn,
    DocumentoIn,
    DocumentoUpdateIn,
    OrdenDetalleIn,
    OrdenIn,
    TarifaIn,
)


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)


def serializar_cliente(cliente):
    if not cliente:
        return None
    return {
        "id": cliente.id,
        "nombre": cliente.nombre,
        "telefono": cliente.telefono,
        "rnc": cliente.rnc,
        "direccion": cliente.direccion,
    }


def serializar_tarifa(tarifa):
    if not tarifa:
        return None
    return {
        "codigo": tarifa.codigo,
        "nombre": tarifa.nombre,
        "precio": tarifa.precio,
        "extra": tarifa.extra,
    }


def serializar_detalle_orden(detalle):
    return {
        "id": detalle.id,
        "orden_id": detalle.orden_id,
        "cantidad": detalle.cantidad,
        "codigo_material": detalle.codigo_material,
        "descripcion_material": detalle.descripcion_material,
        "ancho": detalle.ancho,
        "largo": detalle.largo,
        "pies": detalle.pies,
        "precio": detalle.precio,
        "subtotal": detalle.subtotal,
        "total": detalle.total,
    }


def serializar_orden(orden, incluir_detalles=True):
    data = {
        "id": orden.id,
        "documento_id": orden.documento_id,
        "a_enmarcar": orden.a_enmarcar,
        "notas": orden.notas,
        "ancho": orden.ancho,
        "largo": orden.largo,
        "total_orden": orden.total_orden,
    }
    if incluir_detalles:
        data["detalles"] = [serializar_detalle_orden(item) for item in orden.detalles]
    return data


def serializar_cobro(cobro):
    return {
        "id": cobro.id,
        "documento_id": cobro.documento_id,
        "numero_doc": cobro.numero_doc,
        "cliente_nombre": cobro.cliente_nombre,
        "fecha": cobro.fecha,
        "monto": cobro.monto,
        "metodo_pago": cobro.metodo_pago,
        "referencia": cobro.referencia,
        "pagado_total": cobro.pagado_total,
    }


def serializar_documento(documento, incluir_relaciones=True):
    data = {
        "id": documento.id,
        "tipo": documento.tipo,
        "numero_doc": documento.numero_doc,
        "cliente_id": documento.cliente_id,
        "fecha": documento.fecha,
        "fecha_entrega": documento.fecha_entrega,
        "subtotal": documento.subtotal,
        "descuento": documento.descuento,
        "itbis": documento.itbis,
        "total_final": documento.total_final,
        "cerrado": documento.cerrado,
        "metodo_pago": documento.metodo_pago,
        "retirado": documento.retirado,
    }
    if incluir_relaciones:
        data["cliente"] = serializar_cliente(documento.cliente)
        data["ordenes"] = [serializar_orden(item, incluir_detalles=True) for item in documento.ordenes]
        data["cobros"] = [serializar_cobro(item) for item in documento.cobros]
    return data

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def manejar_error_general(request: Request, exc: Exception):
    detalle = str(exc)
    if settings.app_env == "production":
        detalle = "Internal Server Error"
    return JSONResponse(
        status_code=500,
        content={
            "error": detalle,
            "path": str(request.url.path),
            "type": exc.__class__.__name__,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@app.get("/clientes")
def get_clientes(db: Session = Depends(get_db)):
    return [serializar_cliente(item) for item in listar_clientes(db)]


@app.get("/tarifas")
def get_tarifas(db: Session = Depends(get_db)):
    return [serializar_tarifa(item) for item in listar_tarifas(db)]


@app.get("/tarifas/{codigo}")
def get_tarifa(codigo: int, db: Session = Depends(get_db)):
    tarifa = obtener_tarifa_por_codigo(db, codigo)
    if not tarifa:
        return {"error": "Tarifa no encontrada"}
    return serializar_tarifa(tarifa)


@app.get("/clientes/by-name/{nombre}")
def get_cliente_by_name(nombre: str, db: Session = Depends(get_db)):
    cliente = obtener_cliente_por_nombre(db, nombre)
    if not cliente:
        return {"error": "Cliente no encontrado"}
    return serializar_cliente(cliente)


@app.post("/clientes")
def post_cliente(payload: ClienteIn, db: Session = Depends(get_db)):
    cliente = upsert_cliente(db, payload.nombre, payload.telefono, payload.rnc, payload.direccion)
    return serializar_cliente(cliente)


@app.post("/tarifas")
def post_tarifa(payload: TarifaIn, db: Session = Depends(get_db)):
    tarifa = upsert_tarifa(db, payload.codigo, payload.nombre, payload.precio, payload.extra)
    return serializar_tarifa(tarifa)


@app.get("/documentos")
def get_documentos(limit: int = 100, filtro: str = "", db: Session = Depends(get_db)):
    if filtro:
        return [serializar_documento(item) for item in buscar_documentos(db, filtro=filtro, limit=limit)]
    return [serializar_documento(item) for item in listar_documentos(db, limit=limit)]


@app.get("/documentos/{documento_id}")
def get_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = obtener_documento(db, documento_id)
    if not documento:
        return {"error": "Documento no encontrado"}
    return serializar_documento(documento)


@app.get("/documentos/by-number/{numero_doc}")
def get_documento_by_number(numero_doc: int, db: Session = Depends(get_db)):
    documento = obtener_documento_por_numero(db, numero_doc)
    if not documento:
        return {"error": "Documento no encontrado"}
    return serializar_documento(documento)


@app.post("/documentos")
def post_documento(payload: DocumentoIn, db: Session = Depends(get_db)):
    documento = crear_documento(db, payload.tipo, payload.cliente_id, payload.fecha, payload.fecha_entrega, payload.numero_doc)
    return serializar_documento(documento, incluir_relaciones=False)


@app.put("/documentos/{documento_id}")
def put_documento(documento_id: int, payload: DocumentoUpdateIn, db: Session = Depends(get_db)):
    documento = actualizar_documento(db, documento_id, **payload.model_dump())
    if not documento:
        return {"error": "Documento no encontrado"}
    return serializar_documento(documento)


@app.post("/ordenes")
def post_orden(payload: OrdenIn, db: Session = Depends(get_db)):
    orden = crear_orden(
        db,
        payload.documento_id,
        payload.a_enmarcar,
        payload.notas,
        payload.ancho,
        payload.largo,
        payload.total_orden,
    )
    return serializar_orden(orden, incluir_detalles=False)


@app.post("/orden-detalles")
def post_orden_detalle(payload: OrdenDetalleIn, db: Session = Depends(get_db)):
    detalle = crear_detalle_orden(db, **payload.model_dump())
    return serializar_detalle_orden(detalle)


@app.post("/cobros")
def post_cobro(payload: CobroIn, db: Session = Depends(get_db)):
    cobro = crear_cobro(db, **payload.model_dump())
    return serializar_cobro(cobro)


@app.put("/cobros/{cobro_id}")
def put_cobro(cobro_id: int, payload: CobroUpdateIn, db: Session = Depends(get_db)):
    cobro = actualizar_cobro(db, cobro_id, **payload.model_dump())
    if not cobro:
        return {"error": "Cobro no encontrado"}
    return serializar_cobro(cobro)


@app.delete("/documentos/{documento_id}")
def delete_documento(documento_id: int, db: Session = Depends(get_db)):
    ok = eliminar_documento(db, documento_id)
    return {"ok": ok}


@app.delete("/documentos")
def delete_todos_documentos(db: Session = Depends(get_db)):
    borrados = eliminar_todos_documentos(db)
    return {"ok": True, "borrados": borrados}


@app.delete("/cobros/{cobro_id}")
def delete_cobro(cobro_id: int, db: Session = Depends(get_db)):
    ok = eliminar_cobro(db, cobro_id)
    return {"ok": ok}


@app.delete("/tarifas/{codigo}")
def delete_tarifa(codigo: int, db: Session = Depends(get_db)):
    ok = eliminar_tarifa(db, codigo)
    return {"ok": ok}


@app.delete("/tarifas")
def delete_todas_tarifas(db: Session = Depends(get_db)):
    borradas = eliminar_todas_tarifas(db)
    return {"ok": True, "borradas": borradas}


@app.post("/admin/create-tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"status": "created"}
