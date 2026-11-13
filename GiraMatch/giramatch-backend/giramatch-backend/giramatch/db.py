"""Acesso ao banco: SQLite (desenvolvimento/testes) ou PostgreSQL (produção).

O banco é escolhido pelo "endereço" passado a `conectar`:
  - caminho de arquivo (ex.: giramatch.db)            -> SQLite
  - postgres://usuario:senha@host:5432/banco          -> PostgreSQL

O restante do código usa sempre `?` como marcador e `cur.lastrowid`; esta camada traduz
isso para o PostgreSQL.
"""
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")
SCHEMA_PG = Path(__file__).with_name("schema_pg.sql")

# Tabelas com coluna `id` autogerada (as demais não devolvem lastrowid)
_TABELAS_COM_ID = {"orgaos", "usuarios", "demandas", "matches", "comites", "tarefas", "mensagens",
                    "ocorrencias", "ocorrencia_respostas"}
_INSERT = re.compile(r"^\s*INSERT\s+INTO\s+(\w+)", re.IGNORECASE)


def agora() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def eh_postgres(endereco: str) -> bool:
    return str(endereco).startswith(("postgres://", "postgresql://"))


class _Cursor:
    """Cursor mínimo, igual ao do sqlite3 para o que o projeto usa."""

    def __init__(self, cur, lastrowid=None):
        self._cur, self.lastrowid = cur, lastrowid

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def __iter__(self):
        return iter(self._cur)


class _ConexaoPG:
    def __init__(self, endereco: str):
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("Para usar PostgreSQL instale o driver: pip install 'psycopg[binary]'") from e
        self._conn = psycopg.connect(endereco, row_factory=dict_row, connect_timeout=10)

    def execute(self, sql: str, params=()):
        sql = sql.replace("%", "%%").replace("?", "%s")
        m = _INSERT.match(sql)
        com_id = bool(m) and m.group(1).lower() in _TABELAS_COM_ID and "returning" not in sql.lower()
        if com_id:
            sql += " RETURNING id"
        cur = self._conn.execute(sql, list(params))
        lastrowid = cur.fetchone()["id"] if com_id else None
        return _Cursor(cur, lastrowid)

    def executescript(self, script: str):
        self._conn.execute(script)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def conectar(endereco: str):
    if eh_postgres(endereco):
        return _ConexaoPG(endereco)
    conn = sqlite3.connect(endereco, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas(conn) -> None:
    arquivo = SCHEMA_PG if isinstance(conn, _ConexaoPG) else SCHEMA
    conn.executescript(arquivo.read_text(encoding="utf-8"))
    _migrar(conn)
    conn.commit()


def _migrar(conn) -> None:
    """Acrescenta colunas novas em bancos criados por versões anteriores."""
    if isinstance(conn, _ConexaoPG):
        conn.execute("ALTER TABLE comites ADD COLUMN IF NOT EXISTS data_fim_contrato TEXT")
    elif "data_fim_contrato" not in [r["name"] for r in conn.execute("PRAGMA table_info(comites)")]:
        conn.execute("ALTER TABLE comites ADD COLUMN data_fim_contrato TEXT")


def apagar_tudo(conn) -> None:
    """Apaga todas as tabelas (usado só pelo comando `demo`)."""
    tabelas = ["ocorrencia_respostas", "ocorrencias", "pontos", "mensagens", "tarefas", "comites", "decisoes", "matches", "demandas", "sessoes", "usuarios", "orgaos"]
    for t in tabelas:
        conn.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()


def banco_vazio(conn) -> bool:
    return conn.execute("SELECT COUNT(*) n FROM orgaos").fetchone()["n"] == 0


def linha(row):
    """Linha do banco -> dict (ou None)."""
    return dict(row) if row is not None else None


def carregar_json(texto, padrao=None):
    if texto in (None, ""):
        return padrao
    return json.loads(texto)


def para_json(valor) -> str:
    return json.dumps(valor, ensure_ascii=False)
