"""Dados de exemplo (só para ver a interface funcionando)."""
from tema import PALETA

FILMES_DEMO = [
    {"titulo": "Avatar", "genero": "Ficção", "duracao": 162, "cor": PALETA[0], "imagem": None},
    {"titulo": "Avengers: Endgame", "genero": "Ação", "duracao": 181, "cor": PALETA[1], "imagem": None},
    {"titulo": "Titanic", "genero": "Drama", "duracao": 194, "cor": PALETA[2], "imagem": None},
    {"titulo": "Star Wars VII", "genero": "Aventura", "duracao": 138, "cor": PALETA[3], "imagem": None},
    {"titulo": "Interestelar", "genero": "Ficção", "duracao": 169, "cor": PALETA[4], "imagem": None},
    {"titulo": "Duna: Parte 2", "genero": "Ficção", "duracao": 166, "cor": PALETA[5], "imagem": None},
    {"titulo": "Divertida Mente 2", "genero": "Animação", "duracao": 96, "cor": PALETA[6], "imagem": None},
    {"titulo": "Barbie", "genero": "Comédia", "duracao": 114, "cor": PALETA[7], "imagem": None},
]

SESSOES_DEMO = [
    {"filme": "Avatar", "horario": "14:00", "sala": "1", "preco": 10.0, "lugares": 5},
    {"filme": "Titanic", "horario": "16:30", "sala": "2", "preco": 10.0, "lugares": 4},
    {"filme": "Duna: Parte 2", "horario": "19:00", "sala": "3", "preco": 10.0, "lugares": 6},
    {"filme": "Barbie", "horario": "21:30", "sala": "2", "preco": 10.0, "lugares": 3},
]

CLIENTES_DEMO = [
    {"nome": "Ana", "email": "ana@email.com", "ingressos": 4, "gasto": 120.0},
    {"nome": "Bruno", "email": "bruno@email.com", "ingressos": 2, "gasto": 50.0},
    {"nome": "Carla", "email": "carla@email.com", "ingressos": 0, "gasto": 0.0},
]

# (filme, ingressos, faturamento)
RELATORIO_DEMO = [("Avatar", 5, 150.0), ("Barbie", 2, 56.0), ("Titanic", 1, 25.0)]

CADEIRAS_OCUPADAS_DEMO = {"A3", "A5", "B7", "C5", "C6", "D1", "E8", "E9", "F2", "G5", "G6", "H9"}
