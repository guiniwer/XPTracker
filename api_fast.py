from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Optional

import bcrypt
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, HttpUrl


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "xptracker.db"

app = FastAPI(title="XPTracker API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                foto_url TEXT,
                bio TEXT DEFAULT '',
                criado_em TEXT NOT NULL
            )
            """
        )
        ensure_column(conn, "usuarios", "bio", "TEXT DEFAULT ''")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS avaliacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                jogo_nome TEXT NOT NULL,
                jogo_capa_url TEXT,
                nota REAL NOT NULL,
                plataforma TEXT,
                texto TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                atualizado_em TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
            """
        )
        ensure_column(conn, "avaliacoes", "plataforma", "TEXT")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS desejos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                jogo_nome TEXT NOT NULL,
                jogo_capa_url TEXT NOT NULL,
                criado_em TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                UNIQUE (usuario_id, jogo_nome)
            )
            """
        )
        conn.commit()


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def hash_password(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))


def row_to_usuario(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "foto_url": row["foto_url"],
        "foto_perfil_url": row["foto_url"],
        "bio": row["bio"] if "bio" in row.keys() and row["bio"] else "",
        "criado_em": row["criado_em"],
    }


def row_to_avaliacao(row: sqlite3.Row) -> dict:
    avaliacao = {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "id_usuario": row["usuario_id"],
        "jogo_nome": row["jogo_nome"],
        "nome_jogo": row["jogo_nome"],
        "jogo_capa_url": row["jogo_capa_url"],
        "capa_jogo_url": row["jogo_capa_url"],
        "link_capa": row["jogo_capa_url"],
        "nota": row["nota"],
        "plataforma": row["plataforma"] if "plataforma" in row.keys() else None,
        "texto": row["texto"],
        "review_texto": row["texto"],
        "criado_em": row["criado_em"],
        "atualizado_em": row["atualizado_em"],
    }

    if "usuario_nome" in row.keys():
        avaliacao["usuario_nome"] = row["usuario_nome"]
    if "usuario_foto_url" in row.keys():
        avaliacao["usuario_foto_url"] = row["usuario_foto_url"]

    return avaliacao


def row_to_desejo(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "usuario_id": row["usuario_id"],
        "id_usuario": row["usuario_id"],
        "jogo_nome": row["jogo_nome"],
        "nome_jogo": row["jogo_nome"],
        "jogo_capa_url": row["jogo_capa_url"],
        "capa_jogo_url": row["jogo_capa_url"],
        "link_capa": row["jogo_capa_url"],
        "criado_em": row["criado_em"],
    }


class UsuarioCadastro(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nome: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=128)
    foto_url: Optional[HttpUrl] = None
    bio: Optional[str] = Field(default="", max_length=500)


class LoginEntrada(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=1)


class FotoPerfilAtualizacao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    foto_url: HttpUrl


class UsuarioAtualizacao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nome: Optional[str] = Field(default=None, min_length=2, max_length=80)
    bio: Optional[str] = Field(default=None, max_length=500)
    foto_url: Optional[str] = Field(
        default=None,
        max_length=500,
        validation_alias=AliasChoices("foto_url", "foto_perfil_url", "avatar_url"),
    )


class AvaliacaoCriacao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    usuario_id: int = Field(
        ...,
        gt=0,
        validation_alias=AliasChoices("usuario_id", "id_usuario", "user_id"),
    )
    jogo_nome: str = Field(
        ...,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("jogo_nome", "nome_jogo", "game_name"),
    )
    jogo_capa_url: Optional[str] = Field(
        default=None,
        max_length=500,
        validation_alias=AliasChoices(
            "jogo_capa_url",
            "capa_jogo_url",
            "link_capa",
            "capa_url",
            "cover_url",
        ),
    )
    nota: float = Field(..., ge=0, le=5)
    plataforma: Optional[str] = Field(default=None, max_length=50)
    texto: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        validation_alias=AliasChoices("texto", "review_texto", "review", "comentario"),
    )


class AvaliacaoAtualizacao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    jogo_nome: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("jogo_nome", "nome_jogo", "game_name"),
    )
    jogo_capa_url: Optional[str] = Field(
        default=None,
        max_length=500,
        validation_alias=AliasChoices(
            "jogo_capa_url",
            "capa_jogo_url",
            "link_capa",
            "capa_url",
            "cover_url",
        ),
    )
    nota: Optional[float] = Field(default=None, ge=0, le=5)
    plataforma: Optional[str] = Field(default=None, max_length=50)
    texto: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000,
        validation_alias=AliasChoices("texto", "review_texto", "review", "comentario"),
    )


class DesejoCriacao(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    usuario_id: int = Field(
        ...,
        gt=0,
        validation_alias=AliasChoices("usuario_id", "id_usuario", "user_id"),
    )
    jogo_nome: str = Field(
        ...,
        min_length=1,
        max_length=120,
        validation_alias=AliasChoices("jogo_nome", "nome_jogo", "game_name"),
    )
    jogo_capa_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
        validation_alias=AliasChoices(
            "jogo_capa_url",
            "capa_jogo_url",
            "link_capa",
            "capa_url",
            "cover_url",
        ),
    )


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def health_check() -> dict:
    return {"status": "ok", "message": "XPTracker FastAPI rodando"}


@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioCadastro) -> dict:
    senha_hash = hash_password(dados.senha)
    criado_em = datetime.utcnow().isoformat()

    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, foto_url, bio, criado_em)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    dados.nome.strip(),
                    dados.email.lower(),
                    senha_hash,
                    str(dados.foto_url) if dados.foto_url else None,
                    dados.bio.strip() if dados.bio else "",
                    criado_em,
                ),
            )
            conn.commit()
            usuario_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este e-mail ja esta cadastrado.",
        )

    with get_connection() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    return {"message": "Usuario cadastrado com sucesso.", "usuario": row_to_usuario(row)}


@app.post("/login")
def login(dados: LoginEntrada) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE email = ?",
            (dados.email.lower(),),
        ).fetchone()

    if row is None or not verify_password(dados.senha, row["senha_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha invalidos.",
        )

    return {"message": "Login realizado com sucesso.", "usuario": row_to_usuario(row)}


@app.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado.")

    return row_to_usuario(row)


@app.put("/usuarios/{usuario_id}/foto")
def atualizar_foto_perfil(usuario_id: int, dados: FotoPerfilAtualizacao) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE usuarios SET foto_url = ? WHERE id = ?",
            (str(dados.foto_url), usuario_id),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    return {"message": "Foto de perfil atualizada.", "usuario": row_to_usuario(row)}


@app.put("/usuarios/{usuario_id}")
def atualizar_usuario(usuario_id: int, dados: UsuarioAtualizacao) -> dict:
    campos = []
    valores = []

    if dados.nome is not None:
        campos.append("nome = ?")
        valores.append(dados.nome.strip())
    if dados.bio is not None:
        campos.append("bio = ?")
        valores.append(dados.bio.strip())
    if dados.foto_url is not None:
        campos.append("foto_url = ?")
        valores.append(str(dados.foto_url))

    if not campos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie ao menos um campo para atualizar.",
        )

    valores.append(usuario_id)

    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE usuarios SET {', '.join(campos)} WHERE id = ?",
            tuple(valores),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()

    return {"message": "Usuario atualizado com sucesso.", "usuario": row_to_usuario(row)}


@app.post("/avaliacoes", status_code=status.HTTP_201_CREATED)
def criar_avaliacao(dados: AvaliacaoCriacao) -> dict:
    agora = datetime.utcnow().isoformat()

    with get_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE id = ?", (dados.usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        cursor = conn.execute(
            """
            INSERT INTO avaliacoes
                (usuario_id, jogo_nome, jogo_capa_url, nota, plataforma, texto, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dados.usuario_id,
                dados.jogo_nome.strip(),
                dados.jogo_capa_url.strip() if dados.jogo_capa_url else None,
                dados.nota,
                dados.plataforma.strip() if dados.plataforma else None,
                dados.texto.strip(),
                agora,
                agora,
            ),
        )
        conn.commit()
        avaliacao_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM avaliacoes WHERE id = ?", (avaliacao_id,)).fetchone()

    return {"message": "Avaliacao criada com sucesso.", "avaliacao": row_to_avaliacao(row)}


