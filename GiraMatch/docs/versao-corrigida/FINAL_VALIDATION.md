# FINAL_VALIDATION

## Declaração final
# ESTADO NÃO OK — validação incompleta

Isto **não** afirma que o software falha: tudo o que pôde ser executado passou. A conclusão é "incompleta" porque o fluxo P0 **não foi comprovado no caminho que será demonstrado** (PostgreSQL, API publicada e interface em navegador), como exige o critério do Prompt 5. Este resultado **não é certificação de segurança, de conformidade legal nem homologação institucional.**

**Independência:** correção, testes e reauditoria foram feitos pelo mesmo agente que criou o código. Recomenda-se revisão cruzada humana.

## Versão e ambiente
- Entrada: `v0-auditada` (`27d941d`). Original: `v0-original` (`55b52a6`). Saída: tag `v1-corrigida` (hash na saída de `git rev-parse v1-corrigida`).
- Windows 11, Python 3.13.14, pytest 9.x, SQLite. Data: 12/11/2026.

## Evidências executadas
| # | Verificação | Comando / método | Resultado |
|---|---|---|---|
| 1 | Instalação e compilação | `python -m py_compile giramatch/*.py` | sem erro |
| 2 | Suíte completa (regressão) | `python -m pytest -q` | **28 passed** (diagnóstico: 26 passed + 1 xfailed) |
| 3 | Achados corrigidos | T-F001, T-F003, T-F003b | passaram |
| 4 | Inicialização e fluxo (execução real) | `demo` + `servir` em banco temporário (porta 8766) | `/api/health` 200 |
| 5 | Limite de login (execução real) | 9 logins errados em sequência + 1 correto | 8×401, depois 429, inclusive com a senha certa |
| 6 | Log sem IP/URL (execução real) | `GET /api/health?teste=segredo123` | log: `GET /api/health -> 200` (sem IP e sem a query) |
| 7 | Segredos | varredura por padrões | só a credencial **fictícia** de demonstração em `index.html`; nenhum `.env` versionado; `DATABASE_URL` só com marcadores (`usuario:senha@host`) |
| 8 | Variáveis de ambiente | leitura de `config.py`/`.env.exemplo` | documentadas, incluindo as 3 novas |
| 9 | Arquitetura documentada × implementada | contagem de rotas (20) e componentes | coerente; PNG atualizado e conferido visualmente |
| 10 | Recursos da apresentação | busca por `src/href/url(http…)` | 0 recursos externos (funciona offline); **não aberta em navegador** |
| 11 | Supervisão humana / guardrails | testes de decisão (`conectar`/`recusar`, 409 ao redecidir), leitura | decisão sempre do gestor; sem IA no MVP |

## Critérios do Prompt 5
| Critério | Situação |
|---|---|
| Instala e inicia sem erro impeditivo | **Sim** (SQLite, local) |
| Fluxo principal ponta a ponta | **API: sim (SQLite)**; interface e PostgreSQL: **não verificados** |
| Testes essenciais aprovados | **Sim** (28) |
| Sem achado crítico/alto sem tratamento | **Não**: F-002 (alto) permanece **não verificado** |
| Sem segredo real exposto | **Sim** (só credenciais fictícias) |
| Segurança/LGPD/rastreabilidade/supervisão humana ativas | **Parcial** (ver `RESIDUAL_RISKS.md`) |
| Documentação corresponde à implementação | **Sim**, conferida para o que mudou |
| PNG e apresentação refletem a versão corrigida | **Sim** (PNG); apresentação **sem capturas reais** |
| Sem regressões relevantes | **Sim** (28 passed, antes 26+1xfail) |

## Dependências externas
- **Testado de verdade:** API + SQLite.
- **Simulado e declarado:** modo demonstração do navegador.
- **Pendente (não executado):** PostgreSQL, deploy no Render, Docker, navegador real.

## Pendências para chegar a ESTADO OK COM RESSALVAS
1. Rodar a suíte em PostgreSQL (`TEST_DATABASE_URL`) e fazer o deploy; registrar `/api/health` publicado.
2. Testar dois órgãos no navegador (conectar e conversar) e salvar capturas.
3. Preencher nome da equipe, URL e capturas na apresentação.
4. Definir `GIRAMATCH_CORS` com o domínio do site.
5. Revisão cruzada por outra pessoa e, se existir, o edital.
