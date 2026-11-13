"""Dados de demonstração (FICTÍCIOS) para a maratona.

Os órgãos são reais, mas quantidades, valores, meses e códigos de catálogo
são inventados apenas para demonstrar o funcionamento.
"""
from .api import inserir_demanda, validar_demanda
from .auth import gerar_hash
from .matching import gerar_matches

SENHA_DEMO = "demo123"

ORGAOS = [
    ("TRE-PB", "Tribunal Regional Eleitoral da Paraíba", "eleitoral", "federal", "PB", "João Pessoa"),
    ("TRT 13", "Tribunal Regional do Trabalho da 13ª Região", "trabalho", "federal", "PB", "João Pessoa"),
    ("JFPB", "Justiça Federal na Paraíba", "federal", "federal", "PB", "João Pessoa"),
    ("TJPB", "Tribunal de Justiça da Paraíba", "estadual", "estadual", "PB", "João Pessoa"),
    ("TRE-RN", "Tribunal Regional Eleitoral do Rio Grande do Norte", "eleitoral", "federal", "RN", "Natal"),
]

NB = ["eficiência energética", "logística reversa", "restrição de substâncias perigosas"]
SOLAR = ["energia renovável", "logística reversa de módulos"]
AR = ["gás refrigerante de baixo impacto", "destinação adequada de resíduos"]
PAPEL = ["papel reciclado", "certificação florestal"]

DEMANDAS = {
    "TRE-PB": [
        dict(descricao="Notebooks corporativos", codigo_catalogo="CATMAT-DEMO-0001", categoria="TIC",
             quantidade=120, unidade="un", valor_estimado=760_000, mes_previsto=3, criterios_sustentaveis=NB),
        dict(descricao="Usina solar fotovoltaica em prédio próprio", codigo_catalogo="CATSER-DEMO-0101",
             categoria="Energia", tipo="servico", quantidade=300, unidade="kWp", valor_estimado=1_600_000,
             mes_previsto=6, criterios_sustentaveis=SOLAR),
        dict(descricao="Manutenção preventiva e corretiva de ar-condicionado", codigo_catalogo="CATSER-DEMO-0202",
             categoria="Manutenção", tipo="servico", quantidade=260, unidade="equipamento",
             valor_estimado=900_000, mes_previsto=8, fim_contrato_atual="2027-08-31", criterios_sustentaveis=AR),
        dict(descricao="Papel A4 reciclado", codigo_catalogo="CATMAT-DEMO-0003", categoria="Expediente",
             quantidade=2000, unidade="resma", valor_estimado=50_000, mes_previsto=2, criterios_sustentaveis=PAPEL),
        dict(descricao="Curso de fiscalização de contratos na Lei 14.133", natureza="capacitacao",
             categoria="Capacitação", quantidade=40, unidade="vaga", mes_previsto=5),
    ],
    "TRT 13": [
        dict(descricao="Notebooks corporativos", codigo_catalogo="CATMAT-DEMO-0001", categoria="TIC",
             quantidade=180, unidade="un", valor_estimado=1_140_000, mes_previsto=4, criterios_sustentaveis=NB),
        dict(descricao="Curso de fiscalização de contratos administrativos", natureza="capacitacao",
             categoria="Capacitação", quantidade=60, unidade="vaga", mes_previsto=6),
        dict(descricao="Outsourcing de impressão", codigo_catalogo="CATSER-DEMO-0303", categoria="TIC",
             tipo="servico", quantidade=1, unidade="contrato", valor_estimado=420_000, mes_previsto=11),
    ],
    "JFPB": [
        dict(descricao="Manutenção preventiva e corretiva de ar-condicionado", codigo_catalogo="CATSER-DEMO-0202",
             categoria="Manutenção", tipo="servico", quantidade=380, unidade="equipamento",
             valor_estimado=1_400_000, mes_previsto=9, fim_contrato_atual="2027-09-30", criterios_sustentaveis=AR),
        dict(descricao="Curso de fiscalização de contratos (EAD)", natureza="capacitacao",
             categoria="Capacitação", quantidade=25, unidade="vaga", mes_previsto=6),
    ],
    "TJPB": [
        dict(descricao="Usina solar fotovoltaica em prédios próprios", codigo_catalogo="CATSER-DEMO-0101",
             categoria="Energia", tipo="servico", quantidade=900, unidade="kWp", valor_estimado=4_800_000,
             valor_sigiloso=True, mes_previsto=6, criterios_sustentaveis=SOLAR),
        dict(descricao="Papel A4 reciclado", codigo_catalogo="CATMAT-DEMO-0003", categoria="Expediente",
             quantidade=3000, unidade="resma", valor_estimado=70_000, mes_previsto=3, criterios_sustentaveis=PAPEL),
        dict(descricao="Notebooks corporativos", codigo_catalogo="CATMAT-DEMO-0001", categoria="TIC",
             quantidade=250, unidade="un", valor_estimado=1_500_000, mes_previsto=5, criterios_sustentaveis=NB[:2]),
    ],
    "TRE-RN": [
        dict(descricao="Notebooks corporativos", codigo_catalogo="CATMAT-DEMO-0001", categoria="TIC",
             quantidade=90, unidade="un", valor_estimado=560_000, mes_previsto=3, criterios_sustentaveis=NB),
    ],
}


