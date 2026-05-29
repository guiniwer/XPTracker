from functools import wraps # Importa wraps para manter informacoes originais das funcoes decoradas, como nome e docstring.
import os # Importa os para acessar variaveis de ambiente, como chaves e portas.
import secrets # Importa secrets para gerar uma chave secreta segura caso nao exista no .env.

from dotenv import load_dotenv # Carrega variaveis do arquivo .env para dentro da aplicacao.
# Importa recursos principais do Flask para rotas, templates, sessoes, mensagens e respostas JSON.
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
import requests # Importa requests para fazer chamadas HTTP para a FastAPI e para a API externa RAWG.


load_dotenv()

# Cria a aplicacao Flask.
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)

# Configuracoes principais usadas para conectar com APIs e controlar timeout das requisicoes.
API_FASTAPI = os.getenv("API_FASTAPI", "http://127.0.0.1:8000")
RAWG_KEY = os.getenv("RAWG_KEY", "")
REQUEST_TIMEOUT = 8


# Funcao auxiliar para centralizar chamadas HTTP feitas para a API FastAPI.
def api_request(method, path, **kwargs):
    try:
        return requests.request(
            method,
            f"{API_FASTAPI}{path}",
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )
    except requests.RequestException:
        return None


# Funcao auxiliar para transformar erros da API em mensagens amigaveis para o usuario.
def api_error_message(resposta, fallback):
    if resposta is None:
        return "Nao foi possivel conectar com a API. Verifique se a FastAPI esta rodando na porta 8000."

    try:
        dados = resposta.json()
    except ValueError:
        return fallback

    detail = dados.get("detail")
    if isinstance(detail, str):
        return detail
    if isinstance(detail, list) and detail:
        return detail[0].get("msg", fallback)
    return dados.get("message", fallback)


# Decorator que protege rotas e obriga o usuario a estar logado para acessar.
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


# Funcao que padroniza os dados do usuario vindos da API antes de usar na sessao ou templates.
def normalizar_usuario(payload):
    usuario = payload.get("usuario", payload) if isinstance(payload, dict) else {}
    foto = usuario.get("foto_url") or usuario.get("foto_perfil_url") or ""

    return {
        "id": usuario.get("id"),
        "nome": usuario.get("nome", "Usuario"),
        "email": usuario.get("email", ""),
        "foto_url": foto,
        "foto_perfil_url": foto,
        "bio": usuario.get("bio") or "Nada aqui...",
        "criado_em": usuario.get("criado_em", ""),
    }


# Funcao que padroniza os dados de uma avaliacao/review, aceitando nomes diferentes de campos.
def normalizar_review(review):
    capa = (
        review.get("capa_jogo_url")
        or review.get("jogo_capa_url")
        or review.get("link_capa")
        or ""
    )
    texto = review.get("review_texto") or review.get("texto") or review.get("review") or ""
    nome_jogo = review.get("nome_jogo") or review.get("jogo_nome") or ""

    return {
        "id": review.get("id"),
        "usuario_id": review.get("usuario_id") or review.get("id_usuario"),
        "usuario": review.get("usuario_nome") or review.get("usuario") or "Usuario",
        "usuario_foto_url": review.get("usuario_foto_url") or "",
        "nome_jogo": nome_jogo,
        "jogo_nome": nome_jogo,
        "capa_jogo_url": capa,
        "jogo_capa_url": capa,
        "nota": review.get("nota", 0),
        "plataforma": review.get("plataforma") or "",
        "review_texto": texto,
        "texto": texto,
    }


# Funcao que padroniza os dados dos jogos salvos na lista de desejos.
def normalizar_desejo(desejo):
    capa = (
        desejo.get("capa_jogo_url")
        or desejo.get("jogo_capa_url")
        or desejo.get("link_capa")
        or ""
    )
    nome_jogo = desejo.get("nome_jogo") or desejo.get("jogo_nome") or ""

    return {
        "id": desejo.get("id"),
        "usuario_id": desejo.get("usuario_id") or desejo.get("id_usuario"),
        "nome_jogo": nome_jogo,
        "jogo_nome": nome_jogo,
        "capa_jogo_url": capa,
        "jogo_capa_url": capa,
    }


