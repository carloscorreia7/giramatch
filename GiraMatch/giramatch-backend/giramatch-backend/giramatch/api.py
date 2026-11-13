"""API REST do GiraMatch (somente biblioteca padrão do Python)."""
import csv
import io
import json
import re
import sys
import traceback
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import __version__, auth, config
from .db import agora, carregar_json, conectar, linha, para_json
from .matching import gerar_matches

MAX_CORPO = 2 * 1024 * 1024
NATUREZAS = {"contratacao", "capacitacao", "outra"}
TIPOS = {"material", "servico", "capacitacao", "outro"}
AVISO_IA = (
    "Sugestões geradas automaticamente para apoiar a decisão. "
    "A decisão de cooperar é sempre dos gestores."
)


class ApiError(Exception):
    def __init__(self, status: int, mensagem: str, detalhes=None):
        super().__init__(mensagem)
        self.status, self.mensagem, self.detalhes = status, mensagem, detalhes


# ---------------------------------------------------------------------------
# Roteador
# ---------------------------------------------------------------------------
ROTAS = []


def rota(metodo: str, padrao: str, publica: bool = False):
    regex = re.compile("^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[0-9]+)", padrao) + "$")

    def registrar(func):
        ROTAS.append((metodo, regex, func, publica))
        return func

    return registrar


def eh_fiscal(ctx) -> bool:
    return ctx.usuario["perfil"] == "fiscal"


def exigir_gestor(ctx) -> None:
    if eh_fiscal(ctx):
        raise ApiError(403, "O perfil de fiscalização é somente leitura nos comitês: registre uma ocorrência.")


def exigir_fiscal(ctx) -> None:
    if not eh_fiscal(ctx):
        raise ApiError(403, "Somente o perfil de fiscalização pode fazer isso.")


# O fiscal só enxerga comitês, ocorrências e a própria sessão (o restante é dos órgãos cooperados).
FISCAL_PERMITIDAS = [
    ("GET", re.compile(r"^/api/(me|comites(/\d+)?|ocorrencias)$")),
    ("POST", re.compile(r"^/api/(auth/logout|comites/\d+/ocorrencias|ocorrencias/\d+/respostas)$")),
    ("PATCH", re.compile(r"^/api/ocorrencias/\d+$")),
]


def fiscal_pode(metodo: str, caminho: str) -> bool:
    return any(m == metodo and r.match(caminho) for m, r in FISCAL_PERMITIDAS)


