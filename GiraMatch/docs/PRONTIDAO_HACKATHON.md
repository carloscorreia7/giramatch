# PRONTIDÃO DO HACKATHON — GiraMatch

**Projeto:** GiraMatch (cooperação entre órgãos públicos por "match" de demandas)
**Versão/commit/hash:** tag `v1-corrigida` = `d7f7b103555ea9ba1f8c2591d5b6e179027b35d7`. Original: `55b52a6` (`v0-original`). Auditada: `27d941d` (`v0-auditada`).
**Ambiente:** Windows 11, Python 3.13.14, pytest 9.x, SQLite. Docker: não disponível.
**Desafio e fluxo P0:** edital e critérios da banca **NÃO fornecidos** (base provisória = descrição da equipe em `DOCUMENTACAO.md`). Fluxo P0: cadastrar demanda → match explicado → "Conectar" dos dois órgãos → comitê com conversa.
**Data e responsáveis:** 12/11/2026. Correção e testes feitos pelo **mesmo agente de IA que desenvolveu o código (sem independência)**; revisor humano: [preencher].
**Responsável pela validação jurídica:** **NÃO DEFINIDO.**

## 1. Resumo do MVP
Órgãos públicos planejam compras e capacitações isoladamente. O GiraMatch sugere parcerias entre órgãos com demandas parecidas, explica o porquê (score, motivos, caminho jurídico, alertas) e, quando os dois aceitam, abre um comitê com cronograma e conversa. O usuário é o gestor de contratações. A decisão de cooperar é sempre humana. Dados 100% fictícios.

## 2. Resultado dos testes
| ID | Cenário | Comando/passos | Esperado | Observado | Estado | Evidência |
|---|---|---|---|---|---|---|
| T-01 | Fluxo principal (via API) | `python -m pytest -q` | comitê criado; mensagem de um órgão lida pelo outro | passou | **PASSOU** | `test_conexao_dos_dois_lados_cria_comite`, `test_conversa_entre_os_dois_orgaos` |
| T-01b | Fluxo pela interface no navegador e com PostgreSQL publicado | — | — | sem navegador, PostgreSQL nem deploy | **NÃO EXECUTADO** | — |
| T-02 | Entrada inválida | idem | 422 (mês 13, descrição vazia, mensagem de 4001 caracteres); JSON malformado rejeitado | conforme | **PASSOU** | `test_req001_*`, `test_req003_mensagem_acima_do_limite` |
| T-03 | Banco indisponível | idem | 503 genérico, sem vazar caminho | conforme (SQLite) | **PASSOU** | `test_falha_de_dependencia_banco_indisponivel` |
| T-04 | Acesso, logs, dados | idem + execução real da API (`servir`) | órgão de fora 404; valor sigiloso oculto; token inválido 401; 8 falhas → 429; log sem IP/URL | conforme | **PASSOU** | testes + `versao-corrigida/FINAL_VALIDATION.md` |
| T-04b | Segredos na interface/pacote | varredura por padrões; lista do ZIP | nenhum segredo real | só credenciais **fictícias** (`demo123` e conta de teste) em `index.html` | **PASSOU, com exceção declarada** | — |
| T-05 | IA jurídica | — | — | MVP sem LLM | **NÃO APLICÁVEL** | busca no código |
| T-06 | Regressão | `python -m pytest -q` | tudo passa | **28 passed** (original: 17) | **PASSOU** | `especificacao/EVIDENCIAS_EXECUCAO.md` |

## 3. Correções e riscos
| Falha | Prioridade | Alteração | Teste | Situação final | Risco residual |
|---|---|---|---|---|---|
| F-001 banco fora → cliente sem resposta | P0 | `api.py`: 503 genérico | T-03 | corrigida (SQLite) | não executada em PostgreSQL |
| F-002 PostgreSQL e deploy nunca executados | **P0** | nenhuma | T-01b | **ABERTA** | principal risco da demo publicada |
| F-003 sem limite de login | P1 | 429 após 8 falhas | T-04 | corrigida | contadores em memória |
| F-006 log com IP/URL | P1 | log enxuto | T-04 | corrigida | traceback de erro 500 vai ao stderr |
| F-004 CORS `*` | P1 | aviso na subida | — | parcial | definir `GIRAMATCH_CORS` na hospedagem |
| F-007/F-008 front sem teste; apresentação sem capturas, equipe e URL | P1 | nenhuma | — | **ABERTAS** | — |

