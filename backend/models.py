from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    telefono: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rnc: Mapped[str | None] = mapped_column(String(50), nullable=True)
    direccion: Mapped[str | None] = mapped_column(Text, nullable=True)

    documentos: Mapped[list["Documento"]] = relationship(back_populates="cliente")


class Documento(Base):
    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50), index=True)
    numero_doc: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    fecha: Mapped[str] = mapped_column(String(20))
    fecha_entrega: Mapped[str] = mapped_column(String(20), default="")
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    descuento: Mapped[float] = mapped_column(Float, default=0)
    itbis: Mapped[float] = mapped_column(Float, default=0)
    total_final: Mapped[float] = mapped_column(Float, default=0)
    cerrado: Mapped[bool] = mapped_column(Boolean, default=False)
    metodo_pago: Mapped[str] = mapped_column(String(50), default="Pendiente")
    retirado: Mapped[bool] = mapped_column(Boolean, default=False)

    cliente: Mapped["Cliente"] = relationship(back_populates="documentos")
    ordenes: Mapped[list["Orden"]] = relationship(back_populates="documento", cascade="all, delete-orphan")
    cobros: Mapped[list["Cobro"]] = relationship(back_populates="documento", cascade="all, delete-orphan")


class Orden(Base):
    __tablename__ = "ordenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), index=True)
    a_enmarcar: Mapped[str] = mapped_column(Text)
    notas: Mapped[str] = mapped_column(Text, default="")
    ancho: Mapped[float] = mapped_column(Float, default=0)
    largo: Mapped[float] = mapped_column(Float, default=0)
    total_orden: Mapped[float] = mapped_column(Float, default=0)

    documento: Mapped["Documento"] = relationship(back_populates="ordenes")
    detalles: Mapped[list["OrdenDetalle"]] = relationship(back_populates="orden", cascade="all, delete-orphan")


class OrdenDetalle(Base):
    __tablename__ = "orden_detalles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orden_id: Mapped[int] = mapped_column(ForeignKey("ordenes.id"), index=True)
    cantidad: Mapped[float] = mapped_column(Float, default=0)
    codigo_material: Mapped[int] = mapped_column(Integer, index=True)
    descripcion_material: Mapped[str] = mapped_column(Text)
    ancho: Mapped[float] = mapped_column(Float, default=0)
    largo: Mapped[float] = mapped_column(Float, default=0)
    pies: Mapped[float] = mapped_column(Float, default=0)
    precio: Mapped[float] = mapped_column(Float, default=0)
    subtotal: Mapped[float] = mapped_column(Float, default=0)
    total: Mapped[float] = mapped_column(Float, default=0)

    orden: Mapped["Orden"] = relationship(back_populates="detalles")


class Cobro(Base):
    __tablename__ = "cobros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    documento_id: Mapped[int] = mapped_column(ForeignKey("documentos.id"), index=True)
    numero_doc: Mapped[int] = mapped_column(Integer, index=True)
    cliente_nombre: Mapped[str] = mapped_column(String(255))
    fecha: Mapped[str] = mapped_column(String(20))
    monto: Mapped[float] = mapped_column(Float, default=0)
    metodo_pago: Mapped[str] = mapped_column(String(50), default="Pendiente")
    referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    pagado_total: Mapped[bool] = mapped_column(Boolean, default=False)

    documento: Mapped["Documento"] = relationship(back_populates="cobros")
