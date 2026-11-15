"""Tela 2 - Em cartaz (catálogo)."""
import tkinter as tk
from tkinter import ttk

from componentes import Tela, Botao
from janela_novo_filme import JanelaNovoFilme
from tema import FUNDO, TEXTO, TEXTO_SUAVE, FONTE, FONTE_NEGRITO, FONTE_PEQUENA


class CartaoPoster(tk.Frame):
    PROPORCAO = 215 / 150          # altura / largura do pôster

    def __init__(self, pai, filme, largura):
        super().__init__(pai, bg=FUNDO)
        altura = round(largura * self.PROPORCAO)
        quadro = tk.Canvas(self, width=largura, height=altura, bg=filme["cor"],
                           highlightthickness=0)
        quadro.pack()
        if filme.get("imagem") is not None:       # PhotoImage do pôster (futuro)
            quadro.create_image(largura / 2, altura / 2, image=filme["imagem"], anchor="center")
            quadro.imagem = filme["imagem"]        # evita o garbage collector
        else:
            quadro.create_text(largura / 2, altura / 2, text="Pôster", fill=TEXTO, font=FONTE)
        tk.Label(self, text=filme["titulo"], bg=FUNDO, fg=TEXTO, font=FONTE_NEGRITO,
                 anchor="w", justify="left", wraplength=largura).pack(fill="x", pady=(6, 0))
        tk.Label(self, text=f'{filme["genero"]} • {filme["duracao"]} min', bg=FUNDO,
                 fg=TEXTO_SUAVE, font=FONTE_PEQUENA, anchor="w").pack(fill="x")


class TelaCatalogo(Tela):
    # tamanho do cartão: tenta chegar perto do ALVO e nunca sai de [MIN, MAX]
    LARGURA_ALVO, LARGURA_MIN, LARGURA_MAX = 160, 130, 190
    ESPACO = 14                    # folga de cada lado de um cartão

    def __init__(self, app):
        super().__init__(app)
        self._largura = 0          # largura atual da área do catálogo
        self._pendente = None      # redesenho agendado (debounce do redimensionamento)

        self.botao_menu()
        barra = self.cabecalho("Em cartaz")
        Botao(barra, "+ Adicionar filme", lambda: JanelaNovoFilme(app)).pack(side="right")

        corpo = tk.Frame(self, bg=FUNDO)
        corpo.pack(fill="both", expand=True, padx=32)
        self.canvas = tk.Canvas(corpo, bg=FUNDO, highlightthickness=0)
        barra_rolagem = ttk.Scrollbar(corpo, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=barra_rolagem.set)
        barra_rolagem.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.grade = tk.Frame(self.canvas, bg=FUNDO)
        self.janela = self.canvas.create_window((0, 0), window=self.grade, anchor="nw")
        self.grade.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._ao_redimensionar)
        self.canvas.bind("<Enter>", lambda e: self._ligar_roda(True))
        self.canvas.bind("<Leave>", lambda e: self._ligar_roda(False))

    # --- layout responsivo
    def _ao_redimensionar(self, e):
        self.canvas.itemconfigure(self.janela, width=e.width)   # a grade ocupa toda a largura
        if e.width != self._largura:
            self._largura = e.width
            if self._pendente:
                self.after_cancel(self._pendente)
            self._pendente = self.after(120, self.atualizar)

    def _calcular_layout(self, largura_total):
        """Devolve (colunas, largura do cartão) para a largura disponível."""
        colunas = max(1, largura_total // (self.LARGURA_ALVO + 2 * self.ESPACO))
        largura = (largura_total - 2 * self.ESPACO * colunas) // colunas
        return colunas, max(self.LARGURA_MIN, min(self.LARGURA_MAX, largura))

    def atualizar(self):
        self._pendente = None
        if self._largura < 50:     # ainda sem tamanho: o primeiro <Configure> redesenha
            return
        colunas, largura_cartao = self._calcular_layout(self._largura)
        for w in self.grade.winfo_children():
            w.destroy()
        filmes = self.app.filmes
        for inicio in range(0, len(filmes), colunas):
            linha = tk.Frame(self.grade, bg=FUNDO)
            linha.pack(pady=self.ESPACO)          # cada linha fica centralizada
            for filme in filmes[inicio:inicio + colunas]:
                CartaoPoster(linha, filme, largura_cartao).pack(
                    side="left", padx=self.ESPACO, anchor="n")

    # --- rolagem com a roda do mouse
    def _ligar_roda(self, ligar):
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            if ligar:
                self.canvas.bind_all(evento, self._roda)
            else:
                self.canvas.unbind_all(evento)

    def _roda(self, e):
        passo = -1 if (e.num == 4 or e.delta > 0) else 1
        self.canvas.yview_scroll(passo, "units")