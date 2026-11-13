import json
import os
import threading
import urllib.error
import urllib.request

import pytest

from giramatch.api import criar_servidor
from giramatch.db import apagar_tudo, conectar, criar_tabelas, eh_postgres
from giramatch.seed import SENHA_DEMO, popular


@pytest.fixture()
def base(tmp_path):
    # Para testar no PostgreSQL: defina TEST_DATABASE_URL (o banco indicado será APAGADO).
    db = os.environ.get("TEST_DATABASE_URL") or str(tmp_path / "teste.db")
    conn = conectar(db)
    if eh_postgres(db):
        apagar_tudo(conn)
    criar_tabelas(conn)
    popular(conn)
    conn.close()
    srv = criar_servidor(db, "127.0.0.1", 0, silencioso=True)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def chamar(base, metodo, caminho, dados=None, token=None, bruto=None, tipo="application/json"):
    corpo = bruto if bruto is not None else (json.dumps(dados).encode() if dados is not None else None)
    req = urllib.request.Request(base + caminho, data=corpo, method=metodo)
    if corpo is not None:
        req.add_header("Content-Type", tipo)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def entrar(base, sigla):
    email = f"gestor@{sigla}.giramatch.demo"
    s, r = chamar(base, "POST", "/api/auth/login", {"email": email, "senha": SENHA_DEMO})
    assert s == 200, r
    return r["token"]


def test_health_e_login(base):
    assert chamar(base, "GET", "/api/health")[0] == 200
    s, r = chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": "errada"})
    assert s == 401
    assert chamar(base, "GET", "/api/me")[0] == 401
    s, r = chamar(base, "GET", "/api/me", token=entrar(base, "trepb"))
    assert s == 200 and r["orgao"]["sigla"] == "TRE-PB"


def test_feed_de_matches_ordenado_e_explicado(base):
    s, r = chamar(base, "GET", "/api/matches?pendentes=1", token=entrar(base, "trepb"))
    assert s == 200 and r["total"] > 0
    scores = [m["score"] for m in r["matches"]]
    assert scores == sorted(scores, reverse=True)
    m = r["matches"][0]
    assert m["motivos"] and m["caminho"]["gerenciador"]
    assert m["minha_demanda"]["orgao"]["sigla"] == "TRE-PB"


def test_valor_sigiloso_escondido_do_outro_orgao(base):
    _, r = chamar(base, "GET", "/api/matches", token=entrar(base, "trepb"))
    usina = next(m for m in r["matches"] if "solar" in m["minha_demanda"]["descricao"].lower())
    assert usina["outra_demanda"]["orgao"]["sigla"] == "TJPB"
    assert usina["outra_demanda"]["valor_estimado"] is None
    _, r2 = chamar(base, "GET", "/api/demandas", token=entrar(base, "tjpb"))
    propria = next(d for d in r2["demandas"] if "solar" in d["descricao"].lower())
    assert propria["valor_estimado"] == 4_800_000


