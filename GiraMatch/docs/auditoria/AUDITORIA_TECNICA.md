# Auditoria técnica — GiraMatch

## Declaração de independência (leia primeiro)
**Esta revisão NÃO é independente.** Quem a conduziu (Claude) também escreveu grande parte do código, da especificação (`SPEC.md` e demais) e da documentação as-built auditados. Há viés provável de confirmação. **Recomenda-se revisão cruzada por outro integrante da equipe.**

## Identificação
- **Versão auditada:** commit `fc5ea42` + `tests/test_auditoria.py` (criado nesta etapa). Original: `55b52a6` (ZIP SHA-256 em `docs/as-built/AS_BUILT.md`).
- **Ambiente:** Windows 11, Python 3.13.14, pytest 9.x, SQLite. Data: 12/11/2026.
- **Base de conformidade:** **edital, desafio e critérios da banca NÃO fornecidos.** A avaliação é **técnica/operacional**, **não** de aderência ao problema nem aos critérios do edital. `SPEC.md`/`RULES.md` foram escritos a partir do próprio protótipo e não são referencial independente.
- **Não alterei o MVP.** Só criei testes adicionais.

## Parecer executivo
O núcleo da API funciona e foi **comprovado por execução em SQLite**: cadastro de demanda, match explicado com sigilo, conexão dos dois lados, comitê e conversa entre órgãos (26 testes passam; 1 falha esperada e documentada, F-001). Porém, o **caminho de produção e de demonstração não foi comprovado**: PostgreSQL, deploy, front-end em navegador real e capturas. Há também uma falha de robustez confirmada (banco indisponível derruba a resposta). Por isso **não é possível aprovar** a prontidão para a demonstração.

## Decisão final
**NÃO APTO — evidência insuficiente.**
Isto **não** afirma que o software falha: o fluxo central passou nos testes em SQLite. A decisão decorre de faltar evidência sobre requisitos P0 no caminho que será demonstrado (API publicada com PostgreSQL e interface no navegador) e de haver um achado Alto aberto (F-001).

## Evidências executadas
| Comando | Resultado |
|---|---|
| `python -m pytest -q` (completo) | **26 passed, 1 xfailed** (SQLite) — o xfail é F-001, falha esperada e registrada |
| `python -m pytest tests/test_auditoria.py` (antes do `xfail`) | 7 passed, 1 failed (`RemoteDisconnected`, traceback em `api.py:650`) |
| Original `55b52a6` | 17 passed (etapa anterior) |

## Matriz requisito → evidência → resultado
| ID | Resultado | Evidência | Restrição |
|---|---|---|---|
| REQ-001 Cadastrar/importar demanda | **ATENDE PARCIALMENTE** | `test_nova_demanda_gera_match`, `test_importar_csv`, `test_req001_entrada_invalida_e_sem_login` (mês 13 e descrição vazia → 422; sem login → 401), `test_req001_json_malformado` | só API em SQLite; tela `nova-demanda.html` não verificada em navegador |
| REQ-002 Match explicável e sigilo | **ATENDE PARCIALMENTE** | `test_feed_de_matches_ordenado_e_explicado`, `test_valor_sigiloso_escondido_do_outro_orgao`, `test_nao_ve_match_de_terceiros`, 9 testes do motor, `test_req002_ausencia_de_dados_feed_vazio` | idem; economia em reais é ilustrativa (parâmetros em `config.py`) |
| REQ-003 Conectar e cooperar | **ATENDE PARCIALMENTE** | `test_conexao_dos_dois_lados_cria_comite`, `test_recusa_encerra_match`, `test_conversa_entre_os_dois_orgaos`, `test_req003_mensagem_acima_do_limite` (4000 ok, 4001 → 422) | conversa ao vivo entre dois navegadores e atualização a cada 5 s **NÃO VERIFICADAS**; só com API publicada |
| Login e sessão | **ATENDE PARCIALMENTE** | `test_health_e_login`, `test_token_expirado_e_invalido`, `test_login_com_tentativa_de_injecao_sql` | sem limite de tentativas (F-003) |
| Falha de dependência (banco) | **NÃO ATENDE** | `test_falha_de_dependencia_banco_indisponivel` (xfail), `api.py:650` | F-001 |
| Publicação sem terminal (PostgreSQL + Render) | **NÃO VERIFICADO** | — | `db.py`, `schema_pg.sql`, `render.yaml` nunca executados |
| Distinção real × simulado | **ATENDE PARCIALMENTE** | etiqueta "Modo demonstração" no app; slide 3 e README declaram simulação | verificado só por leitura, sem navegador |
| Correspondência MVP × PNG × apresentação | **ATENDE PARCIALMENTE** | PNG e slide 2 descrevem os mesmos componentes (leitura) | apresentação sem capturas reais, sem nome da equipe e sem URL |
| IA / prompt injection / citações inventadas | **NÃO APLICÁVEL** | busca no código: nenhuma chamada a modelo (só comentário em `matching.py`) | Res. CNJ 615/2025: pontos só valem se houver IA; a alteração 674/2026 **não foi verificada** |
| Demonstração em ≤ 5 min | **NÃO VERIFICADO** | roteiro em `HARNESS.md` | depende do deploy |
| LGPD / dados fictícios | **ATENDE PARCIALMENTE** | dados do `seed.py` e do CSV são fictícios (leitura) | sem verificação de reidentificação; senhas fictícias em código público (F-005) |

