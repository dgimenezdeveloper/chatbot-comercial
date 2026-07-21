"""Modelo de apuesta a turnos — funcionalidad de gamificación.

Permite a los clientes apostar sobre la cantidad de turnos que se agendarán
en una fecha determinada.
"""

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.db.database import Base


class TurnoApuesta(Base):
    """Apuestas diarias de clientes sobre cantidad de turnos."""

    __tablename__ = "turno_apuesta"

    id = Column(Integer, primary_key=True, index=True, comment="ID interno autoincremental")
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"),
        nullable=False,
        comment="Negocio de la apuesta",
    )

    appointment_id = Column(
        Integer, ForeignKey("appointment.id", ondelete="SET NULL"),
        nullable=True,
        comment="Turno relacionado (si aplica)",
    )

    user_phone = Column(
        String(20), nullable=True,
        comment="Teléfono del apostador",
    )
    user_name = Column(
        String(200), nullable=True,
        comment="Nombre del apostador",
    )

    # Datos de la apuesta
    scheduled_date = Column(
        Date, nullable=False,
        comment="Fecha sobre la que se apuesta",
    )
    estimated_turnos = Column(
        Integer, default=0,
        comment="Cantidad estimada de turnos por el negocio",
    )
    apuesta_amount = Column(
        Numeric(10, 2), nullable=False, default=0.00,
        comment="Monto apostado",
    )

    status = Column(
        Enum("open", "settled", name="apuesta_status"),
        default="open",
        comment="open=pendiente de resolución, settled=resuelta",
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(),
        comment="Fecha de creación",
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(),
        comment="Fecha de última modificación",
    )
