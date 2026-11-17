
"""Acesso ao banco. As telas conversam com estas funções, que devolvem dicionários
no mesmo formato do dados_demo.py (por isso as telas nem percebem a troca)."""
from datetime import date, datetime
 
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
 
from database.connection import Base, engine, SessionLocal
from database.models import Filme, Sessao, Cliente, Ingresso
from dados_demo import FILMES_DEMO, CLIENTES_DEMO, CADEIRAS_OCUPADAS_DEMO
 
DATA_PADRAO = date(2026, 11, 16)
PRECO_PADRAO = 10.0
 
SESSOES_SEED = [
    ("Avatar", "14:30", "1", 5),
    ("Titanic", "16:00", "2", 4),
    ("Duna: Parte 2", "19:00", "3", 6),
    ("Barbie", "19:00", "2", 3),
]
 
 
def criar_tabelas():
    Base.metadata.create_all(bind=engine)
 
 
def _hora(texto):
    try:
        return datetime.strptime(str(texto).strip(), "%H:%M").time()
    except ValueError:
        raise ValueError("Horário inválido. Use o formato HH:MM, por exemplo 19:00.")
 
 
def _filme_dict(f):
    return {"titulo": f.titulo, "genero": f.genero, "duracao": f.duracao,
            "cor": f.cor, "imagem": f.imagem}
 
 
def _sessao_dict(s):
    return {"id": s.id, "filme": s.filme.titulo, "horario": s.horario.strftime("%H:%M"),
            "sala": s.sala, "preco": s.preco, "lugares": s.lugares}
 
 
def _cliente_dict(c):
    return {"id": c.id, "nome": c.nome, "email": c.email, "ingressos": len(c.ingressos),
            "gasto": sum(i.preco for i in c.ingressos)}
 
 
def listar_filmes():
    with SessionLocal() as db:
        return [_filme_dict(f) for f in db.query(Filme).order_by(Filme.id)]
 
 
def listar_sessoes():
    with SessionLocal() as db:
        return [_sessao_dict(s) for s in db.query(Sessao).order_by(Sessao.id)]
 
 
def listar_clientes():
    with SessionLocal() as db:
        return [_cliente_dict(c) for c in db.query(Cliente).order_by(Cliente.id)]
 
 
# ---------- gravações (erros de regra viram ValueError, que o app mostra num aviso)
def adicionar_filme(d):
    try:
        duracao = int(d["duracao"])
    except (ValueError, TypeError):
        duracao = 0                       # a janela manda "?" quando fica em branco
    with SessionLocal() as db:
        if db.query(Filme).filter(Filme.titulo == d["titulo"]).first():
            raise ValueError(f'O filme "{d["titulo"]}" já está cadastrado.')
        db.add(Filme(titulo=d["titulo"], genero=d["genero"], duracao=duracao,
                     cor=d.get("cor"), imagem=d.get("imagem")))
        db.commit()
 
 
def adicionar_sessao(d):
    with SessionLocal() as db:
        filme = db.query(Filme).filter(Filme.titulo == d["filme"]).first()
        if filme is None:
            raise ValueError("Filme não encontrado.")
        db.add(Sessao(filme_id=filme.id, data=DATA_PADRAO, horario=_hora(d["horario"]),
                      sala=str(d["sala"]), preco=d.get("preco", PRECO_PADRAO),
                      lugares=d["lugares"]))
        db.commit()
 
 
def adicionar_cliente(d):
    with SessionLocal() as db:
        db.add(Cliente(nome=d["nome"], email=d["email"]))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError("Já existe um cliente com esse e-mail.")
 
 
def remover_filme(titulo):
    """Apaga o filme, as sessões dele e os ingressos dessas sessões."""
    with SessionLocal() as db:
        filme = db.query(Filme).filter(Filme.titulo == titulo).first()
        if filme is None:
            return
        for sessao in filme.sessoes:
            for ingresso in sessao.ingressos:
                db.delete(ingresso)
            db.delete(sessao)
        db.delete(filme)
        db.commit()
 
 
def listar_ocupadas():
    """{id_da_sessao: {"A3", "B7", ...}} com as cadeiras já vendidas."""
    with SessionLocal() as db:
        ocupadas = {}
        for sessao_id, cadeira in db.query(Ingresso.sessao_id, Ingresso.cadeira):
            ocupadas.setdefault(sessao_id, set()).add(cadeira)
        return ocupadas
 
 
def contar_ingressos():
    with SessionLocal() as db:
        return db.query(Ingresso).count()
 
 
def registrar_compra(cliente_id, sessao_id, cadeiras):
    """Grava um ingresso por cadeira. Tudo ou nada: se uma cadeira já foi vendida, nenhuma é gravada."""
    with SessionLocal() as db:
        sessao = db.get(Sessao, sessao_id)
        if sessao is None or db.get(Cliente, cliente_id) is None:
            raise ValueError("Cliente ou sessão não encontrados.")
        for cadeira in cadeiras:
            db.add(Ingresso(sessao_id=sessao_id, cliente_id=cliente_id,
                            cadeira=cadeira, preco=sessao.preco))
        try:
            db.commit()
        except IntegrityError:           # UniqueConstraint (sessao_id, cadeira)
            db.rollback()
            raise ValueError("Alguma dessas cadeiras acabou de ser vendida. Escolha outras.")
 
 
def relatorio_df():
    """DataFrame (pandas) lido do banco: filme, ingressos e faturamento."""
    consulta = (select(Filme.titulo.label("filme"), Ingresso.preco)
                .join(Sessao, Sessao.filme_id == Filme.id)
                .join(Ingresso, Ingresso.sessao_id == Sessao.id))
    df = pd.read_sql(consulta, engine)
    if df.empty:
        return df
    return (df.groupby("filme", as_index=False)
              .agg(ingressos=("preco", "count"), faturamento=("preco", "sum"))
              .sort_values("faturamento", ascending=False))
 
 
def atualizar_imagem(titulo, caminho):
    with SessionLocal() as db:
        filme = db.query(Filme).filter(Filme.titulo == titulo).first()
        if filme:
            filme.imagem = caminho
            db.commit()
 

def popular_se_vazio():
    with SessionLocal() as db:
        if db.query(Filme).count() or db.query(Cliente).count():
            return
        filmes = {}
        for f in FILMES_DEMO:
            filmes[f["titulo"]] = Filme(titulo=f["titulo"], genero=f["genero"],
                                        duracao=f["duracao"], cor=f["cor"], imagem=f["imagem"])
            db.add(filmes[f["titulo"]])
        for c in CLIENTES_DEMO:
            db.add(Cliente(nome=c["nome"], email=c["email"]))
        db.flush()                        # gera os ids dos filmes antes de criar as sessões
        sessoes = []
        for titulo, hora, sala, lugares in SESSOES_SEED:
            sessoes.append(Sessao(filme_id=filmes[titulo].id, data=DATA_PADRAO, horario=_hora(hora),
                                  sala=sala, preco=PRECO_PADRAO, lugares=lugares))
        db.add_all(sessoes)
        db.flush()
        # cadeiras vermelhas de demonstração na 1ª sessão, divididas entre Ana e Bruno
        compradores = db.query(Cliente).order_by(Cliente.id).limit(2).all()
        for i, cadeira in enumerate(sorted(CADEIRAS_OCUPADAS_DEMO)):
            db.add(Ingresso(sessao_id=sessoes[0].id, cliente_id=compradores[i % 2].id,
                            cadeira=cadeira, preco=PRECO_PADRAO))
        db.commit()
 