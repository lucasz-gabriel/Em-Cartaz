# Projeto-Manfrine

🎬 Sistema de Cinema

Sistema de gerenciamento de cinema com interface gráfica, feito em Python usando Tkinter. Permite cadastrar filmes, criar sessões, registrar clientes e vender ingressos, tudo com dados digitados pelo usuário e armazenados em vetores (listas) relacionados entre si.

✨ Funcionalidades
🎞️ Filmes: cadastro com título, gênero e duração
🕒 Sessões: horário, sala, preço e número de lugares, ligadas a um filme
👤 Clientes: cadastro com nome e e-mail, mostrando ingressos comprados e total gasto
🎟️ Venda de ingressos: escolhe cliente, sessão e quantidade, com desconto automático dos lugares
✅ Validação dos campos e bloqueio de venda acima da lotação
📊 Resumo no menu principal com a contagem de filmes, sessões, clientes e ingressos vendidos
🖥️ Telas
#	Tela	O que faz
1	Menu	Tela principal, com acesso às outras telas e resumo geral
2	Filmes	Cadastra e lista os filmes
3	Sessões	Cria sessões vinculadas a um filme
4	Clientes	Cadastra clientes e mostra o histórico de compras
5	Vender ingresso	Registra vendas e lista todas as vendas feitas
🧠 Estrutura dos dados

Todos os dados ficam em listas (vetores) paralelas. A mesma posição (índice) em listas diferentes representa o mesmo registro, e algumas listas guardam o índice de outra para criar a relação.

FILMES                      SESSÕES                       VENDAS
filmes_titulo[i]            sessoes_filme[s]  ───────►    (índice do filme)
filmes_genero[i]            sessoes_horario[s]
filmes_duracao[i]           sessoes_sala[s]               ing_sessao[v]   ───► (índice da sessão)
                            sessoes_preco[s]              ing_cliente[v]  ───► (índice do cliente)
CLIENTES                    sessoes_vagas[s]              ing_qtd[v]
clientes_nome[c]                                          ing_total[v]
clientes_email[c]

Exemplo: se sessoes_filme[2] = 0, a sessão 2 é do filme que está na posição 0 de filmes_titulo.

🚀 Como executar
Pré-requisitos
Python 3.8+
Tkinter (já vem instalado com o Python no Windows e no macOS)

Não precisa instalar nenhuma biblioteca extra.

Passo a passo
bash
# 1. Clonar o repositório
git clone https://github.com/lucasz-gabriel/Projeto-Manfrine.git

# 2. Entrar na pasta
cd Projeto-Manfrine

# 3. Rodar o sistema
python cinema.py

No Linux, se aparecer erro de Tkinter, instale com: sudo apt install python3-tk

📖 Como usar

Como o sistema começa vazio, siga esta ordem:

Cadastre os filmes
Crie as sessões (é preciso ter pelo menos um filme)
Cadastre os clientes
Faça a venda de ingressos (precisa de cliente e sessão com lugares)
📁 Estrutura do projeto
Projeto-Manfrine/
├── cinema.py     # código completo do sistema
└── README.md     # este arquivo
🛠️ Tecnologias
Python 3
Tkinter / ttk: interface gráfica
Listas (vetores) para armazenamento dos dados em memória
⚠️ Observações

Os dados ficam apenas na memória. Ao fechar o programa, tudo é perdido.

🔮 Melhorias futuras
 Salvar os dados em arquivo (JSON ou CSV) ou banco de dados
 Editar e excluir registros
 Escolha de assentos por sessão
 Relatório de faturamento por filme
