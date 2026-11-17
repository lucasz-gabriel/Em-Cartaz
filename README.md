# 🎬 Sistema de Cinema

Sistema de gerenciamento de cinema com interface gráfica, feito em **Python** com **Tkinter**.
Mostra os filmes em cartaz com pôsteres, cadastra sessões e clientes e vende ingressos com **escolha de cadeiras**. Tudo fica salvo em um banco **SQLite** (via **SQLAlchemy**), e o relatório de vendas é gerado com **pandas**.

---

## ✨ Funcionalidades

- 🎞️ **Em cartaz**: catálogo de filmes em grade, com pôster, gênero e duração
- 🔎 **Busca de pôster na web**: ao cadastrar um filme, o sistema busca o pôster na Wikipédia (web scraping)
- 🕒 **Sessões**: horário, sala e quantidade de lugares, ligadas a um filme
- 👤 **Clientes**: cadastro com nome e e-mail, mostrando ingressos comprados e total gasto
- 🎟️ **Compra de ingressos com mapa de cadeiras**: cadeiras livres, ocupadas e selecionadas, com limite de cadeiras por sessão
- 📊 **Relatório de vendas por filme** (pandas), com exportação para **CSV** (abre no Excel)
- 💾 **Persistência**: filmes, sessões, clientes e ingressos continuam salvos ao fechar o programa
- ✅ Validações: e-mail e filme sem repetição, horário no formato `HH:MM` e cadeira que não pode ser vendida duas vezes

---

## 🖥️ Telas

| Tela | O que faz |
|------|-----------|
| **Menu** | Tela principal, com o resumo geral e acesso às outras telas |
| **Em cartaz** | Catálogo de filmes com pôsteres e botão para adicionar filme |
| **Novo filme** (janela) | Cadastra um filme e busca o pôster na Wikipédia |
| **Sessões** | Cria sessões vinculadas a um filme |
| **Clientes** | Cadastra clientes e mostra o histórico de compras |
| **Comprar ingresso** | Escolhe cliente, sessão e cadeiras no mapa da sala |
| **Relatório** (janela) | Faturamento por filme, com exportação em CSV |

---

## 🧠 Como os dados se relacionam

O banco tem 4 tabelas ligadas por chaves estrangeiras (`ForeignKey`):

```
Filme ──< Sessao ──< Ingresso >── Cliente
 (1 filme tem várias sessões)   (1 cliente compra vários ingressos)
 (1 sessão tem vários ingressos)
```

| Tabela | Campos principais |
|--------|-------------------|
| `filmes` | id, titulo, genero, duracao, cor, imagem |
| `sessoes` | id, **filme_id**, data, horario, sala, preco, lugares |
| `clientes` | id, nome, email (único) |
| `ingressos` | id, **sessao_id**, **cliente_id**, cadeira, preco |

A tabela `ingressos` tem uma restrição de unicidade em `(sessao_id, cadeira)`: o próprio banco impede vender a mesma cadeira duas vezes na mesma sessão.

Dentro do programa, os dados são carregados em listas de dicionários, e as telas os mostram em tabelas (como uma planilha).

---

## 🧩 Onde cada conceito aparece no código

| Conceito | Onde |
|----------|------|
| Dados em listas relacionadas | `app.py` (`filmes`, `sessoes`, `clientes`, `ocupadas`) e as chaves estrangeiras em `database/models.py` |
| Tabela estilo Excel | `componentes.py` (`criar_tabela`, `preencher_tabela`), usada em Sessões, Clientes e Relatório |
| **pandas** | `database/repositorio.py` (`relatorio_df`: `read_sql` + `groupby`) e `janelas/janela_relatorio.py` (exportação para CSV) |
| **Web scraping** | `raspador.py` (busca do pôster na Wikipédia), usado em `janelas/janela_novo_filme.py` e no `app.py` |
| **Banco de dados (ORM)** | `database/connection.py`, `database/models.py` e `database/repositorio.py` (SQLAlchemy + SQLite) |
| Interface gráfica | `telas/`, `janelas/`, `componentes.py` e `tema.py` (Tkinter) |

---

## 🚀 Como executar

### Pré-requisitos

- [Python 3.10+](https://www.python.org/downloads/) (o Tkinter já vem junto no Windows e no macOS)

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/lucasz-gabriel/Projeto-Manfrine.git
cd Projeto-Manfrine

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 3. Instalar as bibliotecas
pip install -r requirements.txt

# 4. Rodar o sistema
python app.py
```

Na primeira execução, o arquivo `cinema.db` é criado sozinho e já vem com filmes, sessões e clientes de demonstração. Para voltar ao estado inicial, feche o programa e apague o `cinema.db`.

> No Linux, se aparecer erro de Tkinter, instale com: `sudo apt install python3-tk`

---

## 📁 Estrutura do projeto

```
Projeto-Manfrine/
├── app.py                  # janela principal e ligação entre telas e banco
├── componentes.py          # botão, campos, tabela e classe base das telas
├── tema.py                 # cores e fontes (tema escuro)
├── raspador.py             # web scraping do pôster (Wikipédia)
├── dados_demo.py           # dados de demonstração da carga inicial
├── requirements.txt
├── database/
│   ├── connection.py       # conexão com o SQLite
│   ├── models.py           # tabelas (Filme, Sessao, Cliente, Ingresso)
│   └── repositorio.py      # consultas, gravações e relatório em pandas
├── telas/
│   ├── tela_menu.py
│   ├── tela_catalogo.py
│   ├── tela_sessoes.py
│   ├── tela_clientes.py
│   └── tela_ingressos.py
├── janelas/
│   ├── janela_novo_filme.py
│   └── janela_relatorio.py
└── posters/                # pôsteres baixados (criada automaticamente)
```

---

## 🛠️ Tecnologias

- **Python 3**
- **Tkinter / ttk**: interface gráfica
- **SQLite + SQLAlchemy**: banco de dados e ORM
- **pandas**: relatório de vendas e exportação em CSV
- **requests + BeautifulSoup**: web scraping
- **Pillow**: exibição dos pôsteres
- **Git / GitHub**: versionamento e trabalho em equipe (branches)
- **Figma**: protótipo das telas

---

## 🔮 Melhorias futuras

- [ ] Editar e excluir sessões e clientes
- [ ] Calendário de datas nas sessões
- [ ] Preço diferente por sessão
- [ ] Login de cliente
- [ ] Integração com a API do TMDB para dados e pôsteres

---

## 👨‍💻 Equipe
Lucas Roque 
Ítalo Pereira
Paulo Gabriel

- **Lucas** ([@lucasz-gabriel](https://github.com/lucasz-gabriel)): banco de dados, relatório e integração
- **Ítalo** ([@Italo-P](https://github.com/Italo-P)): telas e web scraping
- *demais integrantes*
