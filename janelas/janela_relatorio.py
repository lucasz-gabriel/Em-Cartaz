
"""Tela 7 - Relatório de vendas (janela): pandas lendo do banco + exportar CSV."""
import tkinter as tk
from tkinter import filedialog, messagebox
 
from componentes import Botao, criar_tabela, preencher_tabela, centralizar_sobre
from database import repositorio
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
 
        self.df = repositorio.relatorio_df()          # DataFrame do pandas, lido do banco
        preencher_tabela(tabela, [(l.filme, l.ingressos, brl(l.faturamento))
                                  for l in self.df.itertuples()])
        Botao(self, "Exportar CSV", self.ao_exportar).pack(pady=18)
        centralizar_sobre(self, app)
 
    def ao_exportar(self):
        if self.df.empty:
            messagebox.showinfo("Relatório", "Ainda não há vendas para exportar.", parent=self)
            return
        caminho = filedialog.asksaveasfilename(
            parent=self, defaultextension=".csv", initialfile="relatorio_vendas.csv",
            filetypes=[("CSV (abre no Excel)", "*.csv")])
        if not caminho:                               # cancelou
            return
        self.df.to_csv(caminho, index=False, sep=";", encoding="utf-8-sig")
        messagebox.showinfo("Relatório", "Arquivo salvo!", parent=self)
 