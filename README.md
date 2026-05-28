# 🎮 XPTracker

Uma rede social de avaliações de jogos — pense em um "Letterboxd para games". Os usuários
podem se cadastrar, avaliar os jogos que jogaram (com nota, plataforma e um texto de review),
montar uma lista de desejo e acompanhar as avaliações da comunidade. 🕹️

O projeto é dividido em duas partes:

- **🔧 Backend (API):** [FastAPI](https://fastapi.tiangolo.com/) + SQLite, com senhas protegidas
  por hash `bcrypt`.
- **🎨 Frontend (site):** [Flask](https://flask.palletsprojects.com/) servindo páginas HTML
  (Jinja), que conversa com a API e usa a [API do RAWG](https://rawg.io/apidocs) para buscar
  capas e dados dos jogos.

## ✨ Funcionalidades

- 🔐 Cadastro e login de usuários (senha com hash `bcrypt`).
- 🔍 Busca de jogos com sugestões automáticas (via RAWG).
- ⭐ Criar, editar e excluir avaliações (nota, plataforma e texto).
- 📰 Feed com as avaliações populares da comunidade e as suas avaliações recentes.
- 💜 Lista de desejo: adicionar e remover jogos.
- 👤 Perfil editável (nome, bio e foto).

## 🛠️ Tecnologias

| Camada   | Stack                                            |
| -------- | ------------------------------------------------ |
| Backend  | FastAPI, Uvicorn, SQLite, bcrypt, Pydantic       |
| Frontend | Flask, Jinja2, HTML/CSS/JS, `requests`           |
| Externo  | API do RAWG (catálogo de jogos)                  |

## 📋 Pré-requisitos

- Python 3.10+
- Uma chave da API do RAWG (gratuita em https://rawg.io/apidocs)

## ⚙️ Configuração

1. Crie o ambiente virtual e instale as dependências:

   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

2. Copie o arquivo de exemplo de variáveis de ambiente e preencha os valores:

   ```bash
   cp .env.example .env
   ```

   No `.env`:

   - `FLASK_SECRET_KEY` — chave de sessão do Flask. Gere uma com
     `python -c "import secrets; print(secrets.token_hex(32))"`.
   - `RAWG_KEY` — sua chave da API do RAWG.
   - `API_FASTAPI` — URL do backend (padrão `http://127.0.0.1:8000`).
   - `PORT` — porta do site Flask (use `5001` no macOS por causa do AirPlay).

## 🚀 Como rodar

São necessários **dois terminais** (backend e frontend rodam separados).

**Terminal 1 — 🔧 API (FastAPI, porta 8000):**

```bash
.venv/bin/python -m uvicorn api_fast:app --reload --port 8000
```

Documentação interativa da API: http://127.0.0.1:8000/docs

**Terminal 2 — 🎨 Site (Flask, porta 5001):**

```bash
.venv/bin/python app_flask.py
```

O site abre em: http://127.0.0.1:5001

> 💡 **Por que a porta 5001 e não 5000?** No macOS a porta 5000 é usada pelo "Receptor AirPlay".
> Para usar a 5000 padrão, desligue-o em Ajustes do Sistema → Geral → AirDrop & Handoff.

## 📡 Endpoints da API

| Método   | Rota                                | Descrição                          |
| -------- | ----------------------------------- | ---------------------------------- |
| `POST`   | `/usuarios`                         | Cadastra um usuário                |
| `POST`   | `/login`                            | Autentica um usuário               |
| `GET`    | `/usuarios/{id}`                    | Busca um usuário                   |
| `PUT`    | `/usuarios/{id}`                    | Atualiza nome, bio e foto          |
| `POST`   | `/avaliacoes`                       | Cria uma avaliação                 |
| `GET`    | `/avaliacoes`                       | Lista todas as avaliações          |
| `GET`    | `/usuarios/{id}/avaliacoes`         | Avaliações de um usuário           |
| `PUT`    | `/avaliacoes/{id}`                  | Edita uma avaliação                |
| `DELETE` | `/avaliacoes/{id}`                  | Exclui uma avaliação               |
| `POST`   | `/desejos`                          | Adiciona um jogo à lista de desejo |
| `GET`    | `/usuarios/{id}/desejos`            | Lista de desejo de um usuário      |
| `DELETE` | `/desejos/{id}`                     | Remove um jogo da lista de desejo  |

## 🗄️ Banco de dados

Os dados ficam em `xptracker.db` (SQLite, criado automaticamente). As tabelas são `usuarios`,
`avaliacoes` e `desejos`. Para começar do zero, basta apagar o arquivo — o `init_db()` recria
as tabelas no próximo start da API.

## 📁 Estrutura do projeto

```
.
├── api_fast.py        # Backend FastAPI (API + banco SQLite)
├── app_flask.py       # Frontend Flask (site + integração com a API)
├── requirements.txt   # Dependências Python
├── .env.example       # Modelo de variáveis de ambiente
├── templates/         # Páginas HTML (Jinja)
└── static/            # CSS, JavaScript e imagens
```
