"""Tela 5 - Clientes."""
import tkinter as tk
from tkinter import messagebox

from componentes import (Tela, Botao, campo_texto, campo_com_rotulo,
                         criar_tabela, preencher_tabela)
from tema import FUNDO, brl


class TelaClientes(Tela):
    def __init__(self, app):
        super().__init__(app)
        self.botao_menu()
        self.cabecalho("Clientes")

        formulario = tk.Frame(self, bg=FUNDO)
        formulario.pack(fill="x", padx=26)
        formulario.columnconfigure((0, 1), weight=1, uniform="col")
        self.campo_nome = campo_com_rotulo(formulario, "Nome", campo_texto, 0, 0)
        self.campo_email = campo_com_rotulo(formulario, "E-mail", campo_texto, 0, 1)
        Botao(self, "Adicionar", self.ao_adicionar).pack(fill="x", padx=32, pady=(14, 0))

        self.tabela = criar_tabela(self, [("Nome", 200, "w"), ("E-mail", 280, "w"),
                                          ("Ingressos", 100, "w"), ("Total gasto", 140, "w")])
        self.tabela.pack(fill="both", expand=True, padx=32, pady=(18, 8))

    def ao_adicionar(self):
        nome = self.campo_nome.get().strip()
        email = self.campo_email.get().strip()
        if not nome or not email:
            messagebox.showwarning("Clientes", "Preencha nome e e-mail.")
            return
        # TODO(backend): salvar no banco
        self.app.adicionar_cliente({"nome": nome, "email": email, "ingressos": 0, "gasto": 0.0})
        self.campo_nome.delete(0, "end")
        self.campo_email.delete(0, "end")

    def atualizar(self):
        preencher_tabela(self.tabela, [
            (c["nome"], c["email"], c["ingressos"], brl(c["gasto"]))
            for c in self.app.clientes])
