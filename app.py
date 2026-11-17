"""Cinema - interface gráfica (Tkinter) com banco SQLite (SQLAlchemy).

Os dados ficam no cinema.db; as telas conversam só com o App, e o App com o repositorio.
Rodar: python app.py
"""
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from database import repositorio
from raspador import buscar_poster
from telas.tela_catalogo import TelaCatalogo
from telas.tela_clientes import TelaClientes
from telas.tela_ingressos import TelaIngressos
from telas.tela_menu import TelaMenu
from telas.tela_sessoes import TelaSessoes
from tema import (FUNDO, SUPERFICIE, BORDA, DESTAQUE, TEXTO, FONTE, FONTE_NEGRITO)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cinema")
        self.geometry("960x720")
        self.minsize(900, 680)
        self.configure(bg=FUNDO)
        self._configurar_estilo()

        #banco
        repositorio.criar_tabelas()
        repositorio.popular_se_vazio()
        self.filmes = repositorio.listar_filmes()
        self.sessoes = repositorio.listar_sessoes()
        self.clientes = repositorio.listar_clientes()
        self.ocupadas = repositorio.listar_ocupadas()
        self.ingressos_vendidos = repositorio.contar_ingressos()
        self.carregados_da_web = len(self.filmes)

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
        self._baixar_posters_demo()

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

    # ---------- banco: tudo passa por aqui
    def _recarregar(self):
        """Relê o estado do banco e redesenha todas as telas."""
        self.filmes = repositorio.listar_filmes()
        self.sessoes = repositorio.listar_sessoes()
        self.clientes = repositorio.listar_clientes()
        self.ocupadas = repositorio.listar_ocupadas()
        self.ingressos_vendidos = repositorio.contar_ingressos()
        self.atualizar_tudo()

    def _salvar(self, funcao, dados):
        try:
            funcao(dados)
        except ValueError as erro:           #evita duplicado, horário inválido
            messagebox.showwarning("Cinema", str(erro))
            return False
        self._recarregar()
        return True

    def adicionar_filme(self, filme):
        return self._salvar(repositorio.adicionar_filme, filme)

    def adicionar_sessao(self, sessao):
        return self._salvar(repositorio.adicionar_sessao, sessao)

    def adicionar_cliente(self, cliente):
        return self._salvar(repositorio.adicionar_cliente, cliente)

    def remover_filme(self, titulo):
        repositorio.remover_filme(titulo)    #apaga também as sessões e os ingressos dele
        self._recarregar()

    def comprar_ingressos(self, cliente_id, sessao_id, cadeiras):
        try:
            repositorio.registrar_compra(cliente_id, sessao_id, cadeiras)
        except ValueError as erro:
            messagebox.showwarning("Cinema", str(erro))
            self._recarregar()               #mostra as cadeiras que mudaram
            return False
        self._recarregar()
        return True

    # ---------- pôsteres dos filmes que ainda não têm imagem (em outra thread)
    def _baixar_posters_demo(self):
        pendentes = [f["titulo"] for f in self.filmes if not f.get("imagem")]
        if not pendentes:
            return
        self._fila_posters = queue.Queue()

        def tarefa():                       
            for titulo in pendentes:
                try:
                    self._fila_posters.put((titulo, buscar_poster(titulo)["poster"]))
                except Exception:            #sem internet ou filme não achado: segue sem pôster
                    pass
            self._fila_posters.put(None)     #sinal de fim

        threading.Thread(target=tarefa, daemon=True).start()
        self.after(300, self._checar_posters)

    def _checar_posters(self):
        terminou, mudou = False, False
        try:
            while True:
                item = self._fila_posters.get_nowait()
                if item is None:
                    terminou = True
                    break
                titulo, caminho = item
                for f in self.filmes:
                    if f["titulo"] == titulo:
                        f["imagem"] = caminho
                        mudou = True
                repositorio.atualizar_imagem(titulo, caminho)   #grava o caminho no banco
        except queue.Empty:
            pass
        if mudou:
            self.telas["catalogo"].atualizar()
        if not terminou:
            self.after(500, self._checar_posters)


if __name__ == "__main__":
    App().mainloop()