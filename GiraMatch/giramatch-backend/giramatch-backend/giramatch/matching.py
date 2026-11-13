"""Motor de match do GiraMatch.

O motor é EXPLICÁVEL: cada sugestão traz a nota de cada critério, os motivos
em linguagem simples, o caminho jurídico sugerido e os alertas. A decisão é
sempre dos gestores (Res. CNJ 615/2025: IA como apoio, com supervisão humana).

Nesta versão a similaridade é por código de catálogo + termos da descrição.
A função `similaridade` é o ponto para plugar um modelo de linguagem
(embeddings) numa versão futura.
"""
import math
import re
import unicodedata
from datetime import date

from . import config
from .db import agora, carregar_json, para_json

STOPWORDS = {
    "de", "da", "do", "das", "dos", "para", "com", "sem", "em", "e", "a", "o",
    "os", "as", "por", "no", "na", "nos", "nas", "um", "uma", "ao", "aos",
    "aquisicao", "contratacao", "fornecimento", "prestacao", "servico", "servicos",
    "empresa", "especializada", "tipo", "unidade", "unidades",
}

FUNDAMENTO_IRP = "Lei 14.133/2021, art. 86 (intenção de registro de preços)"
FUNDAMENTO_TSE = "Res. TSE 23.702/2022, art. 14 (promover compras compartilhadas)"
FUNDAMENTO_PCA = "Lei 14.133/2021, art. 12, VII (PCA para racionalizar contratações)"


# ---------------------------------------------------------------------------
# Critérios
# ---------------------------------------------------------------------------
def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower().strip()


def termos(texto: str) -> set:
    return {t for t in re.findall(r"[a-z0-9]+", normalizar(texto)) if len(t) > 2 and t not in STOPWORDS}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def similaridade(a: dict, b: dict) -> tuple:
    """Retorna (nota 0–1, motivo)."""
    ca, cb = (a.get("codigo_catalogo") or "").strip(), (b.get("codigo_catalogo") or "").strip()
    if ca and cb and normalizar(ca) == normalizar(cb):
        return 1.0, f"Mesmo item no catálogo ({ca})"
    nota = jaccard(termos(a["descricao"]), termos(b["descricao"]))
    return nota, f"Descrições compatíveis ({round(nota * 100)}% dos termos em comum)"


def nota_tempo(a: dict, b: dict) -> tuple:
    d = abs(int(a["mes_previsto"]) - int(b["mes_previsto"]))
    nota = max(0.0, 1 - d / config.JANELA_MESES)
    if d == 0:
        motivo = "Previstas para o mesmo mês no PCA"
    else:
        motivo = f"Previsões no PCA com {d} {'mês' if d == 1 else 'meses'} de diferença"
    return nota, motivo, d


def local(demanda: dict, orgao: dict) -> tuple:
    return (demanda.get("municipio") or orgao["municipio"], demanda.get("uf") or orgao["uf"])


def nota_territorio(a, b, oa, ob) -> tuple:
    (ma, ua), (mb, ub) = local(a, oa), local(b, ob)
    mesmo_mun = normalizar(ma) == normalizar(mb) and normalizar(ua) == normalizar(ub)
    mesma_uf = normalizar(ua) == normalizar(ub)
    tipo = a["tipo"]
    # Serviços dependem mais do local; materiais e capacitações viajam melhor.
    tabela = {
        "servico": (1.0, 0.5, 0.0),
        "material": (1.0, 1.0, 0.5),
        "capacitacao": (1.0, 0.7, 0.4),
    }.get(tipo, (1.0, 0.7, 0.3))
    if mesmo_mun:
        return tabela[0], f"Os dois em {ma}/{ua}"
    if mesma_uf:
        return tabela[1], f"Mesmo estado ({ua})"
    return tabela[2], f"Estados diferentes ({ua} e {ub})"


def nota_sustentabilidade(a, b) -> tuple:
    sa = {normalizar(c): c for c in a.get("criterios_sustentaveis") or []}
    sb = {normalizar(c): c for c in b.get("criterios_sustentaveis") or []}
    if not sa and not sb:
        return 0.5, None
    comuns = [sa[k] for k in sa if k in sb]
    nota = len(comuns) / len(set(sa) | set(sb))
    motivo = f"Critérios sustentáveis em comum: {', '.join(comuns)}" if comuns else None
    return nota, motivo


def dias_entre(d1: str, d2: str):
    try:
        return abs((date.fromisoformat(d1) - date.fromisoformat(d2)).days)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Caminho jurídico e alertas
# ---------------------------------------------------------------------------
def escolher_gerenciador(a, b, oa, ob):
    """Devolve (demanda_g, orgao_g, demanda_p, orgao_p, alerta_interfederativo)."""
    fa, fb = oa["esfera"] == "federal", ob["esfera"] == "federal"
    if fa != fb:
        # Órgão federal não pode aderir a ata de estadual/distrital/municipal
        # (Lei 14.133/2021, art. 86, §8º): o federal deve gerenciar.
        if fa:
            return a, oa, b, ob, True
        return b, ob, a, oa, True
    chave_a = (int(a["mes_previsto"]), -float(a["quantidade"]), a["id"])
    chave_b = (int(b["mes_previsto"]), -float(b["quantidade"]), b["id"])
    if chave_a <= chave_b:
        return a, oa, b, ob, False
    return b, ob, a, oa, False


