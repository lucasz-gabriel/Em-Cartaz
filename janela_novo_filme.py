"""Tela 3 - Adicionar filme (janela)."""
import tkinter as tk
from tkinter import messagebox

from componentes import Botao, campo_texto, centralizar_sobre
from tema import SUPERFICIE, FUNDO, DESTAQUE, TEXTO_SUAVE, FONTE_PEQUENA, PALETA


class JanelaNovoFilme(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app, bg=SUPERFICIE)
        self.app = app
        self.title("Novo filme")
        self.resizable(False, False)
        self.transient(app)

        corpo = tk.Frame(self, bg=SUPERFICIE, padx=28, pady=22)
        corpo.pack()
        tk.Label(corpo, text="Novo filme", bg=SUPERFICIE, fg=DESTAQUE,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        tk.Label(corpo, text="Título", bg=SUPERFICIE, fg=TEXTO_SUAVE,
                 font=FONTE_PEQUENA).pack(anchor="w")
        linha = tk.Frame(corpo, bg=SUPERFICIE)
        linha.pack(fill="x", pady=(0, 8))
        self.campo_titulo = campo_texto(linha, bg=FUNDO, width=28)
        self.campo_titulo.pack(side="left", fill="x", expand=True, ipady=5)
        Botao(linha, "Buscar", self.ao_buscar, contorno=True).pack(side="left", padx=(8, 0))

        self.campo_genero = self._campo(corpo, "Gênero")
        self.campo_duracao = self._campo(corpo, "Duração (min)")
        Botao(corpo, "Salvar", self.ao_salvar).pack(pady=(14, 0))

        centralizar_sobre(self, app)
        self.grab_set()
        self.campo_titulo.focus()

    def _campo(self, pai, rotulo):
        tk.Label(pai, text=rotulo, bg=SUPERFICIE, fg=TEXTO_SUAVE,
                 font=FONTE_PEQUENA).pack(anchor="w")
        campo = campo_texto(pai, bg=FUNDO, width=36)
        campo.pack(fill="x", pady=(0, 8), ipady=5)
        return campo

    def preencher(self, genero, duracao):
        """Chamado com o resultado do scraper para autopreencher os campos."""
        for campo, valor in ((self.campo_genero, genero), (self.campo_duracao, duracao)):
            campo.delete(0, "end")
            campo.insert(0, str(valor))

    def ao_buscar(self):
        # TODO(backend): buscar self.campo_titulo.get() com o scraper e chamar self.preencher(...)
        pass

    def ao_salvar(self):
        titulo = self.campo_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Novo filme", "Informe o título.", parent=self)
            return
        # TODO(backend): salvar no banco / pôster baixado
        self.app.adicionar_filme({
            "titulo": titulo,
            "genero": self.campo_genero.get().strip() or "—",
            "duracao": self.campo_duracao.get().strip() or "?",
            "cor": PALETA[len(self.app.filmes) % len(PALETA)],
            "imagem": None,
        })
        self.destroy()
