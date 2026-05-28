# XPTracker Final - Como rodar (macOS / Linux)

Versão que junta o **backend** (FastAPI + SQLite) com o **layout** mais caprichado do front.

## Preparar o ambiente (uma vez só)

Dentro da pasta do projeto:

```bash
cd XPTracker_final
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

> A pasta `.venv` que veio do projeto original era do Windows e não funciona no Mac — por isso
> criamos uma nova aqui.

## Rodar (precisa de 2 terminais)

### Terminal 1 — FastAPI (backend, porta 8000)

```bash
.venv/bin/python -m uvicorn api_fast:app --reload --port 8000
```

Documentação da API: http://127.0.0.1:8000/docs

### Terminal 2 — Flask (site, porta 5001)

```bash
PORT=5001 .venv/bin/python app_flask.py
```

O site fica em: http://127.0.0.1:5001

> **Por que 5001 e não 5000?** No macOS a porta 5000 é usada pelo "Receptor AirPlay"
> (Control Center). Para usar a 5000 padrão, desligue em
> Ajustes do Sistema → Geral → AirDrop & Handoff → "Receptor AirPlay", e aí pode rodar só
> `.venv/bin/python app_flask.py`.

## Fluxo conectado

1. A tela pública abre em `/`.
2. Cadastro envia dados para `POST /usuarios` na FastAPI (senha com hash bcrypt).
3. Login envia dados para `POST /login` na FastAPI; o Flask guarda o usuário na sessão.
4. A home logada (`/home`) mostra:
   - **Avaliações populares**: reviews reais de todos os usuários (vindas da API).
   - **Suas avaliações recentes**: reviews do usuário logado.
5. O perfil (`/perfil`) busca usuário, reviews e lista de desejo na FastAPI.
6. Criar, editar e excluir reviews usam a FastAPI.
7. Adicionar e remover jogos da lista de desejo também usam a FastAPI.

## Banco de dados

Os dados ficam em `xptracker.db` (SQLite). Para começar do zero, basta apagar esse arquivo —
o `init_db()` recria as tabelas no próximo start da API.
