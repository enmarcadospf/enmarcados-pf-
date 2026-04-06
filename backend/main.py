from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.crud import (
    buscar_documentos,
    actualizar_cobro,
    actualizar_documento,
    eliminar_cobro,
    eliminar_documento,
    listar_clientes,
    listar_documentos,
    crear_cobro,
    crear_detalle_orden,
    crear_documento,
    crear_orden,
    obtener_cliente_por_nombre,
    obtener_documento,
    obtener_documento_por_numero,
    upsert_cliente,
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
)


settings = get_settings()
app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "env": settings.app_env}


@app.get("/clientes")
def get_clientes(db: Session = Depends(get_db)):
    return listar_clientes(db)


@app.get("/clientes/by-name/{nombre}")
def get_cliente_by_name(nombre: str, db: Session = Depends(get_db)):
    cliente = obtener_cliente_por_nombre(db, nombre)
    if not cliente:
        return {"error": "Cliente no encontrado"}
    return cliente


@app.post("/clientes")
def post_cliente(payload: ClienteIn, db: Session = Depends(get_db)):
    return upsert_cliente(db, payload.nombre, payload.telefono, payload.rnc, payload.direccion)


@app.get("/documentos")
def get_documentos(limit: int = 100, filtro: str = "", db: Session = Depends(get_db)):
    if filtro:
        return buscar_documentos(db, filtro=filtro, limit=limit)
    return listar_documentos(db, limit=limit)


@app.get("/documentos/{documento_id}")
def get_documento(documento_id: int, db: Session = Depends(get_db)):
    documento = obtener_documento(db, documento_id)
    if not documento:
        return {"error": "Documento no encontrado"}
    return documento


@app.get("/documentos/by-number/{numero_doc}")
def get_documento_by_number(numero_doc: int, db: Session = Depends(get_db)):
    documento = obtener_documento_por_numero(db, numero_doc)
    if not documento:
        return {"error": "Documento no encontrado"}
    return documento


@app.post("/documentos")
def post_documento(payload: DocumentoIn, db: Session = Depends(get_db)):
    return crear_documento(db, payload.tipo, payload.cliente_id, payload.fecha, payload.fecha_entrega, payload.numero_doc)


@app.put("/documentos/{documento_id}")
def put_documento(documento_id: int, payload: DocumentoUpdateIn, db: Session = Depends(get_db)):
    documento = actualizar_documento(db, documento_id, **payload.model_dump())
    if not documento:
        return {"error": "Documento no encontrado"}
    return documento


@app.post("/ordenes")
def post_orden(payload: OrdenIn, db: Session = Depends(get_db)):
    return crear_orden(
        db,
        payload.documento_id,
        payload.a_enmarcar,
        payload.notas,
        payload.ancho,
        payload.largo,
        payload.total_orden,
    )


@app.post("/orden-detalles")
def post_orden_detalle(payload: OrdenDetalleIn, db: Session = Depends(get_db)):
    return crear_detalle_orden(db, **payload.model_dump())


@app.post("/cobros")
def post_cobro(payload: CobroIn, db: Session = Depends(get_db)):
    return crear_cobro(db, **payload.model_dump())


@app.put("/cobros/{cobro_id}")
def put_cobro(cobro_id: int, payload: CobroUpdateIn, db: Session = Depends(get_db)):
    cobro = actualizar_cobro(db, cobro_id, **payload.model_dump())
    if not cobro:
        return {"error": "Cobro no encontrado"}
    return cobro


@app.delete("/documentos/{documento_id}")
def delete_documento(documento_id: int, db: Session = Depends(get_db)):
    ok = eliminar_documento(db, documento_id)
    return {"ok": ok}


@app.delete("/cobros/{cobro_id}")
def delete_cobro(cobro_id: int, db: Session = Depends(get_db)):
    ok = eliminar_cobro(db, cobro_id)
    return {"ok": ok}


@app.post("/admin/create-tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"status": "created"}