def test_conexao_dos_dois_lados_cria_comite(base):
    tre, trt = entrar(base, "trepb"), entrar(base, "trt13")
    _, r = chamar(base, "GET", "/api/matches", token=tre)
    nb = next(m for m in r["matches"]
              if m["outra_demanda"]["orgao"]["sigla"] == "TRT 13" and "Notebooks" in m["minha_demanda"]["descricao"])

    s, r = chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, tre)
    assert s == 200 and r["deu_match"] is False

    # O TRT 13 ainda não decidiu, mas é avisado de que recebeu um pedido de conexão do TRE-PB
    _, feed = chamar(base, "GET", "/api/matches?pendentes=1", token=trt)
    visto = next(m for m in feed["matches"] if m["id"] == nb["id"])
    assert visto["minha_decisao"] is None
    assert visto["pedido_recebido"] is True
    # Quem fez o pedido não vê "pedido recebido" no próprio match
    _, meu = chamar(base, "GET", f"/api/matches/{nb['id']}", token=tre)
    assert meu["match"]["pedido_recebido"] is False

    s, r = chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, trt)
    assert s == 200 and r["deu_match"] is True and r["match"]["status"] == "conectado"

    comite_id = r["match"]["comite_id"]
    s, c = chamar(base, "GET", f"/api/comites/{comite_id}", token=tre)
    assert s == 200 and len(c["comite"]["tarefas"]) == 5
    assert c["comite"]["gerenciador"]["sigla"] == "TRE-PB"

    s, _ = chamar(base, "POST", f"/api/comites/{comite_id}/mensagens", {"texto": "Vamos alinhar a especificação?"}, trt)
    assert s == 201
    tarefa = c["comite"]["tarefas"][0]["id"]
    s, t = chamar(base, "PATCH", f"/api/comites/{comite_id}/tarefas/{tarefa}", {"concluida": True}, tre)
    assert s == 200 and t["tarefa"]["concluida"] == 1

    # Um órgão de fora não acessa o comitê
    assert chamar(base, "GET", f"/api/comites/{comite_id}", token=entrar(base, "jfpb"))[0] == 404

    # Data fim do contrato: vale para o comitê, aparece para os dois órgãos e valida o formato
    assert c["comite"]["data_fim_contrato"] is None
    s, r2 = chamar(base, "PATCH", f"/api/comites/{comite_id}", {"data_fim_contrato": "2027-06-30"}, tre)
    assert s == 200 and r2["comite"]["data_fim_contrato"] == "2027-06-30"
    assert chamar(base, "GET", f"/api/comites/{comite_id}", token=trt)[1]["comite"]["data_fim_contrato"] == "2027-06-30"
    assert chamar(base, "GET", "/api/comites", token=trt)[1]["comites"][0]["data_fim_contrato"] == "2027-06-30"
    assert chamar(base, "PATCH", f"/api/comites/{comite_id}", {"data_fim_contrato": "30/06/2027"}, tre)[0] == 422
    assert chamar(base, "PATCH", f"/api/comites/{comite_id}", {"data_fim_contrato": "2027-06-30"}, entrar(base, "jfpb"))[0] == 404
    assert chamar(base, "PATCH", f"/api/comites/{comite_id}", {"data_fim_contrato": None}, tre)[1]["comite"]["data_fim_contrato"] is None

    _, p = chamar(base, "GET", "/api/painel", token=tre)
    assert p["rede"]["matches_conectados"] == 1 and p["rede"]["economia_estimada_conectados"] > 0

    # Incentivo: os dois órgãos ganham os mesmos pontos pelo match conectado
    pts = r["pontos_ganhos"]
    assert pts >= 100
    for token, sigla in ((tre, "TRE-PB"), (trt, "TRT 13")):
        _, inc = chamar(base, "GET", "/api/incentivos", token=token)
        assert inc["meus_pontos"] == pts and inc["posicao"] <= 2
        assert inc["ranking"][0]["pontos"] == pts and len(inc["historico"]) == 1
    assert chamar(base, "GET", "/api/incentivos", token=entrar(base, "jfpb"))[1]["meus_pontos"] == 0
    assert p["meu_orgao"]["pontos"] == pts and p["rede"]["pontos"] == 2 * pts

    # Decidir de novo um match já conectado não é permitido (e não duplica pontos)
    assert chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "recusar"}, tre)[0] == 409
    assert chamar(base, "GET", "/api/incentivos", token=tre)[1]["meus_pontos"] == pts


def test_recusa_encerra_match(base):
    tre = entrar(base, "trepb")
    _, r = chamar(base, "GET", "/api/matches?pendentes=1", token=tre)
    alvo = r["matches"][-1]
    s, r = chamar(base, "POST", f"/api/matches/{alvo['id']}/decisao", {"decisao": "recusar"}, tre)
    assert s == 200 and r["match"]["status"] == "recusado"


def test_nova_demanda_gera_match(base):
    jf = entrar(base, "jfpb")
    s, r = chamar(base, "POST", "/api/demandas", {
        "ano": 2027, "descricao": "Notebooks corporativos", "codigo_catalogo": "CATMAT-DEMO-0001",
        "quantidade": 70, "unidade": "un", "valor_estimado": 450000, "mes_previsto": 3,
        "criterios_sustentaveis": ["eficiência energética", "logística reversa"],
    }, jf)
    assert s == 201 and r["matches"]["criados"] >= 1
    s, r = chamar(base, "POST", "/api/demandas", {"ano": 2027, "descricao": "", "mes_previsto": 3}, jf)
    assert s == 422


def test_importar_csv(base):
    trern = entrar(base, "trern")
    csv_texto = (
        "ano;descricao;codigo_catalogo;quantidade;unidade;valor_estimado;mes_previsto;tipo;criterios_sustentaveis\n"
        "2027;Papel A4 reciclado;CATMAT-DEMO-0003;800;resma;20000;2;material;papel reciclado|certificação florestal\n"
        "2027;Linha sem mês;;10;un;;;material;\n"
    ).encode()
    s, r = chamar(base, "POST", "/api/demandas/importar", bruto=csv_texto, token=trern, tipo="text/csv")
    assert s == 201 and r["importadas"] == 1 and len(r["erros"]) == 1


