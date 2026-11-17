"""Tela 2 - Em cartaz (catálogo)."""
import unicodedata
import tkinter as tk
from tkinter import ttk, messagebox

from componentes import Tela, Botao, campo_texto
from janela_novo_filme import JanelaNovoFilme
from tema import FUNDO, TEXTO, TEXTO_SUAVE, FONTE, FONTE_NEGRITO, FONTE_PEQUENA, CADEIRA_OCUPADA

try:
    from PIL import Image, ImageOps, ImageTk
except ImportError:            # sem Pillow os cartões mostram só o placeholder "Pôster"
    Image = None

_cache_posters = {}            # caminho -> ((largura, altura), PhotoImage)

def facilitador(texto):
    #Sempre que o usuário buscar algum filme mesmo que sem acento ou em maiusculo o programa deve encontrar.
    return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                   if unicodedata.category(c) != "Mn")

def carregar_poster(caminho, largura, altura):
    """PhotoImage do pôster, recortado e redimensionado para o cartão (com cache)."""
    guardado = _cache_posters.get(caminho)
    if guardado and guardado[0] == (largura, altura):
        return guardado[1]
    with Image.open(caminho) as original:
        imagem = ImageOps.fit(original.convert("RGB"), (largura, altura),
                              getattr(Image, "Resampling", Image).LANCZOS)
    foto = ImageTk.PhotoImage(imagem)
    _cache_posters[caminho] = ((largura, altura), foto)
    return foto


class CartaoPoster(tk.Frame):
    PROPORCAO = 215 / 150          # altura / largura do pôster

    def __init__(self, pai, filme, largura, ao_remover=None):
        super().__init__(pai, bg=FUNDO)
        altura = round(largura * self.PROPORCAO)
        quadro = tk.Canvas(self, width=largura, height=altura, bg=filme["cor"],
                           highlightthickness=0)
        quadro.pack()
        foto = None
        caminho = filme.get("imagem")              # caminho do arquivo em posters/ (ou None)
        if caminho and Image is not None:
            try:
                foto = carregar_poster(caminho, largura, altura)
            except (OSError, ValueError):          # arquivo sumiu ou não é uma imagem
                foto = None
        if foto is not None:
            quadro.create_image(0, 0, image=foto, anchor="nw")
            quadro.imagem = foto                   # evita o garbage collector
        else:
            quadro.create_text(largura / 2, altura / 2, text="Pôster", fill=TEXTO, font=FONTE)
        tk.Label(self, text=filme["titulo"], bg=FUNDO, fg=TEXTO, font=FONTE_NEGRITO,
                 anchor="w", justify="left", wraplength=largura).pack(fill="x", pady=(6, 0))
        tk.Label(self, text=f'{filme["genero"]} • {filme["duracao"]} min', bg=FUNDO,
                 fg=TEXTO_SUAVE, font=FONTE_PEQUENA, anchor="w", justify="left",
                 wraplength=largura).pack(fill="x")
        if ao_remover:
            remover = tk.Label(self, text="Remover", bg=FUNDO, fg=TEXTO_SUAVE,font=FONTE_PEQUENA, cursor="hand2", anchor="w")
            remover.pack(fill="x", pady=(2, 0))
            remover.bind("<Enter>", lambda e: remover.config(fg=CADEIRA_OCUPADA))
            remover.bind("<Leave>", lambda e: remover.config(fg=TEXTO_SUAVE))
            remover.bind("<Button-1>", lambda e: ao_remover(filme))


class TelaCatalogo(Tela):
    LARGURA_ALVO, LARGURA_MIN, LARGURA_MAX = 160, 130, 190
    ESPACO = 14                    

    def __init__(self, app):
        super().__init__(app)
        self._largura = 0        
        self._pendente = None      #redimensionamento

        self.botao_menu()
        barra = self.cabecalho("Em cartaz")
        Botao(barra, "+ Adicionar filme", lambda: JanelaNovoFilme(app)).pack(side="right")
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *_: self.atualizar())
        campo_texto(barra, width=22, textvariable=self.var_busca).pack(side="right", padx=(0,12), ipady=5)
        tk.Label(barra, text="Buscar", bg=FUNDO, fg=TEXTO_SUAVE,
                 font=FONTE_PEQUENA).pack(side="right", padx=(0,6))


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
        self.canvas.itemconfigure(self.janela, width=e.width)
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
        if self._largura < 50:
            return
        colunas, largura_cartao = self._calcular_layout(self._largura)
        for w in self.grade.winfo_children():
            w.destroy()
        termo = facilitador(self.var_busca.get().strip())
        filmes = [f for f in self.app.filmes if termo in facilitador(f["titulo"])]
        if not filmes:
            texto = (f'Nenhum filme encontrado para "{self.var_busca.get().strip()}".'
                     if termo else "Nenhum filme cadastrado.")
            tk.Label(self.grade, text=texto, bg=FUNDO, fg=TEXTO_SUAVE,
                     font=FONTE).pack(pady=40)
            return
        for inicio in range(0, len(filmes), colunas):
            linha = tk.Frame(self.grade, bg=FUNDO)
            linha.pack(pady=self.ESPACO)
            for filme in filmes[inicio:inicio + colunas]:
                CartaoPoster(linha, filme, largura_cartao, self._remover).pack(
                    side="left", padx=self.ESPACO, anchor="n")

    #rolagem com a roda do mouse
    def _ligar_roda(self, ligar):
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            if ligar:
                self.canvas.bind_all(evento, self._roda)
            else:
                self.canvas.unbind_all(evento)

    def _roda(self, e):
        passo = -1 if (e.num == 4 or e.delta > 0) else 1
        self.canvas.yview_scroll(passo, "units")

    #Remover filmes ja cadastrador
    def _remover(self, filme):
        if messagebox.askyesno(
                "Remover filme",
                f'Remover "{filme["titulo"]}"?\nAs sessões desse filme também serão removidas.'):
            self.app.remover_filme(filme["titulo"])