@app.get("/avaliacoes")
def listar_avaliacoes(usuario_id: Optional[int] = None) -> dict:
    with get_connection() as conn:
        if usuario_id is not None:
            rows = conn.execute(
                """
                SELECT
                    avaliacoes.*,
                    usuarios.nome AS usuario_nome,
                    usuarios.foto_url AS usuario_foto_url
                FROM avaliacoes
                JOIN usuarios ON usuarios.id = avaliacoes.usuario_id
                WHERE usuario_id = ?
                ORDER BY avaliacoes.criado_em DESC
                """,
                (usuario_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT
                    avaliacoes.*,
                    usuarios.nome AS usuario_nome,
                    usuarios.foto_url AS usuario_foto_url
                FROM avaliacoes
                JOIN usuarios ON usuarios.id = avaliacoes.usuario_id
                ORDER BY avaliacoes.criado_em DESC
                """
            ).fetchall()

    return {"avaliacoes": [row_to_avaliacao(row) for row in rows]}


@app.get("/avaliacoes/{avaliacao_id}")
def obter_avaliacao(avaliacao_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                avaliacoes.*,
                usuarios.nome AS usuario_nome,
                usuarios.foto_url AS usuario_foto_url
            FROM avaliacoes
            JOIN usuarios ON usuarios.id = avaliacoes.usuario_id
            WHERE avaliacoes.id = ?
            """,
            (avaliacao_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliacao nao encontrada.",
        )

    return row_to_avaliacao(row)


@app.get("/usuarios/{usuario_id}/avaliacoes")
def listar_avaliacoes_do_usuario(usuario_id: int) -> dict:
    with get_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        rows = conn.execute(
            """
            SELECT
                avaliacoes.*,
                usuarios.nome AS usuario_nome,
                usuarios.foto_url AS usuario_foto_url
            FROM avaliacoes
            JOIN usuarios ON usuarios.id = avaliacoes.usuario_id
            WHERE avaliacoes.usuario_id = ?
            ORDER BY avaliacoes.criado_em DESC
            """,
            (usuario_id,),
        ).fetchall()

    return {"avaliacoes": [row_to_avaliacao(row) for row in rows]}


@app.put("/avaliacoes/{avaliacao_id}")
def atualizar_avaliacao(
    avaliacao_id: int,
    dados: AvaliacaoAtualizacao,
    usuario_id: Optional[int] = None,
) -> dict:
    campos = []
    valores = []

    if dados.jogo_nome is not None:
        campos.append("jogo_nome = ?")
        valores.append(dados.jogo_nome.strip())
    if dados.jogo_capa_url is not None:
        campos.append("jogo_capa_url = ?")
        valores.append(dados.jogo_capa_url.strip())
    if dados.nota is not None:
        campos.append("nota = ?")
        valores.append(dados.nota)
    if dados.plataforma is not None:
        campos.append("plataforma = ?")
        valores.append(dados.plataforma.strip())
    if dados.texto is not None:
        campos.append("texto = ?")
        valores.append(dados.texto.strip())

    if not campos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Envie ao menos um campo para atualizar.",
        )

    campos.append("atualizado_em = ?")
    valores.append(datetime.utcnow().isoformat())
    valores.append(avaliacao_id)

    with get_connection() as conn:
        if usuario_id is not None:
            dono = conn.execute(
                "SELECT id FROM avaliacoes WHERE id = ? AND usuario_id = ?",
                (avaliacao_id, usuario_id),
            ).fetchone()
            if dono is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Esta avaliacao nao pertence ao usuario informado.",
                )

        cursor = conn.execute(
            f"UPDATE avaliacoes SET {', '.join(campos)} WHERE id = ?",
            tuple(valores),
        )
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avaliacao nao encontrada.",
            )

        row = conn.execute("SELECT * FROM avaliacoes WHERE id = ?", (avaliacao_id,)).fetchone()

    return {"message": "Avaliacao atualizada com sucesso.", "avaliacao": row_to_avaliacao(row)}


