from giramatch.matching import avaliar

FED = {"id": 1, "sigla": "TRE-PB", "esfera": "federal", "uf": "PB", "municipio": "João Pessoa"}
FED2 = {"id": 2, "sigla": "TRT 13", "esfera": "federal", "uf": "PB", "municipio": "João Pessoa"}
EST = {"id": 3, "sigla": "TJPB", "esfera": "estadual", "uf": "PB", "municipio": "João Pessoa"}


def demanda(id_, orgao, **kw):
    base = dict(id=id_, orgao_id=orgao["id"], ano=2027, natureza="contratacao", tipo="material",
                codigo_catalogo="X-1", descricao="Notebooks corporativos", quantidade=100, unidade="un",
                valor_estimado=500_000, valor_sigiloso=0, mes_previsto=3, municipio=None, uf=None,
                fim_contrato_atual=None, criterios_sustentaveis=["eficiência energética"])
    base.update(kw)
    return base


def test_mesmo_item_mesmo_mes_gera_match_forte():
    r = avaliar(demanda(1, FED), demanda(2, FED2), FED, FED2)
    assert r["score"] >= 95
    assert r["caminho"]["modelo"] == "irp"
    assert r["volume_total"] == 200
    assert r["economia_valor"] > 0


def test_mesmo_orgao_nao_gera_match():
    assert avaliar(demanda(1, FED), demanda(2, FED), FED, FED) is None


def test_naturezas_diferentes_nao_geram_match():
    assert avaliar(demanda(1, FED), demanda(2, FED2, natureza="capacitacao"), FED, FED2) is None


def test_objetos_diferentes_nao_geram_match():
    b = demanda(2, FED2, codigo_catalogo="Y-9", descricao="Serviço de vigilância armada")
    assert avaliar(demanda(1, FED), b, FED, FED2) is None


def test_federal_com_estadual_federal_gerencia_e_alerta():
    # Mesmo com o estadual comprando antes, o gerenciador deve ser o federal (art. 86, §8º)
    r = avaliar(demanda(1, FED, mes_previsto=5), demanda(2, EST, mes_previsto=2), FED, EST)
    assert r["caminho"]["gerenciador"] == "TRE-PB"
    assert any(a["tipo"] == "interfederativo" for a in r["alertas"])


def test_alerta_me_epp_quando_soma_passa_do_limite():
    r = avaliar(demanda(1, FED, valor_estimado=50_000), demanda(2, FED2, valor_estimado=40_000), FED, FED2)
    assert any(a["tipo"] == "me_epp" for a in r["alertas"])


def test_valor_sigiloso_nao_entra_na_economia_em_reais():
    r = avaliar(demanda(1, FED), demanda(2, FED2, valor_sigiloso=1), FED, FED2)
    assert r["economia_valor"] is None
    assert r["economia_pct"] > 0


def test_unidades_diferentes_nao_somam_volume():
    r = avaliar(demanda(1, FED), demanda(2, FED2, unidade="kit"), FED, FED2)
    assert r is None or (r["volume_total"] is None and any(a["tipo"] == "unidades" for a in r["alertas"]))


def test_meses_distantes_geram_alerta_de_prazo():
    r = avaliar(demanda(1, FED, mes_previsto=1), demanda(2, FED2, mes_previsto=5), FED, FED2)
    assert r is not None
    assert any(a["tipo"] == "prazo" for a in r["alertas"])
