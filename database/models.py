from sqlalchemy import Column, Integer, String, Float, Date, Time, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from database.connection import Base


class Filme(Base):
    __tablename__ = "filmes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    genero = Column(String, nullable=False)
    duracao = Column(Integer, nullable=False)
    cor = Column(String)
    imagem = Column(String)

    sessoes = relationship("Sessao", back_populates="filme")  


class Sessao(Base):
    __tablename__ = "sessoes"

    id = Column(Integer, primary_key=True, index=True)
    filme_id = Column(Integer, ForeignKey("filmes.id"), nullable=False)
    data = Column(Date, nullable=False)
    horario = Column(Time, nullable=False)
    sala = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    lugares = Column(Integer, nullable=False)

    filme = relationship("Filme", back_populates="sessoes")
    ingressos = relationship("Ingresso", back_populates="sessao")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    ingressos = relationship("Ingresso", back_populates="cliente")


class Ingresso(Base):
    __tablename__ = "ingressos"

    id = Column(Integer, primary_key=True, index=True)
    sessao_id = Column(Integer, ForeignKey("sessoes.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    cadeira = Column(String, nullable=False)
    preco = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("sessao_id", "cadeira", name="uq_sessao_cadeira"),
    )

    sessao = relationship("Sessao", back_populates="ingressos")
    cliente = relationship("Cliente", back_populates="ingressos")