def montar_caminho(a, b, oa, ob) -> tuple:
    dg, og, dp, op, interfed = escolher_gerenciador(a, b, oa, ob)
    alertas = []
    if a["natureza"] == "capacitacao":
        caminho = {
            "modelo": "capacitacao_compartilhada",
            "titulo": "Capacitação compartilhada",
            "descricao": (
                f"Turma ou evento único, organizado pelo {og['sigla']} com vagas para o "
                f"{op['sigla']}, formalizado no acordo de cooperação técnica."
            ),
            "gerenciador": og["sigla"],
            "participantes": [op["sigla"]],
            "fundamentos": [FUNDAMENTO_TSE],
        }
        return caminho, alertas, og["id"]

    caminho = {
        "modelo": "irp",
        "titulo": "Intenção de Registro de Preços (IRP)",
        "descricao": (
            f"{og['sigla']} como órgão gerenciador e {op['sigla']} como participante "
            "de uma única licitação por registro de preços."
        ),
        "gerenciador": og["sigla"],
        "participantes": [op["sigla"]],
        "fundamentos": [FUNDAMENTO_IRP, FUNDAMENTO_TSE, FUNDAMENTO_PCA],
    }
    if interfed:
        alertas.append({
            "tipo": "interfederativo",
            "texto": (
                "Órgãos federais não podem aderir a ata gerenciada por órgão estadual, distrital "
                f"ou municipal (Lei 14.133/2021, art. 86, §8º). Por isso o {og['sigla']} foi sugerido "
                f"como gerenciador. Confirme com a assessoria jurídica a participação do {op['sigla']}."
            ),
        })
    va, vb = a.get("valor_estimado"), b.get("valor_estimado")
    if va is not None and vb is not None:
        lim = config.LIMITE_ME_EPP
        if va <= lim and vb <= lim and va + vb > lim:
            alertas.append({
                "tipo": "me_epp",
                "texto": (
                    "Somados, os valores passam de R$ 80 mil e podem afastar a licitação exclusiva para "
                    "ME/EPP (LC 123/2006, art. 48, I). Avalie dividir em itens ou usar cota reservada."
                ),
            })
    return caminho, alertas, og["id"]


def economia(a, b) -> tuple:
    """(volume_total, economia_pct, economia_valor). Ilustrativo — ver config."""
    if normalizar(a["unidade"]) != normalizar(b["unidade"]):
        return None, None, None
    qa, qb = float(a["quantidade"]), float(b["quantidade"])
    total = qa + qb
    maior = max(qa, qb) or 1
    pct = min(config.ECONOMIA_MAX, config.ECONOMIA_BASE + config.ECONOMIA_FATOR * math.log2(total / maior))
    pct = round(pct, 3)
    valor = None
    va, vb = a.get("valor_estimado"), b.get("valor_estimado")
    sigilo = a.get("valor_sigiloso") or b.get("valor_sigiloso")
    if va is not None and vb is not None and not sigilo:
        valor = round((va + vb) * pct, 2)
    return total, pct, valor


# ---------------------------------------------------------------------------
# Avaliação de um par
# ---------------------------------------------------------------------------
def avaliar(a: dict, b: dict, oa: dict, ob: dict):
    """Avalia duas demandas. Devolve o dicionário do match ou None."""
    if a["orgao_id"] == b["orgao_id"] or a["ano"] != b["ano"] or a["natureza"] != b["natureza"]:
        return None

    sim, motivo_sim = similaridade(a, b)
    if sim < config.SIMILARIDADE_MINIMA:
        return None

    alertas_extra = []
    unidades_iguais = normalizar(a["unidade"]) == normalizar(b["unidade"])
    if not unidades_iguais and a["natureza"] == "contratacao":
        sim = max(0.0, sim - 0.2)
        alertas_extra.append({
            "tipo": "unidades",
            "texto": f"Unidades diferentes ({a['unidade']} e {b['unidade']}): padronize antes de somar volumes.",
        })

    t, motivo_t, dif_meses = nota_tempo(a, b)
    terr, motivo_terr = nota_territorio(a, b, oa, ob)
    sust, motivo_sust = nota_sustentabilidade(a, b)

    p = config.PESOS
    score = 100 * (p["similaridade"] * sim + p["tempo"] * t + p["territorio"] * terr + p["sustentabilidade"] * sust)

    motivos = [motivo_sim, motivo_t, motivo_terr]
    if motivo_sust:
        motivos.append(motivo_sust)

    if a["tipo"] == "servico":
        dias = dias_entre(a.get("fim_contrato_atual"), b.get("fim_contrato_atual"))
        if dias is not None and dias <= 90:
            score += config.BONUS_CONTRATOS_ALINHADOS
            motivos.append(f"Contratos atuais terminam com {dias} dias de diferença")

    score = int(round(min(100, score)))
    if score < config.LIMIAR_SCORE:
        return None

    caminho, alertas, gerenciador_id = montar_caminho(a, b, oa, ob)
    alertas += alertas_extra
    if dif_meses > 3:
        alertas.append({
            "tipo": "prazo",
            "texto": f"As previsões estão {dif_meses} meses distantes: um dos órgãos precisará ajustar o cronograma do PCA.",
        })

    volume, pct, valor = economia(a, b)
    return {
        "score": score,
        "componentes": {
            "similaridade": round(sim, 3),
            "tempo": round(t, 3),
            "territorio": round(terr, 3),
            "sustentabilidade": round(sust, 3),
        },
        "motivos": motivos,
        "caminho": caminho,
        "alertas": alertas,
        "volume_total": volume,
        "economia_pct": pct,
        "economia_valor": valor,
        "gerenciador_orgao_id": gerenciador_id,
    }


