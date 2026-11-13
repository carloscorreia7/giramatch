"""Senhas e sessões (token Bearer)."""
import hashlib
import hmac
import secrets
import threading
import time
from datetime import datetime, timedelta, timezone

from . import config
from .db import agora

ITERACOES = 200_000


def gerar_hash(senha: str) -> str:
    sal = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal), ITERACOES)
    return f"pbkdf2_sha256${ITERACOES}${sal}${dk.hex()}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    try:
        _, iteracoes, sal, esperado = armazenado.split("$")
        dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(sal), int(iteracoes))
        return hmac.compare_digest(dk.hex(), esperado)
    except (ValueError, TypeError):
        return False


def criar_sessao(conn, usuario_id: int) -> dict:
    token = secrets.token_urlsafe(32)
    expira = (datetime.now(timezone.utc) + timedelta(hours=config.TOKEN_HORAS)).replace(microsecond=0)
    conn.execute(
        "INSERT INTO sessoes (token, usuario_id, criada_em, expira_em) VALUES (?, ?, ?, ?)",
        (token, usuario_id, agora(), expira.isoformat()),
    )
    return {"token": token, "expira_em": expira.isoformat()}


def usuario_do_token(conn, token: str):
    row = conn.execute(
        """SELECT u.id, u.nome, u.email, u.perfil, u.orgao_id, s.expira_em
             FROM sessoes s JOIN usuarios u ON u.id = s.usuario_id
            WHERE s.token = ?""",
        (token,),
    ).fetchone()
    if row is None:
        return None
    if datetime.fromisoformat(row["expira_em"]) < datetime.now(timezone.utc):
        conn.execute("DELETE FROM sessoes WHERE token = ?", (token,))
        return None
    return dict(row)


def encerrar_sessao(conn, token: str) -> None:
    conn.execute("DELETE FROM sessoes WHERE token = ?", (token,))


# --- Limite de tentativas de login (F-003) -----------------------------------
_falhas: dict = {}
_trava = threading.Lock()


def _recentes(chave: str, agora_s: float) -> list:
    lista = [t for t in _falhas.get(chave, []) if agora_s - t < config.LOGIN_JANELA_S]
    _falhas[chave] = lista
    return lista


def login_bloqueado(ip: str, email: str) -> bool:
    """True se ha falhas demais, para este IP+e-mail ou para este IP, dentro da janela."""
    agora_s = time.monotonic()
    with _trava:
        return (len(_recentes(f"{ip}|{email}", agora_s)) >= config.LOGIN_MAX_FALHAS
                or len(_recentes(f"{ip}|*", agora_s)) >= config.LOGIN_MAX_FALHAS_IP)


def registrar_falha_login(ip: str, email: str) -> None:
    agora_s = time.monotonic()
    with _trava:
        _falhas.setdefault(f"{ip}|{email}", []).append(agora_s)
        _falhas.setdefault(f"{ip}|*", []).append(agora_s)


def limpar_falhas_login(ip: str = None, email: str = None) -> None:
    """Sem argumentos, zera tudo (usado nos testes). Com IP e e-mail, zera so aquele par apos um login valido."""
    with _trava:
        if ip is None:
            _falhas.clear()
        else:
            _falhas.pop(f"{ip}|{email}", None)