@app.delete("/avaliacoes/{avaliacao_id}")
def excluir_avaliacao(avaliacao_id: int, usuario_id: Optional[int] = None) -> dict:
    with get_connection() as conn:
        if usuario_id is not None:
            dono = conn.execute(
                "SELECT id FROM avaliacoes WHERE id = ? AND usuario_id = ?",
                (avaliacao_id, usuario_id),
            ).fetchone()
            if dono is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Esta avaliacao nao pertence ao usuario informado.",
                )

        cursor = conn.execute("DELETE FROM avaliacoes WHERE id = ?", (avaliacao_id,))
        conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avaliacao nao encontrada.",
        )

    return {"message": "Avaliacao excluida com sucesso."}


@app.post("/desejos", status_code=status.HTTP_201_CREATED)
def criar_desejo(dados: DesejoCriacao) -> dict:
    agora = datetime.utcnow().isoformat()

    with get_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE id = ?", (dados.usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        try:
            cursor = conn.execute(
                """
                INSERT INTO desejos (usuario_id, jogo_nome, jogo_capa_url, criado_em)
                VALUES (?, ?, ?, ?)
                """,
                (
                    dados.usuario_id,
                    dados.jogo_nome.strip(),
                    dados.jogo_capa_url.strip(),
                    agora,
                ),
            )
            conn.commit()
            desejo_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            row = conn.execute(
                "SELECT * FROM desejos WHERE usuario_id = ? AND jogo_nome = ?",
                (dados.usuario_id, dados.jogo_nome.strip()),
            ).fetchone()
            return {"message": "Jogo ja esta na lista de desejo.", "desejo": row_to_desejo(row)}

        row = conn.execute("SELECT * FROM desejos WHERE id = ?", (desejo_id,)).fetchone()

    return {"message": "Jogo adicionado a lista de desejo.", "desejo": row_to_desejo(row)}


@app.get("/usuarios/{usuario_id}/desejos")
def listar_desejos_do_usuario(usuario_id: int) -> dict:
    with get_connection() as conn:
        usuario = conn.execute("SELECT id FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado.",
            )

        rows = conn.execute(
            "SELECT * FROM desejos WHERE usuario_id = ? ORDER BY criado_em DESC",
            (usuario_id,),
        ).fetchall()

    return {"desejos": [row_to_desejo(row) for row in rows]}


@app.delete("/desejos/{desejo_id}")
def excluir_desejo(desejo_id: int, usuario_id: Optional[int] = None) -> dict:
    with get_connection() as conn:
        if usuario_id is not None:
            dono = conn.execute(
                "SELECT id FROM desejos WHERE id = ? AND usuario_id = ?",
                (desejo_id, usuario_id),
            ).fetchone()
            if dono is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Este desejo nao pertence ao usuario informado.",
                )

        cursor = conn.execute("DELETE FROM desejos WHERE id = ?", (desejo_id,))
        conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desejo nao encontrado.",
        )

    return {"message": "Jogo removido da lista de desejo."}