# Funcao auxiliar que retorna o id do usuario atualmente salvo na sessao.
def usuario_logado_id():
    usuario = session.get("usuario", {})
    return usuario.get("id")


# Funcao que busca na API todas as avaliacoes feitas por um usuario especifico.
def buscar_reviews_usuario(usuario_id):
    resposta = api_request("GET", f"/usuarios/{usuario_id}/avaliacoes")
    if resposta is None or resposta.status_code != 200:
        return []

    dados = resposta.json()
    return [normalizar_review(review) for review in dados.get("avaliacoes", [])]


# Funcao que busca na API todas as avaliacoes publicadas.
def buscar_todas_reviews():
    resposta = api_request("GET", "/avaliacoes")
    if resposta is None or resposta.status_code != 200:
        return []

    dados = resposta.json()
    return [normalizar_review(review) for review in dados.get("avaliacoes", [])]


# Funcao que busca na API a lista de desejos de um usuario especifico.
def buscar_desejos_usuario(usuario_id):
    resposta = api_request("GET", f"/usuarios/{usuario_id}/desejos")
    if resposta is None or resposta.status_code != 200:
        return []

    dados = resposta.json()
    return [normalizar_desejo(desejo) for desejo in dados.get("desejos", [])]


# Funcao que atualiza os dados do usuario logado dentro da sessao.
def atualizar_usuario_na_sessao():
    usuario_id = usuario_logado_id()
    if not usuario_id:
        return

    resposta = api_request("GET", f"/usuarios/{usuario_id}")
    if resposta is not None and resposta.status_code == 200:
        session["usuario"] = normalizar_usuario(resposta.json())
        session.modified = True


# ROTAS DA APLICACAO - Cada rota corresponde a uma URL e a um metodo HTTP, e define a
# logica de negocio para aquela funcionalidade especifica da aplicacao.

# Rota publica da pagina inicial para usuarios nao logados.
@app.route("/")
def inicio_publico():
    return render_template("index.html")


# Rota da home logada, exibindo dados do usuario, suas reviews e reviews populares.
@app.route("/home")
@login_required
def home():
    usuario_id = usuario_logado_id()
    atualizar_usuario_na_sessao()

    minhas_reviews = buscar_reviews_usuario(usuario_id)

    return render_template(
        "index_logado.html",
        usuario=session["usuario"],
        reviews=minhas_reviews,
        popular_reviews=buscar_todas_reviews(),
    )


# Rota de login: exibe o formulario no GET e autentica o usuario no POST.
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dados = {
            "email": request.form["email"],
            "senha": request.form["senha"],
        }

        resposta = api_request("POST", "/login", json=dados)

        if resposta is not None and resposta.status_code == 200:
            session["usuario"] = normalizar_usuario(resposta.json())
            return redirect(url_for("home"))

        flash(api_error_message(resposta, "Email ou senha invalidos."))

    return render_template("login.html")


# Rota de cadastro: exibe o formulario no GET e cria um novo usuario no POST.
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        senha = request.form["senha"]
        confirmar_senha = request.form.get("confirmar_senha")

        if confirmar_senha and senha != confirmar_senha:
            flash("As senhas nao coincidem.")
            return render_template("cadastro.html")

        dados = {
            "nome": request.form["nome"],
            "email": request.form["email"],
            "senha": senha,
        }

        resposta = api_request("POST", "/usuarios", json=dados)

        if resposta is not None and resposta.status_code in (200, 201):
            flash("Cadastro realizado com sucesso. Agora faca login.")
            return redirect(url_for("login"))

        flash(api_error_message(resposta, "Erro ao cadastrar usuario."))

    return render_template("cadastro.html")


# Rota que redireciona o usuario para a area de criar nova avaliacao na home.
@app.route("/nova-avaliacao")
@login_required
def nova_avaliacao():
    return redirect(url_for("home") + "#minhas-reviews")


# Rota de perfil do usuario logado, exibindo reviews e lista de desejos.
@app.route("/perfil")
@login_required
def perfil():
    usuario_id = usuario_logado_id()
    atualizar_usuario_na_sessao()

    return render_template(
        "perfil.html",
        usuario=session["usuario"],
        reviews=buscar_reviews_usuario(usuario_id),
        desejos=buscar_desejos_usuario(usuario_id),
    )