## 4. Situação antes e depois
| Item | Estado inicial (`55b52a6`) | Estado final (`d7f7b10`) | Evidência |
|---|---|---|---|
| Inicialização | testes 17 passed; API local não iniciada por mim | `demo` + `servir` iniciam; `/api/health` 200 | execução local (banco temporário) |
| Fluxo P0 | coberto por testes de API | idem + conversa entre órgãos | 17 → 28 testes |
| Entrada inválida | validação existente, pouco testada | testada (422) | T-02 |
| Segurança/dados | sem limite de login; log com IP/URL; banco fora derrubava a resposta | 429; log enxuto; 503 | T-03, T-04 |

## 5. Declarações para o pitch
- **Reais e comprovadas:** API, regras do match, sigilo de valores, decisão dos dois lados, comitê e conversa (testados em **SQLite**, via API).
- **Simuladas:** modo demonstração do navegador (dados fictícios locais; sempre visão do TRE-PB; sem conversa entre órgãos), rotulado na tela.
- **Não verificadas:** PostgreSQL, deploy no Render, interface no navegador, apresentação HTML aberta, regras jurídicas (sem validação de jurista), alteração "Res. CNJ 674/2026".
- **Internet:** necessária para a demo entre órgãos (API publicada, que "dorme" no plano gratuito); o modo demonstração funciona sem servidor.
- **Como executar:** pasta `giramatch-backend/giramatch-backend`: `python -m giramatch demo`, `python -m giramatch servir` (parar: Ctrl+C), testes: `python -m pytest -q`; depois abrir `index.html`.
- **Como reverter:** `versao-corrigida/ROLLBACK.md` (tags `v0-original`, `v0-auditada`).
- **Validação jurídica humana:** **pendente** (responsável não definido).

## 6. Versão e integridade
- **Commit/hash da versão final:** `d7f7b103555ea9ba1f8c2591d5b6e179027b35d7` (depois dele só mudou documentação).
- **ZIP:** `docs/GiraMatch_v1_corrigida.zip` (git archive da tag; sem `.env`, banco ou cache; `.env.exemplo` sem valores reais).
- **SHA-256 do ZIP:** `c24eb1439a27fb24457a4cff2e386d58bde21308fc226c9c301bbafff9a7b113` (`docs/SHA256SUMS.txt`).
- **Data/hora do congelamento:** 12/11/2026, 21:18 (-03:00), conforme o commit.

## 7. Decisão final
- [ ] APTO PARA DEMONSTRAÇÃO
- [ ] APTO COM RESSALVAS
- [ ] NÃO APTO PARA DEMONSTRAÇÃO
- [x] **NÃO VERIFICADO / EVIDÊNCIA INSUFICIENTE**

**Justificativa baseada em evidências:** T-01 passou na API em SQLite, mas não foi executado no ambiente que será demonstrado (interface no navegador, API publicada com PostgreSQL), e F-002 (P0) permanece aberta. Não é "não apto": nada executado falhou.
**Confiança qualitativa:** **MÉDIA** para o núcleo da API; **BAIXA** para a demonstração ao vivo.
**Limitações desta análise:** sem edital; sem independência; sem navegador, PostgreSQL, deploy nem Docker; leitura parcial de `api.py`, `matching.py` e das páginas HTML; sem validação jurídica. Não é certificação de segurança, conformidade legal ou homologação.

**Fase 7 (manhã seguinte, nova sessão):** "Execute somente a Fase 7 do Protocolo de Emergência sobre a versão `v1-corrigida` (`d7f7b10`). Revalide T-01 e T-02 no equipamento da apresentação, confirme rede, portas e dependências, teste a contingência e não introduza funcionalidades novas. Pare apenas diante de P0 impeditivo."
