"""Tela 7 - Relatório de vendas (janela)."""
import tkinter as tk

from componentes import Botao, criar_tabela, preencher_tabela, centralizar_sobre
from dados_demo import RELATORIO_DEMO
from tema import FUNDO, DESTAQUE, brl


class JanelaRelatorio(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app, bg=FUNDO)
        self.title("Relatório de vendas")
        self.geometry("560x400")
        self.transient(app)

        tk.Label(self, text="Relatório de vendas", bg=FUNDO, fg=DESTAQUE,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=28, pady=(24, 12))
        tabela = criar_tabela(self, [("Filme", 240, "w"), ("Ingressos", 100, "w"),
                                     ("Faturamento", 140, "w")])
        tabela.pack(fill="both", expand=True, padx=28)
        # TODO(backend): agregar ingressos por filme
        preencher_tabela(tabela, [(filme, qtd, brl(valor)) for filme, qtd, valor in RELATORIO_DEMO])
        Botao(self, "Exportar CSV", self.ao_exportar).pack(pady=18)
        centralizar_sobre(self, app)

    def ao_exportar(self):
        # TODO(backend): gravar o CSV (módulo csv + filedialog.asksaveasfilename)
        pass