class Contexto:
    def __init__(self, conn, usuario, params, query, corpo, tipo_conteudo, token, ip=""):
        self.conn, self.usuario, self.params, self.query = conn, usuario, params, query
        self.ip = ip
        self.corpo, self.tipo_conteudo, self.token = corpo, tipo_conteudo, token

    @property
    def orgao_id(self) -> int:
        return self.usuario["orgao_id"]

    def json(self) -> dict:
        if not self.corpo:
            return {}
        try:
            dados = json.loads(self.corpo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError(400, "Corpo da requisição não é um JSON válido.")
        if not isinstance(dados, dict):
            raise ApiError(400, "O corpo deve ser um objeto JSON.")
        return dados

    def q(self, nome, padrao=None):
        valores = self.query.get(nome)
        return valores[0] if valores else padrao


# ---------------------------------------------------------------------------
# Apresentação (o que cada órgão pode ver)
# ---------------------------------------------------------------------------
def orgao_resumo(conn, orgao_id):
    o = linha(conn.execute("SELECT id, sigla, nome, ramo, esfera, uf, municipio FROM orgaos WHERE id = ?",
                           (orgao_id,)).fetchone())
    return o


def ver_demanda(conn, d: dict, viewer_orgao_id: int) -> dict:
    d = dict(d)
    d["criterios_sustentaveis"] = carregar_json(d["criterios_sustentaveis"], []) \
        if isinstance(d["criterios_sustentaveis"], str) else d["criterios_sustentaveis"]
    d["valor_sigiloso"] = bool(d["valor_sigiloso"])
    if d["valor_sigiloso"] and d["orgao_id"] != viewer_orgao_id:
        d["valor_estimado"] = None  # orçamento sigiloso: só o próprio órgão vê
    d["orgao"] = orgao_resumo(conn, d["orgao_id"])
    for chave in ("sigla", "esfera", "orgao_uf", "orgao_municipio"):
        d.pop(chave, None)
    return d


def buscar_match(conn, match_id: int):
    m = linha(conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone())
    if m is None:
        raise ApiError(404, "Match não encontrado.")
    return m


def lados(conn, m: dict, orgao_id: int):
    a = linha(conn.execute("SELECT * FROM demandas WHERE id = ?", (m["demanda_a_id"],)).fetchone())
    b = linha(conn.execute("SELECT * FROM demandas WHERE id = ?", (m["demanda_b_id"],)).fetchone())
    if a["orgao_id"] == orgao_id:
        return a, b
    if b["orgao_id"] == orgao_id:
        return b, a
    raise ApiError(404, "Match não encontrado.")  # não revela matches de terceiros


def ver_match(conn, m: dict, orgao_id: int) -> dict:
    minha, outra = lados(conn, m, orgao_id)
    decisao = conn.execute("SELECT decisao FROM decisoes WHERE match_id = ? AND orgao_id = ?",
                           (m["id"], orgao_id)).fetchone()
    comite = conn.execute("SELECT id FROM comites WHERE match_id = ?", (m["id"],)).fetchone()
    # Pedido recebido: o outro órgão já clicou em "Conectar" e este ainda não respondeu.
    # (Só o "Conectar" é revelado; uma recusa do outro lado nunca aparece.)
    dec_outro = conn.execute("SELECT decisao FROM decisoes WHERE match_id = ? AND orgao_id = ?",
                             (m["id"], outra["orgao_id"])).fetchone()
    pedido_recebido = bool(dec_outro and dec_outro["decisao"] == "conectar"
                           and m["status"] == "sugerido" and decisao is None)
    return {
        "id": m["id"],
        "score": m["score"],
        "status": m["status"],
        "minha_demanda": ver_demanda(conn, minha, orgao_id),
        "outra_demanda": ver_demanda(conn, outra, orgao_id),
        "componentes": carregar_json(m["componentes"], {}),
        "motivos": carregar_json(m["motivos"], []),
        "caminho": carregar_json(m["caminho"], {}),
        "alertas": carregar_json(m["alertas"], []),
        "volume_total": m["volume_total"],
        "economia_pct": m["economia_pct"],
        "economia_valor": m["economia_valor"],
        "minha_decisao": decisao["decisao"] if decisao else None,
        "pedido_recebido": pedido_recebido,
        "comite_id": comite["id"] if comite else None,
        "atualizado_em": m["atualizado_em"],
    }


# ---------------------------------------------------------------------------
# Validação de demandas
# ---------------------------------------------------------------------------
def _numero(valor, campo, obrigatorio=False, positivo=False):
    if valor in (None, ""):
        if obrigatorio:
            raise ApiError(422, f"O campo '{campo}' é obrigatório.")
        return None
    try:
        n = float(str(valor).replace(",", ".")) if isinstance(valor, str) else float(valor)
    except (TypeError, ValueError):
        raise ApiError(422, f"O campo '{campo}' deve ser numérico.")
    if positivo and n <= 0:
        raise ApiError(422, f"O campo '{campo}' deve ser maior que zero.")
    return n


def validar_demanda(dados: dict, parcial: dict = None) -> dict:
    base = dict(parcial or {})
    base.update({k: v for k, v in dados.items() if k in CAMPOS_DEMANDA})
    d = {}
    d["descricao"] = str(base.get("descricao") or "").strip()
    if not d["descricao"]:
        raise ApiError(422, "O campo 'descricao' é obrigatório.")
    d["natureza"] = base.get("natureza") or "contratacao"
    if d["natureza"] not in NATUREZAS:
        raise ApiError(422, f"'natureza' deve ser uma de: {', '.join(sorted(NATUREZAS))}.")
    d["tipo"] = base.get("tipo") or ("capacitacao" if d["natureza"] == "capacitacao" else "material")
    if d["tipo"] not in TIPOS:
        raise ApiError(422, f"'tipo' deve ser um de: {', '.join(sorted(TIPOS))}.")
    ano = _numero(base.get("ano"), "ano", obrigatorio=True)
    if not 2000 <= ano <= 2100:
        raise ApiError(422, "'ano' inválido.")
    d["ano"] = int(ano)
    mes = _numero(base.get("mes_previsto"), "mes_previsto", obrigatorio=True)
    if not 1 <= mes <= 12:
        raise ApiError(422, "'mes_previsto' deve estar entre 1 e 12.")
    d["mes_previsto"] = int(mes)
    d["quantidade"] = _numero(base.get("quantidade", 1), "quantidade", obrigatorio=True, positivo=True)
    d["unidade"] = str(base.get("unidade") or "un").strip()
    d["valor_estimado"] = _numero(base.get("valor_estimado"), "valor_estimado")
    sig = base.get("valor_sigiloso", False)
    d["valor_sigiloso"] = 1 if (sig is True or str(sig).strip().lower() in {"1", "true", "sim", "s"}) else 0
    for campo in ("codigo_catalogo", "categoria", "municipio", "uf"):
        v = base.get(campo)
        d[campo] = str(v).strip() if v not in (None, "") else None
    fim = base.get("fim_contrato_atual")
    if fim in (None, ""):
        d["fim_contrato_atual"] = None
    else:
        try:
            d["fim_contrato_atual"] = date.fromisoformat(str(fim)).isoformat()
        except ValueError:
            raise ApiError(422, "'fim_contrato_atual' deve estar no formato AAAA-MM-DD.")
    crit = base.get("criterios_sustentaveis") or []
    if isinstance(crit, str):
        crit = carregar_json(crit, []) if crit.strip().startswith("[") else [c for c in crit.split("|")]
    if not isinstance(crit, list):
        raise ApiError(422, "'criterios_sustentaveis' deve ser uma lista de textos.")
    d["criterios_sustentaveis"] = para_json([str(c).strip() for c in crit if str(c).strip()])
    return d


CAMPOS_DEMANDA = {
    "ano", "natureza", "tipo", "codigo_catalogo", "categoria", "descricao", "quantidade", "unidade",
    "valor_estimado", "valor_sigiloso", "mes_previsto", "municipio", "uf", "fim_contrato_atual",
    "criterios_sustentaveis",
}


def inserir_demanda(conn, orgao_id: int, d: dict, origem="manual") -> int:
    ts = agora()
    colunas = list(d.keys()) + ["orgao_id", "origem", "criada_em", "atualizada_em"]
    valores = list(d.values()) + [orgao_id, origem, ts, ts]
    cur = conn.execute(
        f"INSERT INTO demandas ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))})", valores
    )
    return cur.lastrowid


def minha_demanda(ctx, demanda_id: int) -> dict:
    d = linha(ctx.conn.execute("SELECT * FROM demandas WHERE id = ? AND orgao_id = ?",
                               (demanda_id, ctx.orgao_id)).fetchone())
    if d is None:
        raise ApiError(404, "Demanda não encontrada.")
    return d


# ---------------------------------------------------------------------------
# Rotas: sistema e autenticação
# ---------------------------------------------------------------------------
@rota("GET", "/api/health", publica=True)
def health(ctx):
    return {"status": "ok", "versao": __version__}


@rota("POST", "/api/auth/login", publica=True)
def login(ctx):
    dados = ctx.json()
    email = str(dados.get("email") or "").strip().lower()
    senha = str(dados.get("senha") or "")
    if auth.login_bloqueado(ctx.ip, email):
        raise ApiError(429, "Muitas tentativas de login. Aguarde alguns minutos e tente novamente.")
    u = ctx.conn.execute("SELECT * FROM usuarios WHERE lower(email) = ?", (email,)).fetchone()
    if u is None or not auth.verificar_senha(senha, u["senha_hash"]):
        auth.registrar_falha_login(ctx.ip, email)
        raise ApiError(401, "E-mail ou senha incorretos.")
    auth.limpar_falhas_login(ctx.ip, email)
    sessao = auth.criar_sessao(ctx.conn, u["id"])
    return {
        **sessao,
        "usuario": {"id": u["id"], "nome": u["nome"], "email": u["email"], "perfil": u["perfil"]},
        "orgao": orgao_resumo(ctx.conn, u["orgao_id"]),
    }


@rota("POST", "/api/auth/logout")
def logout(ctx):
    auth.encerrar_sessao(ctx.conn, ctx.token)
    return {"ok": True}


@rota("GET", "/api/me")
def me(ctx):
    u = ctx.usuario
    return {"usuario": {k: u[k] for k in ("id", "nome", "email", "perfil")},
            "orgao": orgao_resumo(ctx.conn, u["orgao_id"])}


@rota("GET", "/api/orgaos")
def listar_orgaos(ctx):
    rows = ctx.conn.execute("SELECT id, sigla, nome, ramo, esfera, uf, municipio, cooperado FROM orgaos ORDER BY sigla")
    return {"orgaos": [dict(r) | {"cooperado": bool(r["cooperado"])} for r in rows]}


# ---------------------------------------------------------------------------
# Rotas: demandas (PCA, capacitações...)
# ---------------------------------------------------------------------------
@rota("GET", "/api/demandas")
def listar_demandas(ctx):
    sql, args = "SELECT * FROM demandas WHERE orgao_id = ?", [ctx.orgao_id]
    if ctx.q("ano"):
        sql += " AND ano = ?"
        args.append(int(ctx.q("ano")))
    if ctx.q("natureza"):
        sql += " AND natureza = ?"
        args.append(ctx.q("natureza"))
    sql += " ORDER BY ano, mes_previsto, id"
    return {"demandas": [ver_demanda(ctx.conn, dict(r), ctx.orgao_id) for r in ctx.conn.execute(sql, args)]}


@rota("POST", "/api/demandas")
def criar_demanda(ctx):
    d = validar_demanda(ctx.json())
    novo_id = inserir_demanda(ctx.conn, ctx.orgao_id, d)
    resultado = gerar_matches(ctx.conn, orgao_id=ctx.orgao_id, ano=d["ano"])
    return 201, {"demanda": ver_demanda(ctx.conn, minha_demanda(ctx, novo_id), ctx.orgao_id),
                 "matches": resultado}


@rota("GET", "/api/demandas/{id}")
def obter_demanda(ctx):
    return {"demanda": ver_demanda(ctx.conn, minha_demanda(ctx, int(ctx.params["id"])), ctx.orgao_id)}


@rota("PUT", "/api/demandas/{id}")
def atualizar_demanda(ctx):
    atual = minha_demanda(ctx, int(ctx.params["id"]))
    d = validar_demanda(ctx.json(), parcial=atual)
    sets = ", ".join(f"{k} = ?" for k in d) + ", atualizada_em = ?"
    ctx.conn.execute(f"UPDATE demandas SET {sets} WHERE id = ?", (*d.values(), agora(), atual["id"]))
    resultado = gerar_matches(ctx.conn, orgao_id=ctx.orgao_id, ano=d["ano"])
    return {"demanda": ver_demanda(ctx.conn, minha_demanda(ctx, atual["id"]), ctx.orgao_id),
            "matches": resultado}


@rota("DELETE", "/api/demandas/{id}")
def excluir_demanda(ctx):
    atual = minha_demanda(ctx, int(ctx.params["id"]))
    conectado = ctx.conn.execute(
        "SELECT 1 FROM matches WHERE status = 'conectado' AND (demanda_a_id = ? OR demanda_b_id = ?)",
        (atual["id"], atual["id"]),
    ).fetchone()
    if conectado:
        raise ApiError(409, "Esta demanda já tem um comitê de cooperação ativo e não pode ser excluída.")
    ctx.conn.execute("DELETE FROM demandas WHERE id = ?", (atual["id"],))
    return {"ok": True}


@rota("POST", "/api/demandas/importar")
def importar_demandas(ctx):
    """Importa o PCA em CSV (separador ';' ou ',', primeira linha com os nomes das colunas)."""
    try:
        texto = ctx.corpo.decode("utf-8-sig")
    except UnicodeDecodeError:
        texto = ctx.corpo.decode("latin-1")
    if not texto.strip():
        raise ApiError(400, "Envie o conteúdo do CSV no corpo da requisição.")
    primeira = texto.splitlines()[0]
    separador = ";" if primeira.count(";") >= primeira.count(",") else ","
    leitor = csv.DictReader(io.StringIO(texto), delimiter=separador)
    importadas, erros, anos = [], [], set()
    for n, registro in enumerate(leitor, start=2):
        registro = {(k or "").strip(): (v or "").strip() for k, v in registro.items()}
        try:
            d = validar_demanda(registro)
        except ApiError as e:
            erros.append({"linha": n, "erro": e.mensagem})
            continue
        importadas.append(inserir_demanda(ctx.conn, ctx.orgao_id, d, origem="csv"))
        anos.add(d["ano"])
    resultado = {"criados": 0, "atualizados": 0, "removidos": 0}
    for ano in anos:
        for k, v in gerar_matches(ctx.conn, orgao_id=ctx.orgao_id, ano=ano).items():
            resultado[k] += v
    return 201 if importadas else 200, {"importadas": len(importadas), "erros": erros, "matches": resultado}


# ---------------------------------------------------------------------------
# Rotas: matches
# ---------------------------------------------------------------------------
@rota("POST", "/api/matches/gerar")
def regerar(ctx):
    return {"matches": gerar_matches(ctx.conn, orgao_id=ctx.orgao_id)}


@rota("GET", "/api/matches")
def listar_matches(ctx):
    sql = """SELECT m.* FROM matches m
               JOIN demandas a ON a.id = m.demanda_a_id
               JOIN demandas b ON b.id = m.demanda_b_id
              WHERE (a.orgao_id = ? OR b.orgao_id = ?)"""
    args = [ctx.orgao_id, ctx.orgao_id]
    status = ctx.q("status")
    if status:
        sql += " AND m.status = ?"
        args.append(status)
    if str(ctx.q("pendentes", "")).lower() in {"1", "true", "sim"}:
        # O "feed" para avaliar: sugestões que este órgão ainda não respondeu
        sql += """ AND m.status = 'sugerido'
                   AND NOT EXISTS (SELECT 1 FROM decisoes x WHERE x.match_id = m.id AND x.orgao_id = ?)"""
        args.append(ctx.orgao_id)
    sql += " ORDER BY m.score DESC, m.id"
    itens = [ver_match(ctx.conn, dict(r), ctx.orgao_id) for r in ctx.conn.execute(sql, args)]
    return {"matches": itens, "total": len(itens), "aviso": AVISO_IA}


@rota("GET", "/api/matches/{id}")
def obter_match(ctx):
    return {"match": ver_match(ctx.conn, buscar_match(ctx.conn, int(ctx.params["id"])), ctx.orgao_id),
            "aviso": AVISO_IA}


def _primeiro_dia(ano: int, mes: int, deslocamento: int) -> str:
    total = ano * 12 + (mes - 1) + deslocamento
    return date(total // 12, total % 12 + 1, 1).isoformat()


def criar_comite(conn, m: dict) -> int:
    a = linha(conn.execute("SELECT * FROM demandas WHERE id = ?", (m["demanda_a_id"],)).fetchone())
    b = linha(conn.execute("SELECT * FROM demandas WHERE id = ?", (m["demanda_b_id"],)).fetchone())
    caminho = carregar_json(m["caminho"], {})
    gerenciador = conn.execute("SELECT id FROM orgaos WHERE sigla = ?", (caminho.get("gerenciador"),)).fetchone()
    gid = gerenciador["id"] if gerenciador else a["orgao_id"]
    cur = conn.execute(
        "INSERT INTO comites (match_id, nome, gerenciador_orgao_id, criado_em) VALUES (?, ?, ?, ?)",
        (m["id"], f"Comitê de cooperação — {a['descricao']}", gid, agora()),
    )
    comite_id = cur.lastrowid
    ano, mes = a["ano"], min(a["mes_previsto"], b["mes_previsto"])
    if caminho.get("modelo") == "capacitacao_compartilhada":
        passos = [
            ("Definir conteúdo, formato e número de vagas", None, -2),
            ("Formalizar no acordo de cooperação técnica", gid, -1),
            ("Realizar a capacitação compartilhada", gid, 0),
        ]
    else:
        passos = [
            ("Alinhar especificação técnica e critérios sustentáveis", None, -3),
            ("Elaborar ETP e termo de referência conjuntos", gid, -2),
            ("Publicar a IRP (prazo mínimo de 8 dias úteis)", gid, -1),
            ("Realizar a licitação", gid, 0),
            ("Assinar a ata e emitir o contrato de cada órgão", None, 1),
        ]
    for ordem, (titulo, resp, desloc) in enumerate(passos, start=1):
        conn.execute(
            "INSERT INTO tarefas (comite_id, ordem, titulo, responsavel_orgao_id, prazo) VALUES (?, ?, ?, ?, ?)",
            (comite_id, ordem, titulo, resp, _primeiro_dia(ano, mes, desloc)),
        )
    return comite_id


# ---------------------------------------------------------------------------
# Incentivos: pontuação das instituições por match conectado
# ---------------------------------------------------------------------------
PONTOS_BASE = 100          # todo match conectado vale 100 pontos para cada órgão
PONTOS_POR_MIL = 1         # +1 ponto a cada R$ 1.000 de economia estimada...
PONTOS_BONUS_MAX = 100     # ...limitado a 100 pontos de bônus


def calcular_pontos(economia_valor) -> tuple:
    """(pontos, motivo) que cada órgão ganha por um match conectado."""
    bonus = min(int((economia_valor or 0) // 1000) * PONTOS_POR_MIL, PONTOS_BONUS_MAX)
    motivo = "Match conectado" + (f" + bônus de economia ({bonus})" if bonus else "")
    return PONTOS_BASE + bonus, motivo


def conceder_pontos(conn, m: dict) -> None:
    """Credita os pontos aos dois órgãos do match (idempotente)."""
    pts, motivo = calcular_pontos(m.get("economia_valor"))
    for col in ("demanda_a_id", "demanda_b_id"):
        oid = conn.execute("SELECT orgao_id FROM demandas WHERE id = ?", (m[col],)).fetchone()["orgao_id"]
        if conn.execute("SELECT 1 FROM pontos WHERE match_id = ? AND orgao_id = ?", (m["id"], oid)).fetchone():
            continue
        conn.execute("INSERT INTO pontos (match_id, orgao_id, pontos, motivo, criado_em) VALUES (?, ?, ?, ?, ?)",
                     (m["id"], oid, pts, motivo, agora()))


def total_pontos(conn, orgao_id=None) -> int:
    sql, args = "SELECT COALESCE(SUM(pontos), 0) t FROM pontos", []
    if orgao_id is not None:
        sql, args = sql + " WHERE orgao_id = ?", [orgao_id]
    return int(conn.execute(sql, args).fetchone()["t"])


@rota("POST", "/api/matches/{id}/decisao")
def decidir(ctx):
    m = buscar_match(ctx.conn, int(ctx.params["id"]))
    _, outra = lados(ctx.conn, m, ctx.orgao_id)
    decisao = str(ctx.json().get("decisao") or "").lower()
    if decisao not in {"conectar", "recusar"}:
        raise ApiError(422, "'decisao' deve ser 'conectar' ou 'recusar'.")
    if m["status"] != "sugerido":
        raise ApiError(409, f"Este match já está '{m['status']}'.")
    ctx.conn.execute(
        """INSERT INTO decisoes (match_id, orgao_id, usuario_id, decisao, decidido_em) VALUES (?, ?, ?, ?, ?)
           ON CONFLICT (match_id, orgao_id) DO UPDATE SET decisao = excluded.decisao,
                  usuario_id = excluded.usuario_id, decidido_em = excluded.decidido_em""",
        (m["id"], ctx.orgao_id, ctx.usuario["id"], decisao, agora()),
    )
    deu_match = False
    if decisao == "recusar":
        ctx.conn.execute("UPDATE matches SET status = 'recusado', atualizado_em = ? WHERE id = ?", (agora(), m["id"]))
    else:
        outro = ctx.conn.execute("SELECT decisao FROM decisoes WHERE match_id = ? AND orgao_id = ?",
                                 (m["id"], outra["orgao_id"])).fetchone()
        if outro and outro["decisao"] == "conectar":
            ctx.conn.execute("UPDATE matches SET status = 'conectado', atualizado_em = ? WHERE id = ?",
                             (agora(), m["id"]))
            criar_comite(ctx.conn, m)
            conceder_pontos(ctx.conn, m)
            deu_match = True
    atualizado = buscar_match(ctx.conn, m["id"])
    resp = {"deu_match": deu_match, "match": ver_match(ctx.conn, atualizado, ctx.orgao_id)}
    if deu_match:
        resp["pontos_ganhos"] = calcular_pontos(m.get("economia_valor"))[0]
    return resp


# ---------------------------------------------------------------------------
# Rotas: comitês de cooperação
# ---------------------------------------------------------------------------
def meu_comite(ctx, comite_id: int) -> dict:
    c = linha(ctx.conn.execute("SELECT * FROM comites WHERE id = ?", (comite_id,)).fetchone())
    if c is None:
        raise ApiError(404, "Comitê não encontrado.")
    if not eh_fiscal(ctx):  # o fiscal acompanha todos os comitês
        lados(ctx.conn, buscar_match(ctx.conn, c["match_id"]), ctx.orgao_id)  # checa acesso
    return c


def ver_comite(ctx, c: dict, completo=True) -> dict:
    m = buscar_match(ctx.conn, c["match_id"])
    if eh_fiscal(ctx):
        minha, outra = (linha(ctx.conn.execute("SELECT * FROM demandas WHERE id = ?", (m[col],)).fetchone())
                        for col in ("demanda_a_id", "demanda_b_id"))
    else:
        minha, outra = lados(ctx.conn, m, ctx.orgao_id)
    dados = {
        "id": c["id"],
        "nome": c["nome"],
        "match_id": c["match_id"],
        "gerenciador": orgao_resumo(ctx.conn, c["gerenciador_orgao_id"]),
        "membros": [orgao_resumo(ctx.conn, minha["orgao_id"]), orgao_resumo(ctx.conn, outra["orgao_id"])],
        "criado_em": c["criado_em"],
        "data_fim_contrato": c.get("data_fim_contrato"),
        "ocorrencias_abertas": ctx.conn.execute(
            "SELECT COUNT(*) n FROM ocorrencias WHERE comite_id = ? AND status <> 'resolvida'", (c["id"],)).fetchone()["n"],
    }
    if completo:
        dados["tarefas"] = [
            dict(r) | {"concluida": bool(r["concluida"])}
            for r in ctx.conn.execute("SELECT * FROM tarefas WHERE comite_id = ? ORDER BY ordem", (c["id"],))
        ]
        dados["mensagens"] = [
            dict(r) for r in ctx.conn.execute(
                """SELECT ms.id, ms.texto, ms.enviada_em, u.nome AS autor, o.sigla AS orgao
                     FROM mensagens ms JOIN usuarios u ON u.id = ms.usuario_id JOIN orgaos o ON o.id = u.orgao_id
                    WHERE ms.comite_id = ? ORDER BY ms.id""", (c["id"],))
        ]
        if not eh_fiscal(ctx):  # visão do fiscal não passa pelo filtro de valores sigilosos de cada órgão
            dados["match"] = ver_match(ctx.conn, m, ctx.orgao_id)
    return dados


@rota("GET", "/api/comites")
def listar_comites(ctx):
    if eh_fiscal(ctx):
        rows = ctx.conn.execute("SELECT * FROM comites ORDER BY id DESC")
        return {"comites": [ver_comite(ctx, dict(r), completo=False) for r in rows]}
    rows = ctx.conn.execute(
        """SELECT c.* FROM comites c JOIN matches m ON m.id = c.match_id
             JOIN demandas a ON a.id = m.demanda_a_id JOIN demandas b ON b.id = m.demanda_b_id
            WHERE a.orgao_id = ? OR b.orgao_id = ? ORDER BY c.id DESC""",
        (ctx.orgao_id, ctx.orgao_id),
    )
    return {"comites": [ver_comite(ctx, dict(r), completo=False) for r in rows]}


@rota("GET", "/api/comites/{id}")
def obter_comite(ctx):
    return {"comite": ver_comite(ctx, meu_comite(ctx, int(ctx.params["id"])))}


@rota("POST", "/api/comites/{id}/mensagens")
def enviar_mensagem(ctx):
    exigir_gestor(ctx)
    c = meu_comite(ctx, int(ctx.params["id"]))
    texto = str(ctx.json().get("texto") or "").strip()
    if not texto:
        raise ApiError(422, "A mensagem não pode ser vazia.")
    if len(texto) > 4000:
        raise ApiError(422, "A mensagem pode ter no máximo 4000 caracteres.")
    cur = ctx.conn.execute("INSERT INTO mensagens (comite_id, usuario_id, texto, enviada_em) VALUES (?, ?, ?, ?)",
                           (c["id"], ctx.usuario["id"], texto, agora()))
    return 201, {"mensagem": {"id": cur.lastrowid, "texto": texto, "autor": ctx.usuario["nome"]}}


@rota("PATCH", "/api/comites/{id}")
def atualizar_comite(ctx):
    exigir_gestor(ctx)
    c = meu_comite(ctx, int(ctx.params["id"]))
    dados = ctx.json()
    if "data_fim_contrato" not in dados:
        raise ApiError(422, "Informe 'data_fim_contrato' (AAAA-MM-DD) ou null para limpar.")
    fim = dados["data_fim_contrato"] or None
    if fim:
        try:
            fim = date.fromisoformat(str(fim)).isoformat()
        except ValueError:
            raise ApiError(422, "'data_fim_contrato' deve estar no formato AAAA-MM-DD.")
    ctx.conn.execute("UPDATE comites SET data_fim_contrato = ? WHERE id = ?", (fim, c["id"]))
    return {"comite": ver_comite(ctx, meu_comite(ctx, c["id"]), completo=False)}


@rota("PATCH", "/api/comites/{id}/tarefas/{tarefa_id}")
def atualizar_tarefa(ctx):
    exigir_gestor(ctx)
    c = meu_comite(ctx, int(ctx.params["id"]))
    t = ctx.conn.execute("SELECT * FROM tarefas WHERE id = ? AND comite_id = ?",
                         (int(ctx.params["tarefa_id"]), c["id"])).fetchone()
    if t is None:
        raise ApiError(404, "Tarefa não encontrada.")
    dados = ctx.json()
    concluida = 1 if dados.get("concluida") else 0
    prazo = dados.get("prazo", t["prazo"])
    if prazo:
        try:
            prazo = date.fromisoformat(str(prazo)).isoformat()
        except ValueError:
            raise ApiError(422, "'prazo' deve estar no formato AAAA-MM-DD.")
    ctx.conn.execute("UPDATE tarefas SET concluida = ?, prazo = ? WHERE id = ?", (concluida, prazo, t["id"]))
    return {"tarefa": dict(ctx.conn.execute("SELECT * FROM tarefas WHERE id = ?", (t["id"],)).fetchone())}


# ---------------------------------------------------------------------------
# Rotas: fiscalização (ocorrências sobre o cronograma dos comitês)
# ---------------------------------------------------------------------------
TIPOS_OCORRENCIA = {"inconsistencia", "falha", "falta_informacao", "intercorrencia"}
GRAVIDADES = {"baixa", "media", "alta"}


def _ver_ocorrencia(conn, o: dict) -> dict:
    autor = conn.execute("SELECT nome FROM usuarios WHERE id = ?", (o["autor_usuario_id"],)).fetchone()
    comite = conn.execute("SELECT nome FROM comites WHERE id = ?", (o["comite_id"],)).fetchone()
    tarefa = conn.execute("SELECT titulo, ordem FROM tarefas WHERE id = ?", (o["tarefa_id"],)).fetchone() if o["tarefa_id"] else None
    respostas = [dict(r) for r in conn.execute(
        """SELECT r.id, r.texto, r.criada_em, u.nome AS autor, u.perfil, og.sigla AS orgao
             FROM ocorrencia_respostas r JOIN usuarios u ON u.id = r.usuario_id JOIN orgaos og ON og.id = u.orgao_id
            WHERE r.ocorrencia_id = ? ORDER BY r.id""", (o["id"],))]
    return {
        "id": o["id"], "comite_id": o["comite_id"], "comite_nome": comite["nome"] if comite else None,
        "tarefa_id": o["tarefa_id"], "tarefa_titulo": tarefa["titulo"] if tarefa else None,
        "tarefa_ordem": tarefa["ordem"] if tarefa else None,
        "tipo": o["tipo"], "gravidade": o["gravidade"], "descricao": o["descricao"], "status": o["status"],
        "autor": autor["nome"] if autor else None, "criada_em": o["criada_em"], "resolvida_em": o["resolvida_em"],
        "respostas": respostas,
    }


def _ocorrencia_acessivel(ctx, ocorrencia_id: int) -> dict:
    o = linha(ctx.conn.execute("SELECT * FROM ocorrencias WHERE id = ?", (ocorrencia_id,)).fetchone())
    if o is None:
        raise ApiError(404, "Ocorrência não encontrada.")
    meu_comite(ctx, o["comite_id"])  # 404 para quem não participa do comitê
    return o


@rota("GET", "/api/ocorrencias")
def listar_ocorrencias(ctx):
    sql, args = "SELECT o.* FROM ocorrencias o", []
    if not eh_fiscal(ctx):
        sql += """ JOIN comites c ON c.id = o.comite_id JOIN matches m ON m.id = c.match_id
                   JOIN demandas a ON a.id = m.demanda_a_id JOIN demandas b ON b.id = m.demanda_b_id
                   WHERE (a.orgao_id = ? OR b.orgao_id = ?)"""
        args += [ctx.orgao_id, ctx.orgao_id]
    filtros = []
    if ctx.q("comite_id"):
        filtros.append("o.comite_id = ?")
        args.append(int(ctx.q("comite_id")) if str(ctx.q("comite_id")).isdigit() else -1)
    if ctx.q("status") in {"aberta", "respondida", "resolvida"}:
        filtros.append("o.status = ?")
        args.append(ctx.q("status"))
    if filtros:
        sql += (" AND " if " WHERE " in sql else " WHERE ") + " AND ".join(filtros)
    sql += " ORDER BY o.id DESC"
    return {"ocorrencias": [_ver_ocorrencia(ctx.conn, dict(r)) for r in ctx.conn.execute(sql, args)]}


@rota("POST", "/api/comites/{id}/ocorrencias")
def criar_ocorrencia(ctx):
    exigir_fiscal(ctx)
    c = meu_comite(ctx, int(ctx.params["id"]))
    dados = ctx.json()
    tipo, gravidade = str(dados.get("tipo") or ""), str(dados.get("gravidade") or "media")
    descricao = str(dados.get("descricao") or "").strip()
    if tipo not in TIPOS_OCORRENCIA:
        raise ApiError(422, "'tipo' deve ser: " + ", ".join(sorted(TIPOS_OCORRENCIA)) + ".")
    if gravidade not in GRAVIDADES:
        raise ApiError(422, "'gravidade' deve ser: baixa, media ou alta.")
    if len(descricao) < 10:
        raise ApiError(422, "Descreva a ocorrência com pelo menos 10 caracteres.")
    if len(descricao) > 4000:
        raise ApiError(422, "A descrição pode ter no máximo 4000 caracteres.")
    tarefa_id = dados.get("tarefa_id")
    if tarefa_id not in (None, ""):
        ok = str(tarefa_id).isdigit() and ctx.conn.execute(
            "SELECT 1 FROM tarefas WHERE id = ? AND comite_id = ?", (int(tarefa_id), c["id"])).fetchone()
        if not ok:
            raise ApiError(422, "'tarefa_id' não pertence a este comitê.")
        tarefa_id = int(tarefa_id)
    else:
        tarefa_id = None
    cur = ctx.conn.execute(
        """INSERT INTO ocorrencias (comite_id, tarefa_id, tipo, gravidade, descricao, autor_usuario_id, criada_em)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (c["id"], tarefa_id, tipo, gravidade, descricao, ctx.usuario["id"], agora()))
    o = linha(ctx.conn.execute("SELECT * FROM ocorrencias WHERE id = ?", (cur.lastrowid,)).fetchone())
    return 201, {"ocorrencia": _ver_ocorrencia(ctx.conn, o)}


@rota("POST", "/api/ocorrencias/{id}/respostas")
def responder_ocorrencia(ctx):
    o = _ocorrencia_acessivel(ctx, int(ctx.params["id"]))
    texto = str(ctx.json().get("texto") or "").strip()
    if not texto:
        raise ApiError(422, "A resposta não pode ser vazia.")
    if len(texto) > 4000:
        raise ApiError(422, "A resposta pode ter no máximo 4000 caracteres.")
    if o["status"] == "resolvida" and not eh_fiscal(ctx):
        raise ApiError(409, "Esta ocorrência já foi resolvida pela fiscalização.")
    ctx.conn.execute("INSERT INTO ocorrencia_respostas (ocorrencia_id, usuario_id, texto, criada_em) VALUES (?, ?, ?, ?)",
                     (o["id"], ctx.usuario["id"], texto, agora()))
    if not eh_fiscal(ctx) and o["status"] == "aberta":
        ctx.conn.execute("UPDATE ocorrencias SET status = 'respondida' WHERE id = ?", (o["id"],))
    atual = linha(ctx.conn.execute("SELECT * FROM ocorrencias WHERE id = ?", (o["id"],)).fetchone())
    return 201, {"ocorrencia": _ver_ocorrencia(ctx.conn, atual)}


@rota("PATCH", "/api/ocorrencias/{id}")
def atualizar_ocorrencia(ctx):
    exigir_fiscal(ctx)
    o = _ocorrencia_acessivel(ctx, int(ctx.params["id"]))
    status = str(ctx.json().get("status") or "")
    if status not in {"aberta", "resolvida"}:
        raise ApiError(422, "'status' deve ser 'resolvida' (encerrar) ou 'aberta' (reabrir).")
    ctx.conn.execute("UPDATE ocorrencias SET status = ?, resolvida_em = ? WHERE id = ?",
                     (status, agora() if status == "resolvida" else None, o["id"]))
    atual = linha(ctx.conn.execute("SELECT * FROM ocorrencias WHERE id = ?", (o["id"],)).fetchone())
    return {"ocorrencia": _ver_ocorrencia(ctx.conn, atual)}


# ---------------------------------------------------------------------------
# Rota: painel de indicadores
# ---------------------------------------------------------------------------
def _indicadores(conn, orgao_id=None) -> dict:
    filtro, args = "", []
    if orgao_id is not None:
        filtro = " WHERE (a.orgao_id = ? OR b.orgao_id = ?)"
        args = [orgao_id, orgao_id]
    base = f"""FROM matches m JOIN demandas a ON a.id = m.demanda_a_id
               JOIN demandas b ON b.id = m.demanda_b_id{filtro}"""
    contagem = {r["status"]: r["n"] for r in conn.execute(f"SELECT m.status, COUNT(*) n {base} GROUP BY m.status", args)}
    economia = conn.execute(
        f"SELECT COALESCE(SUM(m.economia_valor), 0) v {base}{' AND' if filtro else ' WHERE'} m.status = 'conectado'",
        args,
    ).fetchone()["v"]
    demandas = conn.execute(
        "SELECT COUNT(*) n FROM demandas" + (" WHERE orgao_id = ?" if orgao_id else ""),
        [orgao_id] if orgao_id else [],
    ).fetchone()["n"]
    return {
        "demandas": demandas,
        "matches_sugeridos": contagem.get("sugerido", 0),
        "matches_conectados": contagem.get("conectado", 0),
        "matches_recusados": contagem.get("recusado", 0),
        # cada match conectado = 1 licitação a menos
        "processos_evitados": contagem.get("conectado", 0),
        "economia_estimada_conectados": round(economia, 2),
        "pontos": total_pontos(conn, orgao_id),
    }


@rota("GET", "/api/painel")
def painel(ctx):
    orgaos = ctx.conn.execute("SELECT COUNT(*) n FROM orgaos WHERE cooperado = 1").fetchone()["n"]
    return {
        "rede": _indicadores(ctx.conn) | {"orgaos_cooperados": orgaos},
        "meu_orgao": _indicadores(ctx.conn, ctx.orgao_id),
        "observacao": "Economia estimada com parâmetros ilustrativos; não considera valores sigilosos.",
    }


@rota("GET", "/api/incentivos")
def incentivos(ctx):
    ranking = [dict(r) for r in ctx.conn.execute(
        """SELECT o.id orgao_id, o.sigla, o.nome, COALESCE(SUM(p.pontos), 0) pontos, COUNT(p.match_id) matches
           FROM orgaos o LEFT JOIN pontos p ON p.orgao_id = o.id WHERE o.cooperado = 1
           GROUP BY o.id, o.sigla, o.nome ORDER BY pontos DESC, o.sigla""")]
    for i, r in enumerate(ranking, start=1):
        r["posicao"], r["pontos"], r["meu"] = i, int(r["pontos"]), r["orgao_id"] == ctx.orgao_id
    historico = [dict(r) for r in ctx.conn.execute(
        "SELECT match_id, pontos, motivo, criado_em FROM pontos WHERE orgao_id = ? ORDER BY criado_em DESC, match_id DESC",
        (ctx.orgao_id,))]
    meu = next((r for r in ranking if r["meu"]), None)
    return {
        "meus_pontos": total_pontos(ctx.conn, ctx.orgao_id),
        "posicao": meu["posicao"] if meu else None,
        "ranking": ranking,
        "historico": historico,
        "regras": {"base": PONTOS_BASE, "por_mil_reais": PONTOS_POR_MIL, "bonus_maximo": PONTOS_BONUS_MAX},
    }


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------
def criar_handler(db_path: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = f"GiraMatch/{__version__}"

        def log_message(self, formato, *args):
            # Log enxuto (F-006): sem IP do cliente e sem parametros de URL.
            if not getattr(self.server, "silencioso", False):
                sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), formato % args))

        def log_request(self, code="-", size="-"):
            self.log_message("%s %s -> %s", self.command, urlparse(self.path).path, code)

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", config.CORS_ORIGEM)
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")

        def _responder(self, status: int, dados):
            corpo = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self._cors()
            self.end_headers()
            self.wfile.write(corpo)

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            self._despachar("GET")

        def do_POST(self):
            self._despachar("POST")

        def do_PUT(self):
            self._despachar("PUT")

        def do_PATCH(self):
            self._despachar("PATCH")

        def do_DELETE(self):
            self._despachar("DELETE")

        def _despachar(self, metodo: str):
            url = urlparse(self.path)
            caminho = url.path.rstrip("/") or "/"
            encontrada, metodo_errado = None, False
            for m, regex, func, publica in ROTAS:
                achou = regex.match(caminho)
                if achou:
                    if m == metodo:
                        encontrada = (func, publica, achou.groupdict())
                        break
                    metodo_errado = True
            if encontrada is None:
                status = 405 if metodo_errado else 404
                return self._responder(status, {"erro": "Método não permitido." if metodo_errado else "Rota não encontrada."})

            func, publica, params = encontrada
            tamanho = int(self.headers.get("Content-Length") or 0)
            if tamanho > MAX_CORPO:
                return self._responder(413, {"erro": "Corpo da requisição muito grande."})
            corpo = self.rfile.read(tamanho) if tamanho else b""

            try:
                conn = conectar(db_path)
            except Exception as e:  # noqa: BLE001  (F-001: banco indisponivel nao pode deixar o cliente sem resposta)
                # So o tipo do erro vai ao log: a mensagem pode conter endereco/credenciais do banco.
                sys.stderr.write("Falha ao conectar ao banco: %s\n" % type(e).__name__)
                return self._responder(503, {"erro": "Serviço temporariamente indisponível. Tente novamente em instantes."})
            try:
                token = None
                usuario = None
                cab = self.headers.get("Authorization", "")
                if cab.startswith("Bearer "):
                    token = cab[7:].strip()
                    usuario = auth.usuario_do_token(conn, token)
                if not publica and usuario is None:
                    conn.commit()
                    raise ApiError(401, "Faça login para continuar.")
                if usuario is not None and usuario["perfil"] == "fiscal" and not publica and not fiscal_pode(metodo, caminho):
                    conn.commit()
                    raise ApiError(403, "O perfil de fiscalização só acessa comitês e ocorrências.")
                ctx = Contexto(conn, usuario, params, parse_qs(url.query), corpo,
                               self.headers.get("Content-Type", ""), token, self.client_address[0])
                resultado = func(ctx)
                status, dados = resultado if isinstance(resultado, tuple) else (200, resultado)
                conn.commit()
                self._responder(status, dados)
            except ApiError as e:
                conn.rollback()
                corpo_erro = {"erro": e.mensagem}
                if e.detalhes:
                    corpo_erro["detalhes"] = e.detalhes
                self._responder(e.status, corpo_erro)
            except Exception:  # noqa: BLE001
                conn.rollback()
                traceback.print_exc()
                self._responder(500, {"erro": "Erro interno do servidor."})
            finally:
                conn.close()

    return Handler


def criar_servidor(db_path: str, host: str, porta: int, silencioso=False) -> ThreadingHTTPServer:
    servidor = ThreadingHTTPServer((host, porta), criar_handler(db_path))
    servidor.silencioso = silencioso
    return servidor