## Achados priorizados
| ID | Criticidade | Achado | Evidência | Correção recomendada | Responsável sugerido |
|---|---|---|---|---|---|
| F-001 | **Alto** | Com o banco indisponível, o servidor fecha a conexão **sem responder** (a chamada `conectar` fica fora do `try`) | `api.py:650`; teste xfail; traceback observado | mover a conexão para dentro do `try` e responder 503 com mensagem genérica | desenvolvedor do backend |
| F-002 | **Alto** | Caminho de produção **não verificado**: PostgreSQL, deploy e URL da API | `db.py`, `render.yaml` | rodar a suíte com `TEST_DATABASE_URL`, fazer o deploy e registrar `/api/health` | quem publica |
| F-003 | Médio | Sem limite de tentativas de login (15 erros seguidos → sempre 401) | `test_login_sem_limite_de_tentativas_observado` | limitar por IP/e-mail ou aceitar o risco no protótipo | backend |
| F-004 | Médio | CORS padrão `*` | `config.py:20`, `api.py:596` | definir `GIRAMATCH_CORS` com o domínio do site | quem publica |
| F-005 | Médio | Senhas de demo e de teste legíveis no código público | `index.html:88-92`, `seed.py:10` | manter só enquanto fictícias; nunca reutilizar | front-end |
| F-006 | Médio | Log padrão do `http.server` grava IP e URL; erros imprimem traceback | `api.py:591`, `api.py:675` | revisar o que é logado na hospedagem (inferido, não medido) | backend |
| F-007 | Médio | Front-end sem teste automatizado; ~35 usos de `innerHTML` com escape presumido | contagem por `grep`; sem leitura integral | testes de navegador e revisão de XSS | front-end |
| F-008 | Médio | Apresentação incompleta: sem capturas reais, sem nome da equipe e sem URL | `docs/apresentacao.html` slides 1 e 3 | preencher antes de apresentar | equipe |
| F-009 | Baixo | `DOCUMENTACAO.md` desatualizada (SQLite, `127.0.0.1:8000`) | linhas 5, 30, 32, 58 | atualizar | equipe |
| F-010 | Baixo | Modo demonstração sempre mostra o TRE-PB, qualquer conta | `app.js` (`Demo`) | documentar ou implementar troca de órgão | front-end |
| F-011 | Baixo | Auditoria não independente | declaração acima | revisão cruzada | equipe |

## Teste demonstrável por requisito P0
| REQ | Positivo | Entrada inválida | Falha de dependência |
|---|---|---|---|
| REQ-001 | `test_nova_demanda_gera_match` | `test_req001_entrada_invalida_e_sem_login`, `test_req001_json_malformado` | F-001 (banco fora → **falha atual**) |
| REQ-002 | `test_feed_de_matches_ordenado_e_explicado` | `test_nao_ve_match_de_terceiros`, `test_valor_sigiloso_escondido_do_outro_orgao` | F-001 (idem); ausência de dados: `test_req002_ausencia_de_dados_feed_vazio` |
| REQ-003 | `test_conversa_entre_os_dois_orgaos` | `test_req003_mensagem_acima_do_limite`, texto vazio e órgão de fora no teste de conversa | F-001 (idem) |

## Correções mínimas para apresentar
1. **F-001:** responder 503 quando o banco não abre (poucas linhas).
2. **F-002:** executar o deploy e a suíte em PostgreSQL; registrar a saída.
3. Testar a demo ponta a ponta **no navegador**, com dois órgãos, e salvar as capturas.
4. Preencher nome da equipe e URL na apresentação; trocar `GIRAMATCH_CORS` pelo domínio.
5. Dizer à banca o que é simulado (modo demonstração) e que os dados são fictícios.

## Roteiro de reteste
1. `python -m pytest -q` → esperado: tudo passa; F-001 deixa de ser xfail (remover a marca).
2. `TEST_DATABASE_URL=<banco descartável> python -m pytest -q` → esperado: mesma suíte passa.
3. `GET <URL da API>/api/health` → 200.
4. Dois navegadores (TRE-PB e TJPB): conectar, abrir o comitê, trocar mensagens (em até 5 s), com capturas.
5. 15 logins errados → avaliar a política escolhida (F-003).
6. Repetir esta auditoria com **outra pessoa** e com o edital em mãos.

## Limites desta auditoria
Sem edital; sem PostgreSQL, deploy, Docker e navegador; leitura parcial de `api.py`, `matching.py` e das páginas HTML (ver `AS_BUILT.md`); a varredura de segredos foi por padrões; a citação da Res. CNJ 674/2026 vem de documento externo e não foi confirmada.
