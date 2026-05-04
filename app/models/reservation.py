from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Enum, TIMESTAMP, Text, String
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime # Importamos la clase directamente

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    reservation_date = Column(Date, nullable=False)
    reservation_time = Column(Time, nullable=False)
    pax = Column(Integer, nullable=False)
    status = Column(Enum('confirmada', 'cancelada', 'finalizada'), default='confirmada')
    
    # Usamos datetime.now sin paréntesis para que se ejecute en cada inserción
    created_at = Column(TIMESTAMP, default=datetime.now)
    updated_at = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)

    customer = relationship("Customer", back_populates="reservations")
    table = relationship("Table", back_populates="reservations")
    creator = relationship("User", back_populates="reservations_created")
    logs = relationship("AuditLog", back_populates="reservation")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="SET NULL"))
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50))
    details = Column(Text)
    
    # Se eliminó la advertencia de desuso y el error de 'datetime.datetime'
    change_date = Column(TIMESTAMP, default=datetime.now)

    reservation = relationship("Reservation", back_populates="logs")
    operator = relationship("User", back_populates="logs")