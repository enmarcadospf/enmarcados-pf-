from pydantic import BaseModel


class ClienteOut(BaseModel):
    id: int
    nombre: str
    telefono: str | None = None
    rnc: str | None = None
    direccion: str | None = None

    class Config:
        from_attributes = True


class TarifaIn(BaseModel):
    codigo: int
    nombre: str
    precio: float
    extra: float = 0


class DocumentoResumenOut(BaseModel):
    id: int
    tipo: str
    numero_doc: int | None = None
    fecha: str
    fecha_entrega: str = ""
    subtotal: float
    descuento: float
    itbis: float
    total_final: float
    cerrado: bool
    metodo_pago: str
    retirado: bool

    class Config:
        from_attributes = True


class ClienteIn(BaseModel):
    nombre: str
    telefono: str | None = None
    rnc: str | None = None
    direccion: str | None = None


class DocumentoIn(BaseModel):
    tipo: str
    cliente_id: int
    fecha: str
    fecha_entrega: str = ""
    numero_doc: int | None = None


class DocumentoUpdateIn(BaseModel):
    subtotal: float | None = None
    descuento: float | None = None
    itbis: float | None = None
    total_final: float | None = None
    cerrado: bool | None = None
    metodo_pago: str | None = None
    retirado: bool | None = None
    fecha_entrega: str | None = None


class OrdenIn(BaseModel):
    documento_id: int
    a_enmarcar: str
    notas: str = ""
    ancho: float = 0
    largo: float = 0
    total_orden: float = 0


class OrdenDetalleIn(BaseModel):
    orden_id: int
    cantidad: float
    codigo_material: int
    descripcion_material: str
    ancho: float
    largo: float
    pies: float
    precio: float
    subtotal: float
    total: float


class OrdenDetallePayload(BaseModel):
    cantidad: float
    codigo_material: int
    descripcion_material: str
    ancho: float
    largo: float
    pies: float
    precio: float
    subtotal: float
    total: float


class OrdenUpdateIn(BaseModel):
    a_enmarcar: str
    notas: str = ""
    ancho: float = 0
    largo: float = 0
    total_orden: float = 0
    detalles: list[OrdenDetallePayload] = []


class CobroIn(BaseModel):
    documento_id: int
    numero_doc: int
    cliente_nombre: str
    fecha: str
    monto: float
    metodo_pago: str
    referencia: str | None = None
    pagado_total: bool = False


class CobroUpdateIn(BaseModel):
    fecha: str | None = None
    monto: float | None = None
    metodo_pago: str | None = None
    referencia: str | None = None
    pagado_total: bool | None = None
