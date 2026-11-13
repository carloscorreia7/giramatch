"""Testes adicionais da auditoria (P0): entrada inválida, ausência de dados e falha de dependência.
Não alteram o MVP; só observam o comportamento atual."""
import http.client
import threading
from datetime import datetime, timedelta, timezone

import pytest

from giramatch.api import criar_servidor
from giramatch.db import conectar, criar_tabelas
from giramatch.seed import popular
from test_api import chamar, entrar


@pytest.fixture()
def ambiente(tmp_path):
    db = str(tmp_path / "aud.db")
    conn = conectar(db)
    criar_tabelas(conn)
    popular(conn)
    conn.close()
    srv = criar_servidor(db, "127.0.0.1", 0, silencioso=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield db, f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


DEMANDA_OK = {"ano": 2027, "descricao": "Cadeiras ergonômicas de escritório", "mes_previsto": 5, "quantidade": 10, "unidade": "un"}


# ---- REQ-001 -------------------------------------------------------------
def test_req001_entrada_invalida_e_sem_login(ambiente):
    _, base = ambiente
    tok = entrar(base, "trepb")
    assert chamar(base, "POST", "/api/demandas", DEMANDA_OK, tok)[0] == 201                          # positivo
    assert chamar(base, "POST", "/api/demandas", {**DEMANDA_OK, "mes_previsto": 13}, tok)[0] == 422  # inválida
    assert chamar(base, "POST", "/api/demandas", {**DEMANDA_OK, "descricao": ""}, tok)[0] == 422     # inválida
    assert chamar(base, "POST", "/api/demandas", DEMANDA_OK)[0] == 401                               # sem login


def test_req001_json_malformado(ambiente):
    _, base = ambiente
    tok = entrar(base, "trepb")
    status, _ = chamar(base, "POST", "/api/demandas", bruto=b"{isto nao e json", token=tok)
    assert status in (400, 422)


# ---- REQ-002 -------------------------------------------------------------
def test_req002_ausencia_de_dados_feed_vazio(ambiente):
    """Órgão novo, sem demandas e sem matches, recebe feed vazio (não erro)."""
    db, base = ambiente
    from giramatch.__main__ import salvar_usuario
    conn = conectar(db)
    conn.execute("INSERT INTO orgaos (sigla, nome, ramo, esfera, uf, municipio) VALUES ('NOVO','Novo','x','federal','PB','Cabedelo')")
    conn.commit()
    salvar_usuario(conn, "NOVO", "Novo", "novo@x.giramatch.demo", "Senha-Forte-1")
    conn.close()
    _, r = chamar(base, "POST", "/api/auth/login", {"email": "novo@x.giramatch.demo", "senha": "Senha-Forte-1"})
    status, feed = chamar(base, "GET", "/api/matches?pendentes=1", token=r["token"])
    assert status == 200 and feed["matches"] == []


# ---- REQ-003 / segurança --------------------------------------------------
def test_req003_mensagem_acima_do_limite(ambiente):
    _, base = ambiente
    tre, trt = entrar(base, "trepb"), entrar(base, "trt13")
    _, r = chamar(base, "GET", "/api/matches", token=tre)
    nb = next(m for m in r["matches"] if m["outra_demanda"]["orgao"]["sigla"] == "TRT 13" and "Notebooks" in m["minha_demanda"]["descricao"])
    chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, tre)
    _, r = chamar(base, "POST", f"/api/matches/{nb['id']}/decisao", {"decisao": "conectar"}, trt)
    cid = r["match"]["comite_id"]
    assert chamar(base, "POST", f"/api/comites/{cid}/mensagens", {"texto": "x" * 4000}, tre)[0] == 201
    assert chamar(base, "POST", f"/api/comites/{cid}/mensagens", {"texto": "x" * 4001}, tre)[0] == 422


def test_token_expirado_e_invalido(ambiente):
    db, base = ambiente
    tok = entrar(base, "trepb")
    conn = conectar(db)
    passado = (datetime.now(timezone.utc) - timedelta(hours=1)).replace(microsecond=0).isoformat()
    conn.execute("UPDATE sessoes SET expira_em = ?", (passado,))
    conn.commit()
    conn.close()
    assert chamar(base, "GET", "/api/me", token=tok)[0] == 401
    assert chamar(base, "GET", "/api/me", token="token-inventado")[0] == 401


def test_login_com_tentativa_de_injecao_sql(ambiente):
    _, base = ambiente
    s, _ = chamar(base, "POST", "/api/auth/login", {"email": "' OR '1'='1", "senha": "' OR '1'='1"})
    assert s == 401


