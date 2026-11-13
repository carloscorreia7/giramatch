# AUDIT_REMEDIATION_MATRIX

Classificação: **OK** (corrigido e comprovado) · **OK COM RESSALVA** · **NÃO OK** · **NÃO VERIFICADO**.

| Achado | Antes | Alteração | Teste / evidência | Resultado | Situação final | Risco residual |
|---|---|---|---|---|---|---|
| F-001 banco fora → sem resposta | NÃO ATENDE (xfail, `RemoteDisconnected`) | `conectar` em `try`; 503 genérico | T-F001 `test_falha_de_dependencia_banco_indisponivel` passou; 28 passed | 503 e sem vazar o caminho | **OK** (em SQLite) | o mesmo caminho em PostgreSQL não foi executado |
| F-003 sem limite de login | 15 falhas → sempre 401 | bloqueio por IP+e-mail e por IP; 429 | T-F003, T-F003b passaram; execução real: 8×401, depois 429 (inclusive com senha certa) | bloqueio comprovado | **OK COM RESSALVA** | contadores em memória; atrás de proxy o IP visto pode ser o do proxy; bloqueio pode afetar um usuário legítimo por 5 min |
| F-006 log com IP/URL | log padrão com IP e URL | log próprio sem IP e sem query | execução real: `GET /api/health?teste=segredo123` apareceu como `GET /api/health -> 200` | comprovado | **OK COM RESSALVA** | o traceback de erro 500 continua indo ao stderr (pode ter dados do contexto); logs da hospedagem não auditados |
| F-004 CORS `*` | padrão aberto | aviso na subida (PostgreSQL + `*`) | só leitura do código; aviso **não executado** | parcial | **OK COM RESSALVA** | o padrão continua `*`; é preciso definir `GIRAMATCH_CORS` na hospedagem |
| F-009 documentação desatualizada | cita só SQLite | texto atualizado | revisão | corrigido | **OK** | — |
| F-002 PostgreSQL/deploy | NÃO VERIFICADO | nenhuma | — | sem ambiente | **NÃO VERIFICADO** | principal risco do caminho de produção |
| F-005 senhas fictícias no código | presente | mantida e documentada | — | — | **OK COM RESSALVA** | qualquer visitante lê; nunca reutilizar |
| F-007 sem teste de front-end | ausente | nenhuma | — | sem navegador | **NÃO VERIFICADO** | XSS e UI sem prova |
| F-008 apresentação incompleta | faltam capturas, nome, URL | contagem de testes atualizada | leitura (0 recursos externos) | parcial | **NÃO OK** | pendente da equipe |
| F-010 demo sempre TRE-PB | presente | mantida | — | — | **OK COM RESSALVA** | documentado |
| F-011 auditoria não independente | presente | — | — | — | **NÃO OK** | depende de revisão cruzada |

## Requisitos (reauditoria)
| Requisito | Antes | Depois | Evidência |
|---|---|---|---|
| REQ-001 | ATENDE PARCIALMENTE | ATENDE PARCIALMENTE | testes de API passam (28); UI/PG não verificados |
| REQ-002 | ATENDE PARCIALMENTE | ATENDE PARCIALMENTE | idem |
| REQ-003 | ATENDE PARCIALMENTE | ATENDE PARCIALMENTE | idem; chat entre dois navegadores não verificado |
| Falha de dependência | NÃO ATENDE | **ATENDE** (SQLite) | T-F001 |
| Publicação sem terminal | NÃO VERIFICADO | NÃO VERIFICADO | — |
