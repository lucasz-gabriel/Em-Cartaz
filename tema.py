"""Tema do Cinema: cores, fontes e formatação de valores."""

FUNDO, SUPERFICIE, BORDA = "#141414", "#1F1F1F", "#3A3A3A"
DESTAQUE, DESTAQUE_HOVER = "#F5B301", "#FFC933"
TEXTO, TEXTO_SUAVE = "#F2F2F2", "#9A9A9A"
CADEIRA_LIVRE, CADEIRA_OCUPADA = "#2E7D32", "#C62828"

FONTE = ("Segoe UI", 11)
FONTE_NEGRITO = ("Segoe UI", 11, "bold")
FONTE_TITULO = ("Segoe UI", 24, "bold")
FONTE_PEQUENA = ("Segoe UI", 9)

# cores dos pôsteres de exemplo (enquanto não há imagem)
PALETA = ["#1E6FB5", "#8B1E3F", "#0F7B6C", "#34495E",
          "#A56A1B", "#5B3A9B", "#2E7D32", "#6D4C41"]


def brl(valor):
    """1234.5 -> 'R$ 1.234,50'"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