def test_nao_ve_match_de_terceiros(base):
    _, r = chamar(base, "GET", "/api/matches", token=entrar(base, "trt13"))
    ids_trt = {m["id"] for m in r["matches"]}
    _, r = chamar(base, "GET", "/api/matches", token=entrar(base, "trepb"))
    so_tre = next(m["id"] for m in r["matches"] if m["id"] not in ids_trt)
    assert chamar(base, "GET", f"/api/matches/{so_tre}", token=entrar(base, "trt13"))[0] == 404


def test_usuarios_do_ambiente(tmp_path, monkeypatch):
    from giramatch import config
    from giramatch.__main__ import criar_usuarios_do_ambiente
    db = str(tmp_path / "u.db")
    conn = conectar(db)
    criar_tabelas(conn)
    popular(conn)
    monkeypatch.setattr(config, "USUARIOS_ENV", "TJPB|Teste|Teste@tjpb.giramatch.demo|Tjpb@2027x;XXX|Fulano|f@x.com|senhaboa123;TJPB|Curta|c@x.com|123")
    criar_usuarios_do_ambiente(conn)
    conn.close()
    srv = criar_servidor(db, "127.0.0.1", 0, silencioso=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        st, r = chamar(base, "POST", "/api/auth/login", {"email": "teste@tjpb.giramatch.demo", "senha": "Tjpb@2027x"})
        assert st == 200 and r["orgao"]["sigla"] == "TJPB"
        assert chamar(base, "POST", "/api/auth/login", {"email": "f@x.com", "senha": "senhaboa123"})[0] == 401
    finally:
        srv.shutdown()
        srv.server_close()


def test_conversa_entre_os_dois_orgaos(base):
    """REQ-003 / TEST-CHAT: o que um órgão escreve no comitê o outro lê; terceiros e textos vazios são barrados."""
    tre, trt = entrar(base, "trepb"), entrar(base, "trt13")
    _, r = chamar(base, "GET", "/api/matches", token=tre)
    nb = next(m for m in r["matches"]
              if m["outra_demanda"]["orgao"]["sigla"] == "TRT 13" and "Notebooks" in m["minha_demanda"]["descricao"])
    chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, tre)
    _, r = chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, trt)
    cid = r["match"]["comite_id"]

    # Comitê novo começa sem conversa
    _, c = chamar(base, "GET", f"/api/comites/{cid}", token=tre)
    assert c["comite"]["mensagens"] == []

    # TRT 13 escreve; TRE-PB lê, com autor e órgão corretos
    assert chamar(base, "POST", f"/api/comites/{cid}/mensagens", {"texto": "Boa noite, TRE-PB"}, trt)[0] == 201
    _, c = chamar(base, "GET", f"/api/comites/{cid}", token=tre)
    assert [(m["texto"], m["orgao"]) for m in c["comite"]["mensagens"]] == [("Boa noite, TRE-PB", "TRT 13")]

    # Negativos: texto vazio e órgão de fora
    assert chamar(base, "POST", f"/api/comites/{cid}/mensagens", {"texto": "   "}, tre)[0] == 422
    assert chamar(base, "POST", f"/api/comites/{cid}/mensagens", {"texto": "oi"}, entrar(base, "jfpb"))[0] == 404


def test_migracao_adiciona_coluna_em_banco_antigo(tmp_path):
    from giramatch.db import conectar, criar_tabelas
    conn = conectar(str(tmp_path / "antigo.db"))
    conn.execute("CREATE TABLE comites (id INTEGER PRIMARY KEY, match_id INTEGER, nome TEXT, gerenciador_orgao_id INTEGER, criado_em TEXT)")
    criar_tabelas(conn)
    assert "data_fim_contrato" in [r["name"] for r in conn.execute("PRAGMA table_info(comites)")]
    criar_tabelas(conn)  # repetir não pode falhar


