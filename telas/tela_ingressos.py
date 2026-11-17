"""Tela 6 - Comprar ingresso (escolha de cadeiras)."""
import tkinter as tk
from tkinter import ttk, messagebox
from types import SimpleNamespace

from componentes import Tela, Botao, campo_com_rotulo
from dados_demo import CADEIRAS_OCUPADAS_DEMO
from janelas.janela_relatorio import JanelaRelatorio
from tema import (FUNDO, DESTAQUE, TEXTO, TEXTO_SUAVE, FONTE_NEGRITO, FONTE_PEQUENA,
                  CADEIRA_LIVRE, CADEIRA_OCUPADA, brl)


class TelaIngressos(Tela):
    FILEIRAS, COLUNAS = "ABCDEFGH", 10
    PRECO_PADRAO=30.0
    # proporções do mapa em relação ao tamanho da cadeira (t)
    ESPACO_REL, CORREDOR_REL, MARGEM_REL, TOPO_REL = 0.2, 0.9, 1.0, 1.9
    TAMANHO_MIN, TAMANHO_MAX = 14, 44      # limites do tamanho da cadeira, em pixels

    def __init__(self, app):
        super().__init__(app)
        self.selecionadas = set()
        self.preco = 0.0                               # preço da sessão escolhida
        self._tamanho_canvas = (0, 0)
        self.itens = {}
        self.geo = None

        self.botao_menu()
        rodape = tk.Frame(self, bg=FUNDO)
        rodape.pack(side="bottom", fill="x", padx=32, pady=(4, 6))
        self.resumo = tk.Label(rodape, bg=FUNDO, fg=TEXTO, font=FONTE_NEGRITO)
        self.resumo.pack(side="left")
        Botao(rodape, "Comprar", self.ao_comprar).pack(side="right")

        barra = self.cabecalho("Comprar ingresso")
        Botao(barra, "Relatório por filme", lambda: JanelaRelatorio(app),
              contorno=True).pack(side="right")

        formulario = tk.Frame(self, bg=FUNDO)
        formulario.pack(fill="x", padx=26)
        formulario.columnconfigure((0, 1), weight=1, uniform="col")
        self.combo_cliente = campo_com_rotulo(
            formulario, "Cliente", lambda p: ttk.Combobox(p, state="readonly"), 0, 0)
        self.combo_sessao = campo_com_rotulo(
            formulario, "Sessão", lambda p: ttk.Combobox(p, state="readonly"), 0, 1)
        self.combo_sessao.bind("<<ComboboxSelected>>", lambda e: self._ao_trocar_sessao())

        # a legenda é empacotada antes do canvas para reservar o espaço dela
        legenda = tk.Frame(self, bg=FUNDO)
        legenda.pack(side="bottom", pady=6)
        for cor, rotulo in [(CADEIRA_LIVRE, "Livre"), (CADEIRA_OCUPADA, "Ocupada"),
                            (DESTAQUE, "Selecionada")]:
            tk.Label(legenda, bg=cor, width=2).pack(side="left", padx=(12, 4))
            tk.Label(legenda, text=rotulo, bg=FUNDO, fg=TEXTO_SUAVE,
                     font=FONTE_PEQUENA).pack(side="left")

        # o canvas ocupa o espaço que sobrar; o mapa é redesenhado ao redimensionar
        self.canvas = tk.Canvas(self, bg=FUNDO, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=32, pady=(10, 0))
        self.canvas.bind("<Configure>", self._ao_redimensionar)
        self._atualizar_resumo()

    # --- sessão escolhida
    @staticmethod
    def _rotulo_sessao(sessao):
        return f'{sessao["filme"]} - {sessao["horario"]} - Sala {sessao["sala"]}'

    @property
    def ocupadas(self):
        """Cadeiras já vendidas da sessão escolhida (vêm do banco, via app)."""
        i = self.combo_sessao.current()
        if i < 0:
            return set()
        return self.app.ocupadas.get(self.app.sessoes[i]["id"], set())
    
    def _ao_trocar_sessao(self):
        indice = self.combo_sessao.current()
        self.preco = self.app.sessoes[indice].get("preco", self.PRECO_PADRAO) if indice >= 0 else 0.0
        self.limpar_selecao()

    def _limite(self):
        indice = self.combo_sessao.current()
        return self.app.sessoes[indice]["lugares"] if indice >= 0 else 0

    # --- mapa de cadeiras (escalável)
    def _ao_redimensionar(self, e):
        if (e.width, e.height) != self._tamanho_canvas:
            self._tamanho_canvas = (e.width, e.height)
            self._desenhar()

    def _calcular_geometria(self, largura, altura):
        """Escolhe o tamanho da cadeira que cabe na área e centraliza o mapa nela."""
        colunas, fileiras = self.COLUNAS, len(self.FILEIRAS)
        un_largura = (2 * self.MARGEM_REL + colunas * (1 + self.ESPACO_REL)
                      - self.ESPACO_REL + self.CORREDOR_REL)
        un_altura = self.TOPO_REL + fileiras * (1 + self.ESPACO_REL) - self.ESPACO_REL
        t = int(min(largura / un_largura, altura / un_altura))
        t = max(self.TAMANHO_MIN, min(self.TAMANHO_MAX, t))

        esp = max(2, round(t * self.ESPACO_REL))
        corredor = round(t * self.CORREDOR_REL)
        margem = round(t * self.MARGEM_REL)
        topo = round(t * self.TOPO_REL)
        total_largura = 2 * margem + colunas * (t + esp) - esp + corredor
        total_altura = topo + fileiras * (t + esp) - esp
        origem_x = max(0, (largura - total_largura) // 2)
        origem_y = max(0, (altura - total_altura) // 2)
        return SimpleNamespace(
            t=t, esp=esp, corredor=corredor, margem=margem, topo=topo,
            x0=origem_x + margem, oy=origem_y, y0=origem_y + topo,
            fonte=max(7, min(12, round(t * 0.3))))

    def _x_cadeira(self, i):
        g = self.geo
        corredor = g.corredor if i >= self.COLUNAS // 2 else 0
        return g.x0 + i * (g.t + g.esp) + corredor

    def _cor(self, rotulo):
        if rotulo in self.ocupadas:
            return CADEIRA_OCUPADA
        return DESTAQUE if rotulo in self.selecionadas else CADEIRA_LIVRE

    def _desenhar(self):
        largura, altura = self._tamanho_canvas
        if largura < 50 or altura < 50:     # ainda sem tamanho: o <Configure> redesenha
            return
        g = self.geo = self._calcular_geometria(largura, altura)
        c = self.canvas
        c.delete("all")
        self.itens = {}
        fonte = ("Segoe UI", g.fonte)

        x_ini = self._x_cadeira(0)
        x_fim = self._x_cadeira(self.COLUNAS - 1) + g.t
        y_linha = g.oy + g.topo * 0.39
        c.create_text((x_ini + x_fim) / 2, g.oy + g.topo * 0.14, text="TELA",
                      fill=TEXTO_SUAVE, font=fonte)
        c.create_line(x_ini, y_linha, x_fim, y_linha, fill=DESTAQUE, width=max(2, g.t // 8))
        for i in range(self.COLUNAS):
            c.create_text(self._x_cadeira(i) + g.t / 2, g.oy + g.topo * 0.75, text=str(i + 1),
                          fill=TEXTO_SUAVE, font=fonte)
        for linha, fileira in enumerate(self.FILEIRAS):
            y = g.y0 + linha * (g.t + g.esp)
            c.create_text(x_ini - g.margem / 2, y + g.t / 2, text=fileira,
                          fill=TEXTO_SUAVE, font=fonte)
            for i in range(self.COLUNAS):
                rotulo = f"{fileira}{i + 1}"
                x = self._x_cadeira(i)
                item = c.create_rectangle(x, y, x + g.t, y + g.t, fill=self._cor(rotulo),
                                          outline="", tags=("cadeira",))
                self.itens[item] = rotulo
        c.tag_bind("cadeira", "<Button-1>", self._ao_clicar_cadeira)

    def _ao_clicar_cadeira(self, _evento):
        if self.combo_sessao.current() < 0:
            messagebox.showinfo("Comprar ingresso", "Escolha uma sessão primeiro.")
            return
        item = self.canvas.find_withtag("current")[0]
        rotulo = self.itens[item]
        if rotulo in self.ocupadas:
            return
        if rotulo not in self.selecionadas and len(self.selecionadas) >= self._limite():
            messagebox.showinfo("Comprar ingresso",
                                f"Esta sessão permite escolher até {self._limite()} cadeira(s).")
            return
        self.selecionadas.symmetric_difference_update({rotulo})
        self.canvas.itemconfig(item, fill=self._cor(rotulo))
        self._atualizar_resumo()

    def _atualizar_resumo(self):
        cadeiras = sorted(self.selecionadas, key=lambda s: (s[0], int(s[1:])))
        texto = ", ".join(cadeiras) if cadeiras else "—"
        self.resumo.config(text=f"Cadeiras: {texto} | Total: {brl(len(cadeiras) * self.preco)}")

    def limpar_selecao(self):
        self.selecionadas.clear()
        self._desenhar()
        self._atualizar_resumo()

    def ao_comprar(self):
        i, j = self.combo_sessao.current(), self.combo_cliente.current()
        if i < 0:
            messagebox.showwarning("Comprar ingresso", "Escolha uma sessão.")
            return
        if j < 0:
            messagebox.showwarning("Comprar ingresso", "Escolha o cliente.")
            return
        if not self.selecionadas:
            messagebox.showwarning("Comprar ingresso", "Selecione ao menos uma cadeira.")
            return
        self.app.comprar_ingressos(self.app.clientes[j]["id"], self.app.sessoes[i]["id"],
                                   sorted(self.selecionadas))
        self.limpar_selecao()

    def atualizar(self):
        self.combo_cliente["values"] = [c["nome"] for c in self.app.clientes]
        self.combo_sessao["values"] = [self._rotulo_sessao(s) for s in self.app.sessoes]
        if self.combo_sessao.current() < 0:      # a sessão escolhida deixou de existir
            self.combo_sessao.set("")
        if self.combo_cliente.current() < 0:
            self.combo_cliente.set("")
        self._desenhar()