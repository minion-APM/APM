# Tabela de tamanhos do produto

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ProdutoTamanho(Base):
    __tablename__ = "produto_tamanhos"

    id         = Column(Integer, primary_key=True, autoincrement=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False)
    tamanho    = Column(String(10), nullable=False)  # Ex: PP, P, M, G, GG
    estoque    = Column(Integer, nullable=False, default=0)

    produto = relationship("Produto", back_populates="tamanhos")