# Testes essenciais

Execução: `python -m pytest -q` em `giramatch-backend/giramatch-backend` (SQLite).
Último resultado registrado: **28 passed** (SQLite). **PostgreSQL: NÃO VERIFICADO.**

| REQ | Critério | Teste existente | Tipo |
|---|---|---|---|
| REQ-001 | Nova demanda gera match | `test_api.py::test_nova_demanda_gera_match` | positivo |
| REQ-001 | Importar CSV | `test_api.py::test_importar_csv` | positivo |
| REQ-002 | Feed ordenado e explicado | `test_api.py::test_feed_de_matches_ordenado_e_explicado` | positivo |
| REQ-002 | Mesmo item e mês gera match forte | `test_matching.py::test_mesmo_item_mesmo_mes_gera_match_forte` | positivo |
| REQ-002 | Mesmo órgão, naturezas ou objetos diferentes não geram match | `test_mesmo_orgao_nao_gera_match`, `test_naturezas_diferentes_nao_geram_match`, `test_objetos_diferentes_nao_geram_match` | negativo |
| REQ-002 | Valor sigiloso escondido | `test_valor_sigiloso_escondido_do_outro_orgao`, `test_valor_sigiloso_nao_entra_na_economia_em_reais` | negativo |
| REQ-002 | Alertas (federal×estadual, ME/EPP, prazo, unidades) | 4 testes em `test_matching.py` | positivo |
| REQ-002 | Não ver match de terceiros | `test_api.py::test_nao_ve_match_de_terceiros` | negativo |
| REQ-003 | Os dois conectam, nasce o comitê | `test_api.py::test_conexao_dos_dois_lados_cria_comite` | positivo |
| REQ-003 | Recusa encerra o match | `test_api.py::test_recusa_encerra_match` | negativo |
| REQ-003 | Conversa entre os dois órgãos (lê, texto vazio, órgão de fora) | `test_api.py::test_conversa_entre_os_dois_orgaos` | positivo e negativo |
| — | Login e saúde da API | `test_api.py::test_health_e_login` | positivo |
| — | Usuários via variável de ambiente | `test_api.py::test_usuarios_do_ambiente` | positivo e negativo |

## Lacunas (a criar)
- Testes em PostgreSQL (`TEST_DATABASE_URL`; **apaga** as tabelas do banco indicado).
- Teste automatizado do front-end (hoje só verificação manual e de sintaxe).
