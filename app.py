"""Cinema - interface gráfica (Tkinter).

Só UI: dados de exemplo em memória, sem scraper e sem banco.
Pontos para ligar o backend estão marcados com TODO(backend).
Rodar: python app.py
"""
import tkinter as tk
from tkinter import ttk

from dados_demo import FILMES_DEMO, SESSOES_DEMO, CLIENTES_DEMO
from tela_catalogo import TelaCatalogo
from tela_clientes import TelaClientes
from tela_ingressos import TelaIngressos
from tela_menu import TelaMenu
from tela_sessoes import TelaSessoes
from tema import (FUNDO, SUPERFICIE, BORDA, DESTAQUE, TEXTO, FONTE, FONTE_NEGRITO)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cinema")
        self.geometry("960x720")
        self.minsize(900, 680)
        self.configure(bg=FUNDO)
        self._configurar_estilo()

        # estado em memória (trocar por banco depois)
        self.filmes = [dict(f) for f in FILMES_DEMO]
        self.sessoes = [dict(s) for s in SESSOES_DEMO]
        self.clientes = [dict(c) for c in CLIENTES_DEMO]
        self.ingressos_vendidos = 0
        self.carregados_da_web = len(FILMES_DEMO)

        self.conteiner = tk.Frame(self, bg=FUNDO)
        self.conteiner.pack(fill="both", expand=True)
        self.conteiner.rowconfigure(0, weight=1)
        self.conteiner.columnconfigure(0, weight=1)

        self.telas = {
            "menu": TelaMenu(self),
            "catalogo": TelaCatalogo(self),
            "sessoes": TelaSessoes(self),
            "clientes": TelaClientes(self),
            "ingressos": TelaIngressos(self),
        }
        for tela in self.telas.values():
            tela.grid(row=0, column=0, sticky="nsew")
        self.atualizar_tudo()
        self.mostrar("menu")

    def _configurar_estilo(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE,
                         foreground=TEXTO, rowheight=30, borderwidth=0, font=FONTE)
        estilo.configure("Treeview.Heading", background=BORDA, foreground=DESTAQUE,
                         font=FONTE_NEGRITO, relief="flat", padding=6)
        estilo.map("Treeview", background=[("selected", BORDA)],
                   foreground=[("selected", TEXTO)])
        estilo.map("Treeview.Heading", background=[("active", BORDA)])
        estilo.configure("TCombobox", fieldbackground=SUPERFICIE, background=BORDA,
                         foreground=TEXTO, arrowcolor=DESTAQUE, bordercolor=BORDA,
                         lightcolor=SUPERFICIE, darkcolor=SUPERFICIE, padding=4)
        estilo.map("TCombobox", fieldbackground=[("readonly", SUPERFICIE)],
                   foreground=[("readonly", TEXTO)],
                   selectbackground=[("readonly", SUPERFICIE)],
                   selectforeground=[("readonly", TEXTO)])
        estilo.configure("Vertical.TScrollbar", background=BORDA, troughcolor=FUNDO,
                         bordercolor=FUNDO, arrowcolor=DESTAQUE, lightcolor=BORDA,
                         darkcolor=BORDA)
        self.option_add("*TCombobox*Listbox.background", SUPERFICIE)
        self.option_add("*TCombobox*Listbox.foreground", TEXTO)
        self.option_add("*TCombobox*Listbox.selectBackground", DESTAQUE)
        self.option_add("*TCombobox*Listbox.selectForeground", FUNDO)
        self.option_add("*TCombobox*Listbox.font", FONTE)

    def mostrar(self, nome):
        self.telas[nome].tkraise()

    def atualizar_tudo(self):
        for tela in self.telas.values():
            tela.atualizar()

    # TODO(backend): estes métodos viram chamadas ao banco
    def adicionar_filme(self, filme):
        self.filmes.append(filme)
        self.atualizar_tudo()

    def adicionar_sessao(self, sessao):
        self.sessoes.append(sessao)
        self.atualizar_tudo()

    def adicionar_cliente(self, cliente):
        self.clientes.append(cliente)
        self.atualizar_tudo()


if __name__ == "__main__":
    App().mainloop()
