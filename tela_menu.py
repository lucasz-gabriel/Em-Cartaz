"""Tela 1 - Menu."""
import tkinter as tk

from componentes import Tela, Botao
from tema import FUNDO, DESTAQUE, TEXTO_SUAVE, FONTE_PEQUENA


class TelaMenu(Tela):
    def __init__(self, app):
        super().__init__(app)
        caixa = tk.Frame(self, bg=FUNDO)
        caixa.place(relx=0.5, rely=0.45, anchor="center")
        tk.Label(caixa, text="Cinema", bg=FUNDO, fg=DESTAQUE,
                 font=("Segoe UI", 32, "bold")).pack(pady=(0, 28))
        for texto, destino in [("Filmes", "catalogo"), ("Sessões", "sessoes"),
                               ("Clientes", "clientes"), ("Comprar ingresso", "ingressos")]:
            Botao(caixa, texto, lambda d=destino: app.mostrar(d), width=30).pack(pady=7)
        self.estatisticas = tk.Label(caixa, bg=FUNDO, fg=TEXTO_SUAVE, font=FONTE_PEQUENA,
                                     justify="center")
        self.estatisticas.pack(pady=(28, 0))

    def atualizar(self):
        a = self.app
        self.estatisticas.config(text=(
            f"{len(a.filmes)} filmes | {len(a.sessoes)} sessões | "
            f"{len(a.clientes)} clientes | {a.ingressos_vendidos} ingressos vendidos\n"
            f"{a.carregados_da_web} filmes carregados da web"))