# Rota de logout, responsavel por limpar a sessao do usuario.
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("inicio_publico"))


# Rota que busca informacoes de um jogo na API RAWG a partir do formulario.
@app.route("/buscar-jogo", methods=["POST"])
@login_required
def buscar_jogo():
    nome_jogo = request.form["nome_jogo"]

    try:
        resposta = requests.get(
            "https://api.rawg.io/api/games",
            params={"key": RAWG_KEY, "search": nome_jogo},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        flash("Erro ao buscar jogo. Tente novamente.")
        return render_template(
            "index_logado.html",
            usuario=session["usuario"],
            reviews=buscar_reviews_usuario(usuario_logado_id()),
            popular_reviews=buscar_todas_reviews(),
            jogo=None,
        )

    jogo = None
    if resposta.status_code == 200:
        dados = resposta.json()
        if dados.get("results"):
            primeiro_jogo = dados["results"][0]
            jogo = {
                "nome": primeiro_jogo.get("name", ""),
                "capa": primeiro_jogo.get("background_image", ""),
                "ano": primeiro_jogo.get("released", ""),
            }

    return render_template(
        "index_logado.html",
        usuario=session["usuario"],
        reviews=buscar_reviews_usuario(usuario_logado_id()),
        popular_reviews=buscar_todas_reviews(),
        jogo=jogo,
    )


# Rota JSON que retorna sugestoes de jogos para autocomplete usando a API RAWG.
@app.route("/sugestoes-jogos")
def sugestoes_jogos():
    termo = request.args.get("q", "").strip()

    if not termo:
        return jsonify([])

    try:
        resposta = requests.get(
            "https://api.rawg.io/api/games",
            params={"key": RAWG_KEY, "search": termo, "page_size": 5},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        return jsonify([])

    if resposta.status_code != 200:
        return jsonify([])

    sugestoes = [
        {
            "nome": jogo.get("name"),
            "capa": jogo.get("background_image"),
        }
        for jogo in resposta.json().get("results", [])
    ]

    return jsonify(sugestoes)


# Rota que salva uma nova avaliacao feita pelo usuario logado.
@app.route("/salvar-avaliacao", methods=["POST"])
@login_required
def salvar_avaliacao():
    origem = request.form.get("origem", "perfil")

    nome_jogo = request.form.get("nome_jogo")
    capa_jogo_url = request.form.get("capa_jogo_url")
    nota = request.form.get("nota")
    plataforma = request.form.get("plataforma")
    review_texto = request.form.get("review_texto")

    try:
        nota_float = float(nota.replace(",", ".")) if nota else None
    except (TypeError, ValueError):
        nota_float = None

    if not nome_jogo or not capa_jogo_url:
        flash("Pesquise ou selecione um jogo antes de publicar a avaliacao.")
        return redirect(url_for("home" if origem == "home" else "perfil"))

    if not nota_float or not review_texto:
        flash("Preencha nota e review antes de publicar.")
        return redirect(url_for("home" if origem == "home" else "perfil"))

    dados = {
        "usuario_id": usuario_logado_id(),
        "jogo_nome": nome_jogo,
        "jogo_capa_url": capa_jogo_url,
        "nota": nota_float,
        "plataforma": plataforma,
        "texto": review_texto,
    }

    resposta = api_request("POST", "/avaliacoes", json=dados)

    if resposta is not None and resposta.status_code in (200, 201):
        flash("Avaliacao publicada com sucesso!")
        if origem == "home":
            return redirect(url_for("home") + "#minhas-reviews")
        return redirect(url_for("perfil"))

    flash(api_error_message(resposta, "Erro ao salvar avaliacao."))
    return redirect(url_for("home" if origem == "home" else "perfil"))


# Rota que atualiza nome, bio e foto de perfil do usuario logado.
@app.route("/editar-perfil", methods=["POST"])
@login_required
def editar_perfil():
    usuario_id = usuario_logado_id()
    dados = {
        "nome": request.form["nome"],
        "bio": request.form.get("bio", ""),
    }

    foto_perfil_url = request.form.get("foto_perfil_url", "").strip()
    if foto_perfil_url:
        dados["foto_perfil_url"] = foto_perfil_url

    resposta = api_request("PUT", f"/usuarios/{usuario_id}", json=dados)

    if resposta is not None and resposta.status_code == 200:
        session["usuario"] = normalizar_usuario(resposta.json())
        flash("Perfil atualizado com sucesso!")
    else:
        flash(api_error_message(resposta, "Erro ao atualizar perfil."))

    return redirect(url_for("perfil"))


# Rota tradicional que deleta uma avaliacao e redireciona de volta ao perfil.
@app.route("/deletar-avaliacao/<int:id>", methods=["POST"])
@login_required
def deletar_avaliacao(id):
    resposta = api_request("DELETE", f"/avaliacoes/{id}", params={"usuario_id": usuario_logado_id()})

    if resposta is not None and resposta.status_code == 200:
        flash("Avaliacao excluida com sucesso!")
    else:
        flash(api_error_message(resposta, "Erro ao excluir avaliacao."))

    return redirect(url_for("perfil"))


# Rota JSON que deleta uma avaliacao sem precisar recarregar a pagina inteira.
@app.route("/deletar-avaliacao-json/<int:id>", methods=["POST"])
@login_required
def deletar_avaliacao_json(id):
    resposta = api_request("DELETE", f"/avaliacoes/{id}", params={"usuario_id": usuario_logado_id()})

    if resposta is not None and resposta.status_code == 200:
        return jsonify({"mensagem": "Avaliacao excluida com sucesso"})

    return jsonify({"erro": api_error_message(resposta, "Erro ao excluir avaliacao.")}), 400


# Rota JSON que edita nota e texto de uma avaliacao existente.
@app.route("/editar-avaliacao-json/<int:id>", methods=["POST"])
@login_required
def editar_avaliacao_json(id):
    dados_json = request.get_json() or {}

    try:
        nota = float(dados_json.get("nota"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Nota invalida."}), 400

    dados = {
        "nota": nota,
        "texto": dados_json.get("review_texto", ""),
    }

    resposta = api_request(
        "PUT",
        f"/avaliacoes/{id}",
        params={"usuario_id": usuario_logado_id()},
        json=dados,
    )

    if resposta is not None and resposta.status_code == 200:
        return jsonify({"mensagem": "Avaliacao editada com sucesso"})

    return jsonify({"erro": api_error_message(resposta, "Erro ao editar avaliacao.")}), 400


# Rota JSON que adiciona um jogo na lista de desejos do usuario.
@app.route("/adicionar-desejo-json", methods=["POST"])
@login_required
def adicionar_desejo_json():
    dados_json = request.get_json() or {}

    nome_jogo = dados_json.get("nome_jogo")
    capa_jogo_url = dados_json.get("capa_jogo_url")

    if not nome_jogo or not capa_jogo_url:
        return jsonify({"erro": "Dados incompletos"}), 400

    resposta = api_request(
        "POST",
        "/desejos",
        json={
            "usuario_id": usuario_logado_id(),
            "jogo_nome": nome_jogo,
            "jogo_capa_url": capa_jogo_url,
        },
    )

    if resposta is not None and resposta.status_code in (200, 201):
        mensagem = resposta.json().get("message", "Jogo adicionado a lista de desejo")
        return jsonify({"mensagem": mensagem})

    return jsonify({"erro": api_error_message(resposta, "Erro ao adicionar desejo.")}), 400


# Rota JSON que remove um jogo da lista de desejos do usuario.
@app.route("/deletar-desejo-json/<int:id>", methods=["POST"])
@login_required
def deletar_desejo_json(id):
    resposta = api_request("DELETE", f"/desejos/{id}", params={"usuario_id": usuario_logado_id()})

    if resposta is not None and resposta.status_code == 200:
        return jsonify({"mensagem": "Jogo removido da lista de desejo"})

    return jsonify({"erro": api_error_message(resposta, "Erro ao remover desejo.")}), 400


# Ponto de entrada da aplicacao quando o arquivo e executado diretamente.
if __name__ == "__main__":
    porta = int(os.getenv("PORT", "5000"))
    app.run(debug=True, port=porta)
