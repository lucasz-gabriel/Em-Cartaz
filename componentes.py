"""Componentes reutilizáveis: botão, campo de texto, tabela e a classe base das telas."""
import tkinter as tk
from tkinter import ttk

from tema import (FUNDO, SUPERFICIE, BORDA, DESTAQUE, DESTAQUE_HOVER, TEXTO,
                  TEXTO_SUAVE, FONTE, FONTE_NEGRITO, FONTE_PEQUENA, FONTE_TITULO)


class Botao(tk.Label):
    """Botão feito com Label (as cores funcionam em qualquer sistema)."""

    def __init__(self, pai, texto, comando=None, contorno=False, **kw):
        base = pai["bg"] if contorno else DESTAQUE
        hover = BORDA if contorno else DESTAQUE_HOVER
        super().__init__(pai, text=texto, bg=base, fg=DESTAQUE if contorno else FUNDO,
                         font=FONTE_NEGRITO, cursor="hand2", padx=14, pady=7,
                         highlightthickness=1 if contorno else 0,
                         highlightbackground=DESTAQUE, **kw)
        self._base, self._hover, self._comando = base, hover, comando
        self.bind("<Enter>", lambda e: self.config(bg=self._hover))
        self.bind("<Leave>", lambda e: self.config(bg=self._base))
        self.bind("<Button-1>", lambda e: self._comando() if self._comando else None)


def campo_texto(pai, bg=SUPERFICIE, **kw):
    return tk.Entry(pai, bg=bg, fg=TEXTO, insertbackground=TEXTO, relief="flat",
                    font=FONTE, highlightthickness=1, highlightbackground=BORDA,
                    highlightcolor=DESTAQUE, **kw)


def campo_com_rotulo(pai, texto, criar_widget, linha, coluna):
    """Rótulo pequeno + campo, posicionado em um grid."""
    caixa = tk.Frame(pai, bg=pai["bg"])
    caixa.grid(row=linha, column=coluna, sticky="ew", padx=6, pady=4)
    tk.Label(caixa, text=texto, bg=pai["bg"], fg=TEXTO_SUAVE, font=FONTE_PEQUENA,
             anchor="w").pack(fill="x")
    widget = criar_widget(caixa)
    widget.pack(fill="x", ipady=5)
    return widget


def criar_tabela(pai, colunas):
    """colunas: lista de (nome, largura, alinhamento)."""
    tabela = ttk.Treeview(pai, columns=[c[0] for c in colunas], show="headings",
                          selectmode="browse")
    for nome, largura, alinhamento in colunas:
        tabela.heading(nome, text=nome, anchor="w")
        tabela.column(nome, width=largura, anchor=alinhamento, stretch=True)
    tabela.tag_configure("impar", background="#1A1A1A")
    tabela.tag_configure("par", background=SUPERFICIE)
    return tabela


def preencher_tabela(tabela, linhas):
    tabela.delete(*tabela.get_children())
    for i, linha in enumerate(linhas):
        tabela.insert("", "end", values=linha, tags=("par" if i % 2 else "impar",))


def centralizar_sobre(janela, pai):
    janela.update_idletasks()
    x = pai.winfo_rootx() + (pai.winfo_width() - janela.winfo_width()) // 2
    y = pai.winfo_rooty() + (pai.winfo_height() - janela.winfo_height()) // 2
    janela.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class Tela(tk.Frame):
    """Base das telas: guarda o app e traz helpers de cabeçalho e rodapé."""

    def __init__(self, app):
        super().__init__(app.conteiner, bg=FUNDO)
        self.app = app

    def cabecalho(self, texto):
        barra = tk.Frame(self, bg=FUNDO)
        barra.pack(fill="x", padx=32, pady=(28, 12))
        tk.Label(barra, text=texto, bg=FUNDO, fg=DESTAQUE, font=FONTE_TITULO).pack(side="left")
        return barra

    def botao_menu(self):
        # chamar ANTES dos widgets que expandem, para reservar o rodapé
        Botao(self, "← Menu", lambda: self.app.mostrar("menu"), contorno=True).pack(side="bottom", pady=18)

    def atualizar(self):
        pass