# ---------------------------------------------------------------------------
# Geração em lote (grava no banco)
# ---------------------------------------------------------------------------
def carregar_demandas(conn, ano=None):
    sql = """SELECT d.*, o.sigla, o.esfera, o.uf AS orgao_uf, o.municipio AS orgao_municipio
               FROM demandas d JOIN orgaos o ON o.id = d.orgao_id
              WHERE o.cooperado = 1"""
    args = []
    if ano is not None:
        sql += " AND d.ano = ?"
        args.append(ano)
    demandas = []
    for row in conn.execute(sql, args):
        d = dict(row)
        d["criterios_sustentaveis"] = carregar_json(d["criterios_sustentaveis"], [])
        demandas.append(d)
    return demandas


def carregar_orgaos(conn) -> dict:
    return {r["id"]: dict(r) for r in conn.execute("SELECT * FROM orgaos")}


def gerar_matches(conn, orgao_id=None, ano=None) -> dict:
    """Recalcula as sugestões. Se `orgao_id` for dado, só os pares desse órgão.

    - Matches já conectados ou recusados não são alterados.
    - Sugestões que deixaram de passar no limiar (e sem decisão) são removidas.
    Complexidade O(n²): suficiente para o protótipo; para a rede inteira,
    agrupar antes por código de catálogo/categoria.
    """
    orgaos = carregar_orgaos(conn)
    demandas = carregar_demandas(conn, ano)
    por_id = {d["id"]: d for d in demandas}

    calculados = {}
    for i, a in enumerate(demandas):
        for b in demandas[i + 1:]:
            if orgao_id is not None and orgao_id not in (a["orgao_id"], b["orgao_id"]):
                continue
            x, y = (a, b) if a["id"] < b["id"] else (b, a)
            r = avaliar(x, y, orgaos[x["orgao_id"]], orgaos[y["orgao_id"]])
            if r:
                calculados[(x["id"], y["id"])] = r

    existentes = {}
    for row in conn.execute("SELECT id, demanda_a_id, demanda_b_id, status FROM matches"):
        par = (row["demanda_a_id"], row["demanda_b_id"])
        envolvidos = {por_id.get(par[0], {}).get("orgao_id"), por_id.get(par[1], {}).get("orgao_id")}
        if orgao_id is None or orgao_id in envolvidos:
            existentes[par] = dict(row)

    criados = atualizados = removidos = 0
    ts = agora()
    for par, r in calculados.items():
        dados = (
            r["score"], para_json(r["componentes"]), para_json(r["motivos"]), para_json(r["caminho"]),
            para_json(r["alertas"]), r["volume_total"], r["economia_pct"], r["economia_valor"],
        )
        atual = existentes.get(par)
        if atual is None:
            conn.execute(
                """INSERT INTO matches (demanda_a_id, demanda_b_id, score, componentes, motivos, caminho,
                                        alertas, volume_total, economia_pct, economia_valor, criado_em, atualizado_em)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (*par, *dados, ts, ts),
            )
            criados += 1
        elif atual["status"] == "sugerido":
            conn.execute(
                """UPDATE matches SET score=?, componentes=?, motivos=?, caminho=?, alertas=?,
                          volume_total=?, economia_pct=?, economia_valor=?, atualizado_em=? WHERE id=?""",
                (*dados, ts, atual["id"]),
            )
            atualizados += 1

    for par, atual in existentes.items():
        if par in calculados or atual["status"] != "sugerido":
            continue
        tem_decisao = conn.execute("SELECT 1 FROM decisoes WHERE match_id = ?", (atual["id"],)).fetchone()
        if not tem_decisao:
            conn.execute("DELETE FROM matches WHERE id = ?", (atual["id"],))
            removidos += 1

    return {"criados": criados, "atualizados": atualizados, "removidos": removidos}