# --- MAIS DEMANDAS (fictícias) para variar os matches da demonstração -------------------
MOBILIARIO = ["restrição de substâncias perigosas", "madeira de origem certificada"]
FROTA = ["eficiência energética", "baixa emissão de poluentes"]
LIMPEZA = ["produtos biodegradáveis", "destinação adequada de resíduos"]

DEMANDAS_EXTRA = {
    "TRE-PB": [
        dict(descricao="Vigilância patrimonial armada 24 horas", codigo_catalogo="CATSER-DEMO-0404", categoria="Segurança",
             tipo="servico", quantidade=24, unidade="posto", valor_estimado=2_100_000, mes_previsto=10,
             fim_contrato_atual="2027-10-31"),
        dict(descricao="Cartuchos de toner para impressoras", codigo_catalogo="CATMAT-DEMO-0606", categoria="TIC",
             quantidade=800, unidade="un", valor_estimado=380_000, mes_previsto=4,
             criterios_sustentaveis=["logística reversa", "cartuchos remanufaturados"]),
        dict(descricao="Cadeiras ergonômicas giratórias", codigo_catalogo="CATMAT-DEMO-0808", categoria="Mobiliário",
             quantidade=150, unidade="un", valor_estimado=180_000, mes_previsto=5, criterios_sustentaveis=MOBILIARIO),
        dict(descricao="Veículos utilitários leves", codigo_catalogo="CATMAT-DEMO-0505", categoria="Frota",
             quantidade=6, unidade="un", valor_estimado=420_000, mes_previsto=7, criterios_sustentaveis=FROTA),
        dict(descricao="Link de internet dedicado", codigo_catalogo="CATSER-DEMO-0707", categoria="TIC",
             tipo="servico", quantidade=4, unidade="link", valor_estimado=260_000, mes_previsto=9,
             fim_contrato_atual="2027-09-20"),
        dict(descricao="Limpeza e conservação predial", codigo_catalogo="CATSER-DEMO-0909", categoria="Serviços gerais",
             tipo="servico", quantidade=8000, unidade="m2", valor_estimado=640_000, mes_previsto=12,
             fim_contrato_atual="2027-12-31", criterios_sustentaveis=LIMPEZA),
        dict(descricao="Curso de inteligência artificial para o setor público", natureza="capacitacao",
             categoria="Capacitação", quantidade=30, unidade="vaga", mes_previsto=8),
        dict(descricao="Curso de proteção de dados pessoais e LGPD", natureza="capacitacao",
             categoria="Capacitação", quantidade=35, unidade="vaga", mes_previsto=4),
        dict(descricao="Projeto conjunto de digitalização de acervo documental", natureza="outra", tipo="outro",
             categoria="Gestão documental", quantidade=1, unidade="projeto", valor_estimado=300_000, mes_previsto=7),
    ],
    "TRT 13": [
        dict(descricao="Vigilância patrimonial armada 24 horas", codigo_catalogo="CATSER-DEMO-0404", categoria="Segurança",
             tipo="servico", quantidade=18, unidade="posto", valor_estimado=1_650_000, mes_previsto=11,
             fim_contrato_atual="2027-11-30"),
        dict(descricao="Cartuchos de toner para impressoras", codigo_catalogo="CATMAT-DEMO-0606", categoria="TIC",
             quantidade=500, unidade="un", valor_estimado=240_000, mes_previsto=5,
             criterios_sustentaveis=["logística reversa", "cartuchos remanufaturados"]),
        dict(descricao="Cadeiras ergonômicas giratórias", codigo_catalogo="CATMAT-DEMO-0808", categoria="Mobiliário",
             quantidade=120, unidade="un", valor_estimado=150_000, mes_previsto=6, criterios_sustentaveis=MOBILIARIO),
        dict(descricao="Curso de inteligência artificial para o setor público", natureza="capacitacao",
             categoria="Capacitação", quantidade=45, unidade="vaga", mes_previsto=9),
        dict(descricao="Projeto conjunto de digitalização de acervo documental", natureza="outra", tipo="outro",
             categoria="Gestão documental", quantidade=1, unidade="projeto", valor_estimado=420_000, mes_previsto=8),
    ],
    "JFPB": [
        dict(descricao="Veículos utilitários leves", codigo_catalogo="CATMAT-DEMO-0505", categoria="Frota",
             quantidade=8, unidade="un", valor_estimado=560_000, mes_previsto=8, criterios_sustentaveis=FROTA),
        dict(descricao="Link de internet dedicado", codigo_catalogo="CATSER-DEMO-0707", categoria="TIC",
             tipo="servico", quantidade=3, unidade="link", valor_estimado=210_000, mes_previsto=10,
             fim_contrato_atual="2027-10-05"),
        dict(descricao="Limpeza e conservação predial", codigo_catalogo="CATSER-DEMO-0909", categoria="Serviços gerais",
             tipo="servico", quantidade=12000, unidade="m2", valor_estimado=950_000, mes_previsto=12,
             fim_contrato_atual="2027-12-15", criterios_sustentaveis=LIMPEZA),
        dict(descricao="Curso de proteção de dados pessoais e LGPD", natureza="capacitacao",
             categoria="Capacitação", quantidade=20, unidade="vaga", mes_previsto=5),
    ],
    "TJPB": [
        dict(descricao="Vigilância patrimonial armada 24 horas", codigo_catalogo="CATSER-DEMO-0404", categoria="Segurança",
             tipo="servico", quantidade=40, unidade="posto", valor_estimado=4_200_000, mes_previsto=10,
             fim_contrato_atual="2027-10-15"),
        dict(descricao="Cartuchos de toner para impressoras", codigo_catalogo="CATMAT-DEMO-0606", categoria="TIC",
             quantidade=1500, unidade="un", valor_estimado=700_000, mes_previsto=3,
             criterios_sustentaveis=["logística reversa", "cartuchos remanufaturados"]),
        dict(descricao="Cadeiras ergonômicas giratórias", codigo_catalogo="CATMAT-DEMO-0808", categoria="Mobiliário",
             quantidade=300, unidade="un", valor_estimado=330_000, mes_previsto=9, criterios_sustentaveis=MOBILIARIO[:1]),
        dict(descricao="Curso de inteligência artificial para o setor público", natureza="capacitacao",
             categoria="Capacitação", quantidade=60, unidade="vaga", mes_previsto=8),
        dict(descricao="Curso de proteção de dados pessoais e LGPD", natureza="capacitacao",
             categoria="Capacitação", quantidade=50, unidade="vaga", mes_previsto=4),
    ],
    "TRE-RN": [
        dict(descricao="Veículos utilitários leves", codigo_catalogo="CATMAT-DEMO-0505", categoria="Frota",
             quantidade=10, unidade="un", valor_estimado=700_000, mes_previsto=7, criterios_sustentaveis=FROTA),
        dict(descricao="Curso de inteligência artificial para o setor público", natureza="capacitacao",
             categoria="Capacitação", quantidade=25, unidade="vaga", mes_previsto=8),
        dict(descricao="Cartuchos de toner para impressoras", codigo_catalogo="CATMAT-DEMO-0606", categoria="TIC",
             quantidade=400, unidade="un", valor_estimado=190_000, mes_previsto=4,
             criterios_sustentaveis=["logística reversa"]),
    ],
}
for _sigla, _itens in DEMANDAS_EXTRA.items():
    DEMANDAS[_sigla] = DEMANDAS[_sigla] + _itens


