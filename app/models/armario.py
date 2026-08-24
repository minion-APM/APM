from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Armario(Base):
    __tablename__ = "armarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero = Column(String(30), nullable=False, unique=True, index=True)
    descricao = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="disponivel", index=True)
    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alugado_em = Column(DateTime, nullable=True)
    criado_em = Column(DateTime, nullable=False, server_default=func.now())
    atualizado_em = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    cliente = relationship("Cliente", back_populates="armarios")
    alugueis = relationship("AluguelArmario", back_populates="armario")


class AluguelArmario(Base):
    __tablename__ = "alugueis_armarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    armario_id = Column(Integer, ForeignKey("armarios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    inicio_em = Column(DateTime, nullable=False)
    devolvido_em = Column(DateTime, nullable=True)

    armario = relationship("Armario", back_populates="alugueis")
    cliente = relationship("Cliente", back_populates="alugueis_armarios")
    usuario = relationship("Usuario")
