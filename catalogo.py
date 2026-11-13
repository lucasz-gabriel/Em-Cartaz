import os 
import pandas as pd
import dados_imdb
import scraping

Cache = "filmes_cache.csv"

def carregar_catalogo(qtd=10):
    #Primeira exucação faz o scraping do site do IMDB, posteriormente apenas carrega
    if os.path.exists(Cache):
        df = pd.read_csv(Cache, encoding="utf-8-sig")
        df = ["poster"] = df["poster"].fillna("")
        return df

    df = scraping.buscar_filmes(qtd) #wikipedia
    try:
        df = dados_imdb.completar(df) #imdb
    except FileNotFoundError:
        df["genero"] = "Não informado"
        df["duração"] = 0

    df["poster"] = [scraping.baixar_poster(1,t) for 1,t in zip(df["link"], df["titulo"])]

    df.to_csv(Cache, index=False, encoding="utf-8-sig")
    return df