def test_f003_login_bloqueia_apos_muitas_falhas(ambiente):
    """T-F003: depois de 8 senhas erradas para o mesmo e-mail o login responde 429, mesmo com a senha certa."""
    _, base = ambiente
    for i in range(8):
        assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": f"errada{i}"})[0] == 401
    assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": "errada9"})[0] == 429
    assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": "demo123"})[0] == 429


def test_f003_poucas_falhas_nao_bloqueiam_e_sucesso_zera(ambiente):
    """T-F003b: 3 erros nao bloqueiam; um login valido continua funcionando e zera o contador."""
    _, base = ambiente
    for i in range(3):
        assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": f"x{i}"})[0] == 401
    assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": "demo123"})[0] == 200
    for i in range(7):
        assert chamar(base, "POST", "/api/auth/login", {"email": "gestor@trepb.giramatch.demo", "senha": f"y{i}"})[0] == 401


# ---- Falha de dependência -------------------------------------------------
def test_falha_de_dependencia_banco_indisponivel(tmp_path):
    """Banco inacessível: o servidor deve responder com erro HTTP, não derrubar a conexão sem resposta."""
    inexistente = str(tmp_path / "pasta_que_nao_existe" / "x.db")
    srv = criar_servidor(inexistente, "127.0.0.1", 0, silencioso=True)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        con = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=5)
        con.request("GET", "/api/health")
        resp = con.getresponse()
        corpo = resp.read().decode("utf-8")
        assert resp.status == 503, f"esperava 503, veio {resp.status}"          # T-F001
        assert "indispon" in corpo and "pasta_que_nao_existe" not in corpo   # mensagem generica, sem vazar caminho
    finally:
        srv.shutdown()
        srv.server_close()


def test_nova_demanda_aparece_em_minhas_demandas(ambiente):
    """Demanda cadastrada aparece na listagem do próprio órgão (e só dele) e continua lá em uma nova sessão."""
    _, base = ambiente
    tre = entrar(base, "trepb")
    antes = chamar(base, "GET", "/api/demandas", token=tre)[1]["demandas"]
    s, r = chamar(base, "POST", "/api/demandas", DEMANDA_OK, tre)
    assert s == 201
    depois = chamar(base, "GET", "/api/demandas", token=tre)[1]["demandas"]
    assert len(depois) == len(antes) + 1
    assert any(d["descricao"] == DEMANDA_OK["descricao"] for d in depois)
    # nova sessão (sair e entrar de novo): a demanda continua
    tre2 = entrar(base, "trepb")
    assert any(d["descricao"] == DEMANDA_OK["descricao"] for d in chamar(base, "GET", "/api/demandas", token=tre2)[1]["demandas"])
    # outro órgão não vê a demanda do TRE-PB na própria lista
    trt = entrar(base, "trt13")
    assert not any(d["descricao"] == DEMANDA_OK["descricao"] for d in chamar(base, "GET", "/api/demandas", token=trt)[1]["demandas"])


def test_painel_campos_usados_pela_tela(ambiente):
    """RF07-RF12: a API entrega os campos que o painel usa para contar, notificar, ordenar e filtrar."""
    _, base = ambiente
    tre = entrar(base, "trepb")
    _, r = chamar(base, "GET", "/api/matches", token=tre)           # todos os matches (sem filtro de status)
    assert r["total"] > 0 and r["aviso"]
    for m in r["matches"]:
        assert {"id", "score", "status", "minha_decisao", "pedido_recebido"} <= set(m)
        assert {"descricao", "ano", "mes_previsto", "tipo"} <= set(m["minha_demanda"])     # filtros por período e categoria
        assert m["outra_demanda"]["orgao"]["sigla"]                                         # notificações
    assert [m["score"] for m in r["matches"]] == sorted((m["score"] for m in r["matches"]), reverse=True)  # maior compatibilidade primeiro
    _, d = chamar(base, "GET", "/api/demandas", token=tre)
    assert all({"id", "criada_em", "tipo", "ano", "mes_previsto"} <= set(x) for x in d["demandas"])       # demandas recentes e filtros
    _, p = chamar(base, "GET", "/api/painel", token=tre)
    assert {"demandas", "matches_conectados", "economia_estimada_conectados"} <= set(p["meu_orgao"])
    assert {"orgaos_cooperados", "demandas", "matches_conectados"} <= set(p["rede"])
