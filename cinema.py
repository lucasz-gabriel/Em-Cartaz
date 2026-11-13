import tkinter as tk
from tkinter import ttk, messagebox

import os
import threading

import pandas as pd
from PIL import Image, ImageTk

import catalogo

filmes_titulo = []
filmes_genero = []
filmes_duracao = []  # minutos
filmes_poster = []  

# cada sessão aponta para um filme pelo índice
sessoes_filme = []
sessoes_horario = []
sessoes_sala = []
sessoes_preco = []
sessoes_vagas = []

clientes_nome = []
clientes_email = []

# cada venda aponta para um cliente e uma sessão
ing_cliente = []
ing_sessao = []
ing_qtd = []
ing_total = []


def reais(v):
    return "R$ " + f"{v:.2f}".replace(".", ",")


def desc_sessao(s):
    return f"{filmes_titulo[sessoes_filme[s]]} - {sessoes_horario[s]} - Sala {sessoes_sala[s]}"

def relatorio_df():
    if not ing_sessao:
        return None
    df = pd.DataFrame({
        "filme":[filmes_titulo[sessoes_filme[s]] for s in ing_sessao],
        "ingresso":ing_qtd,
        "total":ing_total,
    })
    return (df.groupby("filme", as_index=False)
            .agg(ingressos=("ingresso", "sum"), total=("total", "sum"))
            .sort_values("faturamento", ascending=False))


#BASE DAS TELAS

class Tela(tk.Frame):
    def __init__(self, app):
        super().__init__(app, padx=15, pady=15)
        self.app = app
 
    def titulo(self, texto):
        tk.Label(self, text=texto, font=("Arial", 16, "bold")).pack(pady=(0, 10))
 
    def voltar(self):
        tk.Button(self, text="← Menu", command=lambda: self.app.mostrar("Menu")).pack(side="bottom", pady=8)
 
    def tabela(self, colunas, largura=110, pai=None):
        t = ttk.Treeview(pai or self, columns=colunas, show="headings", height=7)
        for c in colunas:
            t.heading(c, text=c)
            t.column(c, width=largura)
        t.pack(fill="both", expand=True, pady=8)
        return t
 
    def campo(self, frame, rotulo, linha):
        tk.Label(frame, text=rotulo).grid(row=linha, column=0, sticky="e", padx=4, pady=2)
        e = tk.Entry(frame, width=22)
        e.grid(row=linha, column=1, pady=2)
        return e
 
    def atualizar(self):
        pass
 
 
#TELA 1: MENU
class Menu(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.titulo("🎬 Cinema")
        for nome, destino in [("Filmes", "Filmes"), ("Sessões", "Sessoes"),
                              ("Clientes", "Clientes"), ("Vender ingresso", "Vendas")]:
            tk.Button(self, text=nome, width=28, pady=6,
                      command=lambda d=destino: app.mostrar(d)).pack(pady=4)
        self.resumo = tk.Label(self, fg="gray")
        self.resumo.pack(pady=12)
        self.lbl.status = tk.Label(self, text="", fg="gray")
        self.lbl.status.pack()
 
    def atualizar(self):
        self.lbl.status.config(text=self.app.title())
        self.resumo.config(text=f"{len(filmes_titulo)} filmes | {len(sessoes_filme)} sessões | "
                                f"{len(clientes_nome)} clientes | {sum(ing_qtd)} ingressos vendidos")




class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Cinema")
        self.geometry("580x500")
        self.telas = {}
        for nome, cls in [("Menu", Menu), ("Filmes",Filmes), ("Sessoes", Sessoes)]:
            t = cls(self)
            t.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.telas[nome] = t
        self.mostrar("Menu")
 
    def mostrar(self, nome):
        t = self.telas[nome]
        t.atualizar()
        t.tkraise()


if __name__ == "__main__":
    App().mainloop()
