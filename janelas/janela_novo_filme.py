"""Tela 3 - Adicionar filme (janela)."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox

from componentes import Botao, campo_texto, centralizar_sobre
from raspador import buscar_poster, ErroBusca
from tema import SUPERFICIE, FUNDO, DESTAQUE, TEXTO_SUAVE, FONTE_PEQUENA, PALETA


class JanelaNovoFilme(tk.Toplevel):
    def __init__(self, app):
        super().__init__(app, bg=SUPERFICIE)
        self.app = app
        self.title("Novo filme")
        self.resizable(False, False)
        self.transient(app)

        self._fila = queue.Queue()     # a thread da busca entrega o resultado por aqui
        self._tarefa = None            # id do after() que fica olhando a fila
        self._buscando = False
        self._busca = None             # última busca: {"titulo": ..., "poster": caminho}

        corpo = tk.Frame(self, bg=SUPERFICIE, padx=28, pady=22)
        corpo.pack()
        tk.Label(corpo, text="Novo filme", bg=SUPERFICIE, fg=DESTAQUE,
                 font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 10))

        tk.Label(corpo, text="Título", bg=SUPERFICIE, fg=TEXTO_SUAVE,
                 font=FONTE_PEQUENA).pack(anchor="w")
        linha = tk.Frame(corpo, bg=SUPERFICIE)
        linha.pack(fill="x", pady=(0, 8))
        self.campo_titulo = campo_texto(linha, bg=FUNDO, width=24)
        self.campo_titulo.pack(side="left", fill="x", expand=True, ipady=5)
        self.campo_titulo.bind("<Return>", self.ao_buscar)        # Enter também busca
        self.botao_buscar = Botao(linha, "Buscar pôster", self.ao_buscar, contorno=True)
        self.botao_buscar.pack(side="left", padx=(8, 0))

        self.campo_genero = self._campo(corpo, "Gênero")
        self.campo_duracao = self._campo(corpo, "Duração (min)")
        self.status = tk.Label(corpo, text="Digite o título e clique em Buscar pôster.",
                               bg=SUPERFICIE, fg=TEXTO_SUAVE, font=FONTE_PEQUENA,
                               wraplength=320, justify="left", anchor="w")
        self.status.pack(fill="x", pady=(2, 0))
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

    def destroy(self):
        if self._tarefa:                     # evita callback do after() em janela já fechada
            self.after_cancel(self._tarefa)
        super().destroy()

    # --- busca do pôster na Wikipédia (em outra thread, para a janela não travar)
    def ao_buscar(self, _evento=None):
        titulo = self.campo_titulo.get().strip()
        if not titulo:
            self.status.config(text="Digite o título primeiro.")
            return
        if self._buscando:
            return
        self._buscando = True
        self.botao_buscar.config(text="Buscando…")
        self.status.config(text="Buscando na Wikipédia…")
        threading.Thread(target=self._trabalhar, args=(titulo,), daemon=True).start()
        self._tarefa = self.after(100, self._checar_fila)

    def _trabalhar(self, titulo):
        """Roda na thread: NÃO mexe em widgets, só devolve o resultado pela fila."""
        try:
            self._fila.put(("ok", titulo, buscar_poster(titulo)))
        except ErroBusca as erro:
            self._fila.put(("erro", titulo, str(erro)))
        except Exception as erro:             # imprevisto não pode deixar o botão travado
            self._fila.put(("erro", titulo, f"Erro inesperado: {erro}"))

    def _checar_fila(self):
        """Roda na thread principal: confere se a busca terminou."""
        try:
            situacao, titulo, resultado = self._fila.get_nowait()
        except queue.Empty:
            self._tarefa = self.after(100, self._checar_fila)
            return
        self._tarefa = None
        self._buscando = False
        self.botao_buscar.config(text="Buscar pôster")
        if situacao == "erro":
            self.status.config(text=resultado)
            return
        self._busca = {"titulo": titulo, "poster": resultado["poster"]}
        self.status.config(text=f'Pôster encontrado em: {resultado["pagina"]}. '
                                "Confira se é o filme certo.")

    def ao_salvar(self):
        titulo = self.campo_titulo.get().strip()
        if not titulo:
            messagebox.showwarning("Novo filme", "Informe o título.", parent=self)
            return
        poster = None                          # só usa o pôster se o título não mudou depois da busca
        if self._busca and self._busca["titulo"] == titulo:
            poster = self._busca["poster"]
        # TODO(backend): salvar no banco
        self.app.adicionar_filme({
            "titulo": titulo,
            "genero": self.campo_genero.get().strip() or "—",
            "duracao": self.campo_duracao.get().strip() or "?",
            "cor": PALETA[len(self.app.filmes) % len(PALETA)],
            "imagem": poster,                  # caminho do arquivo em posters/ (ou None)
        })
        self.destroy()