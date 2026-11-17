"""Raspador da Wikipédia (pt): baixa o pôster (cartaz) de um filme pelo título.

Usa a API da Wikipédia (api.php) para achar a página e pegar o HTML do começo dela,
e o BeautifulSoup para achar a imagem da infocaixa (a tabela do canto direito do artigo).

Teste sozinho:  python raspador.py "Titanic"
Dependências:   pip install requests beautifulsoup4 pillow
"""
import io
import re
import sys
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

try:
    from PIL import Image, ImageOps
except ImportError:   # sem Pillow o pôster é salvo do tamanho original
    Image = None

API = "https://pt.wikipedia.org/w/api.php"
# A Wikimedia exige um User-Agent descritivo, com contato (o padrão do requests
# pode ser bloqueado). TROQUE o e-mail abaixo pelo seu.
CABECALHOS = {"User-Agent": "CinemaApp/0.1 (projeto de faculdade; seu_email@exemplo.com) requests"}
PASTA_POSTERS = Path(__file__).resolve().parent / "posters"
TIMEOUT = 10                    # segundos
TAMANHO_POSTER = (300, 430)     # mesma proporção do cartão do catálogo (150:215)

# rótulos (normalizados) que indicam que uma tabela é a infocaixa de um filme;
# serve para não pegar a imagem de uma página que não é de filme
ROTULOS_DE_FILME = {"genero", "direcao", "realizacao", "elenco", "roteiro", "argumento",
                    "producao", "idioma", "estudio", "musica", "duracao"}


class ErroBusca(Exception):
    """Falha esperada: sem rede, filme não encontrado, página sem pôster..."""


# ---------------------------------------------------------------- utilitários
def _sem_acento(texto):
    s = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _normalizar(texto):
    """'Gênero:' -> 'genero' (minúsculo, sem acento e sem pontuação)."""
    return re.sub(r"[^a-z ]", "", _sem_acento(texto)).strip()


def _slug(texto):
    """'Duna: Parte 2' -> 'duna-parte-2' (para nome de arquivo)."""
    return re.sub(r"[^a-z0-9]+", "-", _sem_acento(texto)).strip("-") or "filme"


def _api(**params):
    params.update(format="json", formatversion=2)
    try:
        resposta = requests.get(API, params=params, headers=CABECALHOS, timeout=TIMEOUT)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as erro:
        raise ErroBusca(f"Não consegui falar com a Wikipédia ({type(erro).__name__}). "
                        "Confira a internet.") from erro


# ---------------------------------------------------------------- leitura da infocaixa
def _rotulos(tabela):
    """Rótulos (normalizados) das linhas com exatamente duas células: rótulo + valor."""
    rotulos = set()
    for tr in tabela.find_all("tr"):
        celulas = tr.find_all(["th", "td"], recursive=False)
        if len(celulas) == 2:
            rotulos.add(_normalizar(celulas[0].get_text(" ", strip=True)))
    return rotulos


def _url_poster(tabela):
    """Primeira imagem grande da infocaixa (ignora bandeiras e ícones pequenos)."""
    for img in tabela.find_all("img"):
        try:
            if int(float(img.get("width") or 0)) < 60:
                continue
        except ValueError:
            continue
        srcset = img.get("srcset")
        url = srcset.split(",")[-1].split()[0] if srcset else img.get("src")
        if not url or url.lower().endswith(".svg") or "/Flag_of_" in url:
            continue
        return "https:" + url if url.startswith("//") else url
    return None


def _poster_da_infocaixa(html):
    """Devolve (é_página_de_filme, url_do_pôster)."""
    soup = BeautifulSoup(html, "html.parser")
    for tabela in soup.find_all("table"):
        if len(ROTULOS_DE_FILME & _rotulos(tabela)) >= 2:
            return True, _url_poster(tabela)
    return False, None


def _baixar(url, titulo):
    """Baixa a imagem, redimensiona para o tamanho padrão e salva em posters/ (JPEG).
    Devolve o caminho do arquivo."""
    try:
        resposta = requests.get(url, headers=CABECALHOS, timeout=TIMEOUT)
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroBusca(f"Não consegui baixar o pôster ({type(erro).__name__}).") from erro
    if not resposta.headers.get("Content-Type", "").startswith("image/"):
        raise ErroBusca("O endereço do pôster não devolveu uma imagem.")
    PASTA_POSTERS.mkdir(exist_ok=True)
    if Image is None:                                  # sem Pillow: guarda o original
        extensao = Path(url.split("?")[0]).suffix.lower()
        destino = PASTA_POSTERS / f"{_slug(titulo)}{extensao if extensao in {'.jpg', '.jpeg', '.png', '.gif', '.webp'} else '.jpg'}"
        destino.write_bytes(resposta.content)
        return str(destino)
    try:
        with Image.open(io.BytesIO(resposta.content)) as original:
            # nunca amplia: se a imagem for menor que o padrão, só ajusta a proporção
            largura = min(TAMANHO_POSTER[0], original.width)
            altura = round(largura * TAMANHO_POSTER[1] / TAMANHO_POSTER[0])
            metodo = getattr(Image, "Resampling", Image).LANCZOS
            imagem = ImageOps.fit(original.convert("RGB"), (largura, altura), method=metodo)
    except OSError as erro:                            # inclui UnidentifiedImageError
        raise ErroBusca("O arquivo baixado não é uma imagem válida.") from erro
    destino = PASTA_POSTERS / f"{_slug(titulo)}.jpg"
    imagem.save(destino, "JPEG", quality=90)
    return str(destino)

# ---------------------------------------------------------------- API pública
def buscar_poster(titulo):
    """Acha o pôster do filme na Wikipédia, baixa para posters/ e devolve
    {"pagina": título do artigo, "poster": caminho do arquivo}. Levanta ErroBusca se falhar."""
    titulo = titulo.strip()
    if not titulo:
        raise ErroBusca("Digite o título do filme.")
    achados = _api(action="query", list="search", srsearch=f"{titulo} filme",
                   srlimit=5, srnamespace=0)
    paginas = [r["title"] for r in achados.get("query", {}).get("search", [])]
    if not paginas:
        raise ErroBusca(f"Nenhum resultado na Wikipédia para “{titulo}”.")
    sem_poster = None
    for pagina in paginas:                             # o 1º resultado nem sempre é o filme
        dados = _api(action="parse", page=pagina, prop="text", section=0, redirects=1,
                     disableeditsection=1, disablelimitreport=1)
        if "parse" not in dados:
            continue
        eh_filme, url = _poster_da_infocaixa(dados["parse"]["text"])
        if not eh_filme:
            continue
        if url:
            return {"pagina": pagina, "poster": _baixar(url, titulo)}
        sem_poster = sem_poster or pagina
    if sem_poster:
        raise ErroBusca(f"Achei “{sem_poster}”, mas a página não tem pôster.")
    raise ErroBusca(f"Não achei a página de um filme para “{titulo}”.")


if __name__ == "__main__":
    nome = " ".join(sys.argv[1:]) or "Avatar"
    try:
        print(buscar_poster(nome))
    except ErroBusca as erro:
        print("Erro:", erro)