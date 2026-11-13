"""Linha de comando do GiraMatch.

Com a variável DATABASE_URL definida (postgres://...), usa PostgreSQL; senão, SQLite local.

    python -m giramatch iniciar          # cria o banco vazio
    python -m giramatch demo             # recria o banco com dados de demonstração
    python -m giramatch servir           # sobe a API em http://127.0.0.1:8000
    python -m giramatch usuario --orgao TJPB --nome "Maria" --email maria@tjpb.jus.br --senha "..."
"""
import argparse
import os

from . import config
from .api import criar_servidor
from .db import apagar_tudo, banco_vazio, conectar, criar_tabelas, eh_postgres
from .auth import gerar_hash
from .seed import SENHA_DEMO, popular


def salvar_usuario(conn, orgao: str, nome: str, email: str, senha: str, perfil: str = "gestor") -> str:
    """Cria (ou atualiza a senha de) um usuário de um órgão já cadastrado. Levanta ValueError se inválido."""
    if len(senha) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    if perfil not in {"gestor", "fiscal"}:
        raise ValueError("O perfil deve ser 'gestor' ou 'fiscal'.")
    org = conn.execute("SELECT id FROM orgaos WHERE lower(sigla) = lower(?)", (orgao,)).fetchone()
    if org is None and perfil == "fiscal":  # o órgão de fiscalização é criado quando ainda não existe
        cur = conn.execute(
            "INSERT INTO orgaos (sigla, nome, ramo, esfera, uf, municipio, cooperado) VALUES (?, ?, ?, ?, ?, ?, 0)",
            (orgao.upper(), "Fiscalização das Contratações", "fiscalizacao", "federal", "PB", "João Pessoa"))
        org = {"id": cur.lastrowid}
    if org is None:
        siglas = ", ".join(r["sigla"] for r in conn.execute("SELECT sigla FROM orgaos ORDER BY sigla"))
        raise ValueError(f"Órgão '{orgao}' não encontrado. Órgãos cadastrados: {siglas or '(nenhum — rode o comando demo)'}")
    email = email.strip().lower()
    existe = conn.execute("SELECT id FROM usuarios WHERE lower(email) = ?", (email,)).fetchone()
    if existe:
        conn.execute("UPDATE usuarios SET senha_hash = ?, nome = ?, orgao_id = ?, perfil = ? WHERE id = ?",
                     (gerar_hash(senha), nome, org["id"], perfil, existe["id"]))
        msg = f"Usuário {email} atualizado."
    else:
        conn.execute("INSERT INTO usuarios (orgao_id, nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?, ?)",
                     (org["id"], nome, email, gerar_hash(senha), perfil))
        msg = f"Usuário {email} criado no órgão {orgao}."
    conn.commit()
    return msg


def criar_usuarios_do_ambiente(conn) -> None:
    """Lê GIRAMATCH_USUARIOS: 'ORGAO|Nome|email|senha[|perfil]' separados por ';' (perfil: gestor ou fiscal)."""
    for item in filter(None, (x.strip() for x in config.USUARIOS_ENV.split(";"))):
        partes = [p.strip() for p in item.split("|")]
        try:
            if len(partes) not in (4, 5):
                raise ValueError("formato esperado: ORGAO|Nome|email|senha[|perfil]")
            print(salvar_usuario(conn, *partes))
        except ValueError as e:
            conn.rollback()
            print(f"Usuário ignorado ({partes[2] if len(partes) > 2 else '?'}): {e}")


def main():
    p = argparse.ArgumentParser(prog="giramatch", description="Backend do GiraMatch")
    p.add_argument("--db", default=config.DB_PATH, help="arquivo do banco SQLite")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("iniciar", help="cria as tabelas")
    sub.add_parser("demo", help="apaga o banco e carrega dados de demonstração")
    u = sub.add_parser("usuario", help="cria (ou atualiza a senha de) um usuário de um órgão já cadastrado")
    u.add_argument("--orgao", required=True, help="sigla do órgão, ex.: TJPB")
    u.add_argument("--nome", required=True)
    u.add_argument("--email", required=True)
    u.add_argument("--senha", required=True)
    u.add_argument("--perfil", default="gestor", choices=["gestor", "fiscal"], help="fiscal = acompanha todos os comitês e registra ocorrências")
    s = sub.add_parser("servir", help="sobe a API")
    s.add_argument("--host", default=config.HOST)
    s.add_argument("--porta", type=int, default=config.PORT)
    args = p.parse_args()

    if args.comando == "demo" and eh_postgres(args.db) and os.environ.get("GIRAMATCH_PERMITIR_DEMO") != "1":
        raise SystemExit("O comando demo APAGA todo o banco PostgreSQL. Para confirmar, defina GIRAMATCH_PERMITIR_DEMO=1.")
    if args.comando == "demo" and not eh_postgres(args.db) and os.path.exists(args.db):
        os.remove(args.db)

    conn = conectar(args.db)
    if args.comando == "demo" and eh_postgres(args.db):
        apagar_tudo(conn)
    criar_tabelas(conn)

    if args.comando == "iniciar":
        print(f"Banco pronto em {args.db}")
    elif args.comando == "demo":
        r = popular(conn)
        print(f"Banco de demonstração criado em {args.db}: {r['criados']} matches sugeridos.")
        print(f"Login: gestor@trepb.giramatch.demo / senha {SENHA_DEMO} (troque 'trepb' por trt13, jfpb, tjpb, trern)")
        print(f"Fiscalização: fiscal@giramatch.demo / senha {SENHA_DEMO}")
    elif args.comando == "usuario":
        try:
            msg = salvar_usuario(conn, args.orgao, args.nome, args.email, args.senha, args.perfil)
        except ValueError as e:
            conn.close()
            raise SystemExit(str(e))
        print(msg)
    elif args.comando == "servir":
        if config.DEMO_SE_VAZIO and banco_vazio(conn):
            r = popular(conn)
            print(f"Banco vazio: dados de demonstração carregados ({r['criados']} matches).")
        criar_usuarios_do_ambiente(conn)
        conn.close()
        if eh_postgres(args.db) and config.CORS_ORIGEM == "*":
            print("AVISO: GIRAMATCH_CORS=* aceita qualquer site. Defina o endereco do seu site (F-004).")
        srv = criar_servidor(args.db, args.host, args.porta)
        print(f"GiraMatch API em http://{args.host}:{args.porta}/api/health  (banco: {'PostgreSQL' if eh_postgres(args.db) else args.db})")
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrado.")
        return
    conn.close()


if __name__ == "__main__":
    main()
