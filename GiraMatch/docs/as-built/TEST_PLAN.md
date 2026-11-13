# TEST_PLAN

Ambiente: Python 3.13, pytest 9, SQLite, Windows 11. Resultado na versão auditada: 19 passed + 8 de auditoria (1 xfail). **Versão corrigida: 28 passed** [C]. Original (`55b52a6`): **17 passed** [C].

## Testes existentes
| ID | Teste | Entrada → resultado esperado |
|---|---|---|
| T-01 | `test_health_e_login` | health 200; senha errada 401; sem token 401; login válido retorna órgão |
| T-02 | `test_feed_de_matches_ordenado_e_explicado` | feed por score, com motivos |
| T-03 | `test_valor_sigiloso_escondido_do_outro_orgao` | valor `null` para o outro órgão |
| T-04 | `test_conexao_dos_dois_lados_cria_comite` | duas conexões → comitê com 5 tarefas; terceiro recebe 404; reconectar dá 409 |
| T-05 | `test_recusa_encerra_match` | recusa encerra o match |
| T-06 | `test_nova_demanda_gera_match` | nova demanda → matches gerados |
| T-07 | `test_importar_csv` | CSV válido importa; linhas ruins vão em `erros` |
| T-08 | `test_nao_ve_match_de_terceiros` | outro órgão não vê o match |
| T-09 | `test_usuarios_do_ambiente` | usuários da variável: válido entra; órgão inexistente é ignorado |
| T-10 | `test_conversa_entre_os_dois_orgaos` | mensagem de um lida pelo outro; vazio 422; terceiro 404 |
| T-11..T-19 | 9 testes de `test_matching.py` | regras do motor (mesmo órgão, natureza, objetos, federal×estadual, ME/EPP, sigilo, unidades, prazo) |

## Testes mínimos a criar para a auditoria
| ID | Objetivo | Condição |
|---|---|---|
| A-01 | Toda a suíte em **PostgreSQL** | `TEST_DATABASE_URL` com banco descartável (apaga tabelas) |
| A-02 | Login: limite de tentativas / bloqueio | **feito** (T-F003, T-F003b) |
| A-03 | Mensagem com 4001 caracteres → 422 | API em execução |
| A-04 | Token expirado (>12 h) → 401 | relógio simulado |
| A-05 | CORS restrito ao domínio do site | `GIRAMATCH_CORS` definido |
| A-06 | Front-end ponta a ponta no navegador (login, feed, conectar, chat) | navegador real + API |
| A-07 | Reidentificação/dados reais: confirmar ausência no banco publicado | inspeção do banco |

## Testes da auditoria e da correção (`tests/test_auditoria.py`)
| ID | Teste | Achado |
|---|---|---|
| T-F001 | `test_falha_de_dependencia_banco_indisponivel` (503, mensagem genérica) | F-001 |
| T-F003 | `test_f003_login_bloqueia_apos_muitas_falhas` | F-003 |
| T-F003b | `test_f003_poucas_falhas_nao_bloqueiam_e_sucesso_zera` | F-003 |
| T-A01 | `test_req001_entrada_invalida_e_sem_login`, `test_req001_json_malformado` | REQ-001 |
| T-A02 | `test_req002_ausencia_de_dados_feed_vazio` | REQ-002 |
| T-A03 | `test_req003_mensagem_acima_do_limite`, `test_token_expirado_e_invalido`, `test_login_com_tentativa_de_injecao_sql` | REQ-003 / segurança |