def test_fiscalizacao_registra_ocorrencias_nos_comites(base):
    tre, trt, jfpb = entrar(base, "trepb"), entrar(base, "trt13"), entrar(base, "jfpb")
    s, r = chamar(base, "POST", "/api/auth/login", {"email": "fiscal@giramatch.demo", "senha": SENHA_DEMO})
    assert s == 200 and r["usuario"]["perfil"] == "fiscal"
    fiscal = r["token"]

    _, lista = chamar(base, "GET", "/api/matches", token=tre)
    nb = next(m for m in lista["matches"]
              if m["outra_demanda"]["orgao"]["sigla"] == "TRT 13" and "Notebooks" in m["minha_demanda"]["descricao"])
    chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, tre)
    comite = chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, trt)[1]["match"]["comite_id"]

    # O fiscal enxerga o comitê (que não é dele) e o cronograma, mas só em leitura
    s, c = chamar(base, "GET", f"/api/comites/{comite}", token=fiscal)
    assert s == 200 and len(c["comite"]["tarefas"]) == 5
    assert [x["id"] for x in chamar(base, "GET", "/api/comites", token=fiscal)[1]["comites"]] == [comite]
    tarefa = c["comite"]["tarefas"][1]["id"]
    assert chamar(base, "PATCH", f"/api/comites/{comite}/tarefas/{tarefa}", {"concluida": True}, fiscal)[0] == 403
    assert chamar(base, "POST", f"/api/comites/{comite}/mensagens", {"texto": "oi"}, fiscal)[0] == 403
    # ...e não acessa demandas, matches, painel nem incentivos
    for rota_ in ("/api/demandas", "/api/matches", "/api/painel", "/api/incentivos"):
        assert chamar(base, "GET", rota_, token=fiscal)[0] == 403

    # Registro de ocorrência: validação
    url = f"/api/comites/{comite}/ocorrencias"
    assert chamar(base, "POST", url, {"tipo": "falha", "descricao": "curta"}, fiscal)[0] == 422
    assert chamar(base, "POST", url, {"tipo": "xis", "descricao": "Descrição longa o bastante"}, fiscal)[0] == 422
    assert chamar(base, "POST", url, {"tipo": "falha", "descricao": "Descrição longa o bastante", "tarefa_id": 99999}, fiscal)[0] == 422
    # Gestor não registra ocorrência
    assert chamar(base, "POST", url, {"tipo": "falha", "descricao": "Descrição longa o bastante"}, tre)[0] == 403

    s, o = chamar(base, "POST", url, {"tipo": "falta_informacao", "gravidade": "alta", "tarefa_id": tarefa,
                                       "descricao": "O termo de referência não informa o quantitativo por órgão."}, fiscal)
    assert s == 201 and o["ocorrencia"]["status"] == "aberta" and o["ocorrencia"]["tarefa_ordem"] == 2
    oid = o["ocorrencia"]["id"]

    # Os dois tribunais veem; um órgão de fora não
    for tok in (tre, trt):
        assert [x["id"] for x in chamar(base, "GET", "/api/ocorrencias", token=tok)[1]["ocorrencias"]] == [oid]
        assert chamar(base, "GET", f"/api/comites/{comite}", token=tok)[1]["comite"]["ocorrencias_abertas"] == 1
    assert chamar(base, "GET", "/api/ocorrencias", token=jfpb)[1]["ocorrencias"] == []
    assert chamar(base, "POST", f"/api/ocorrencias/{oid}/respostas", {"texto": "olá"}, jfpb)[0] == 404

    # Tribunal responde -> "respondida"; só o fiscal encerra/reabre
    s, r = chamar(base, "POST", f"/api/ocorrencias/{oid}/respostas", {"texto": "Quantitativo anexado ao SEI."}, trt)
    assert s == 201 and r["ocorrencia"]["status"] == "respondida" and r["ocorrencia"]["respostas"][0]["orgao"] == "TRT 13"
    assert chamar(base, "PATCH", f"/api/ocorrencias/{oid}", {"status": "resolvida"}, tre)[0] == 403
    s, r = chamar(base, "PATCH", f"/api/ocorrencias/{oid}", {"status": "resolvida"}, fiscal)
    assert s == 200 and r["ocorrencia"]["status"] == "resolvida" and r["ocorrencia"]["resolvida_em"]
    assert chamar(base, "GET", f"/api/comites/{comite}", token=tre)[1]["comite"]["ocorrencias_abertas"] == 0
    assert chamar(base, "POST", f"/api/ocorrencias/{oid}/respostas", {"texto": "mais uma"}, tre)[0] == 409
    assert chamar(base, "PATCH", f"/api/ocorrencias/{oid}", {"status": "aberta"}, fiscal)[1]["ocorrencia"]["resolvida_em"] is None

    # O órgão de fiscalização não entra no ranking de incentivos
    assert "FISCAL" not in [x["sigla"] for x in chamar(base, "GET", "/api/incentivos", token=tre)[1]["ranking"]]