EMAIL_FISCAL_DEMO = "fiscal@giramatch.demo"


def popular(conn, ano: int = 2027) -> dict:
    ids = {}
    for sigla, nome, ramo, esfera, uf, municipio in ORGAOS:
        cur = conn.execute(
            "INSERT INTO orgaos (sigla, nome, ramo, esfera, uf, municipio) VALUES (?, ?, ?, ?, ?, ?)",
            (sigla, nome, ramo, esfera, uf, municipio),
        )
        ids[sigla] = cur.lastrowid
        email = f"gestor@{sigla.lower().replace(' ', '').replace('-', '')}.giramatch.demo"
        conn.execute(
            "INSERT INTO usuarios (orgao_id, nome, email, senha_hash) VALUES (?, ?, ?, ?)",
            (cur.lastrowid, f"Gestor(a) {sigla}", email, gerar_hash(SENHA_DEMO)),
        )
    # Perfil de fiscalização: acompanha todos os comitês, sem demandas nem pontuação (cooperado = 0)
    fiscal = conn.execute(
        "INSERT INTO orgaos (sigla, nome, ramo, esfera, uf, municipio, cooperado) VALUES (?, ?, ?, ?, ?, ?, 0)",
        ("FISCAL", "Fiscalização das Contratações", "fiscalizacao", "federal", "PB", "João Pessoa"),
    )
    conn.execute(
        "INSERT INTO usuarios (orgao_id, nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?, 'fiscal')",
        (fiscal.lastrowid, "Fiscal das Contratações", EMAIL_FISCAL_DEMO, gerar_hash(SENHA_DEMO)),
    )
    for sigla, itens in DEMANDAS.items():
        for item in itens:
            inserir_demanda(conn, ids[sigla], validar_demanda({"ano": ano, **item}), origem="demo")
    resultado = gerar_matches(conn)
    conn.commit()
    return resultado
