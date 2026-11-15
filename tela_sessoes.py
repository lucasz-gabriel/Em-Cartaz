"""Tela 4 - Sessões."""
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import (Tela, Botao, campo_texto, campo_com_rotulo,
                         criar_tabela, preencher_tabela)
from tema import FUNDO, brl


class TelaSessoes(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.botao_menu()
        self.cabecalho("Sessões")

        formulario = tk.Frame(self, bg=FUNDO)
        formulario.pack(fill="x", padx=26)
        formulario.columnconfigure((0, 1), weight=1, uniform="col")
        self.combo_filme = campo_com_rotulo(
            formulario, "Filme", lambda p: ttk.Combobox(p, state="readonly"), 0, 0)
        self.combo_filme.set("Selecione...")
        self.campo_sala = campo_com_rotulo(formulario, "Sala", campo_texto, 0, 1)
        self.campo_horario = campo_com_rotulo(formulario, "Horário", campo_texto, 1, 0)
        self.campo_horario.insert(0, "19:00")
        self.campo_preco = campo_com_rotulo(formulario, "Preço", campo_texto, 1, 1)
        self.campo_lugares = campo_com_rotulo(formulario, "Lugares", campo_texto, 2, 0)
        Botao(formulario, "Adicionar", self.ao_adicionar).grid(
            row=2, column=1, sticky="sew", padx=6, pady=4)

        self.tabela = criar_tabela(self, [("Filme", 260, "w"), ("Horário", 100, "w"),
                                          ("Sala", 80, "w"), ("Preço", 120, "w"),
                                          ("Vagas", 80, "w")])
        self.tabela.pack(fill="both", expand=True, padx=32, pady=(18, 8))

    def ao_adicionar(self):
        filme = self.combo_filme.get()
        if filme not in [f["titulo"] for f in self.app.filmes]:
            messagebox.showwarning("Sessões", "Selecione um filme.")
            return
        try:
            preco = float(self.campo_preco.get().replace(",", "."))
            lugares = int(self.campo_lugares.get())
        except ValueError:
            messagebox.showwarning("Sessões", "Preço e lugares precisam ser números.")
            return
        # TODO(backend): validar horário/sala e salvar no banco
        self.app.adicionar_sessao({
            "filme": filme,
            "horario": self.campo_horario.get().strip(),
            "sala": self.campo_sala.get().strip(),
            "preco": preco,
            "lugares": lugares,
        })

    def atualizar(self):
        self.combo_filme["values"] = [f["titulo"] for f in self.app.filmes]
        preencher_tabela(self.tabela, [
            (s["filme"], s["horario"], s["sala"], brl(s["preco"]), s["lugares"])
            for s in self.app.sessoes])
