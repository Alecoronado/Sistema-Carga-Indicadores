from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Objective(Base):
    __tablename__ = "objectives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_objetivo = Column(String(20), unique=True, nullable=False, index=True)
    objetivo_institucional = Column(Text)
    objetivo_anual = Column(Text)
    lineamiento = Column(String(100))
    tipo_objetivo = Column(String(50))
    unidades_organizacionales = Column(String(100))

    indicators = relationship("Indicator", back_populates="objective", cascade="all, delete-orphan")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_indicador = Column(String(20), unique=True, nullable=False, index=True)
    id_objetivo = Column(String(20), ForeignKey("objectives.id_objetivo"), nullable=False)
    unidad_organizacional = Column(String(50))
    division_area = Column(String(100))
    lineamiento = Column(String(100))
    objetivo_anual = Column(Text)
    indicador = Column(Text)
    acciones = Column(Text)
    resultado_esperado = Column(Text)
    tipo_objetivo = Column(String(50))
    clasificacion = Column(String(50))
    unidad_medida = Column(String(20))
    meta = Column(Float)
    avance_valor = Column(Float, default=0)
    avance_pct = Column(Float, default=0)
    estado = Column(String(50), default="Por Comenzar")
    uo_colaboradora = Column(String(100))
    area_colabora = Column(String(100))
    tiene_hitos = Column(String(5), default="No")
    fecha_inicio = Column(String(20))
    fecha_fin_original = Column(String(20))
    fecha_fin_actual = Column(String(20))
    notas = Column(Text)
    responsable = Column(String(150))
    responsable_carga = Column(String(150))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    objective = relationship("Objective", back_populates="indicators")
    milestones = relationship(
        "Milestone", back_populates="indicator",
        cascade="all, delete-orphan",
        order_by="Milestone.orden"
    )
    history = relationship(
        "ProgressHistory", back_populates="indicator",
        cascade="all, delete-orphan",
        order_by="ProgressHistory.fecha_actualizacion.desc()"
    )


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_hito = Column(String(30), unique=True, nullable=False, index=True)
    id_indicador = Column(String(20), ForeignKey("indicators.id_indicador"), nullable=False)
    nombre_hito = Column(Text)
    orden = Column(Integer, default=1)
    estado = Column(String(50), default="Por Comenzar")
    avance_pct = Column(Float, default=0)
    fecha_inicio = Column(String(20))
    fecha_fin_original = Column(String(20))
    fecha_fin_actual = Column(String(20))
    responsable = Column(String(150))

    indicator = relationship("Indicator", back_populates="milestones")


class MonthlySnapshot(Base):
    __tablename__ = "monthly_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    periodo = Column(String(10), unique=True, nullable=False, index=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    descripcion = Column(Text)
    data_json = Column(Text)


class ProgressHistory(Base):
    __tablename__ = "progress_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_indicador = Column(String(20), ForeignKey("indicators.id_indicador"), nullable=False)
    periodo = Column(String(10))
    avance_valor = Column(Float)
    avance_pct = Column(Float)
    estado = Column(String(50))
    notas = Column(Text)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)

    indicator = relationship("Indicator", back_populates="history")
