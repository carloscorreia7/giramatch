# REMEDIATION_PLAN

**Versão de entrada (fixada):** tag `v0-auditada` = commit `27d941d`. **Original:** tag `v0-original` = `55b52a6`.
**Versão corrigida:** tag `v1-corrigida` (commit indicado em `FINAL_VALIDATION.md`).
Observação sobre "diretório distinto": como o projeto está sob controle de versão, a separação foi feita por **tags e commits** (restaurar com `ROLLBACK.md`), e não por pastas duplicadas. O ZIP da versão corrigida é entregue à parte.

## Entradas e limites
- Presentes: relatório de auditoria, SPEC/RULES/TESTS/GUARDRAILS/HARNESS, documentos as-built, `.env.exemplo`, dependências, apresentação e PNG, dados fictícios e testes.
- **Ausentes:** edital/desafio e critérios da banca; **exemplo de apresentação HTML a seguir** (usei o layout simples próprio); orçamento de tempo definido pela equipe.
- **Orçamento de tempo assumido:** o que cabe em uma sessão de trabalho, sem ampliar o escopo. O que depende de ambiente que não existe aqui (PostgreSQL, deploy, navegador) ficou como pendência.

## Matriz de planejamento
| Achado | Req. | Crit. | Problema | Correção planejada | Arquivos | Teste | Risco de regressão | Situação inicial | Corte |
|---|---|---|---|---|---|---|---|---|---|
| F-001 | REQ-001..003 | Alto | banco fora → cliente sem resposta | `conectar` dentro de `try`; 503 genérico | `api.py` | T-F001 | baixo | aberto (xfail) | **P0** |
| F-003 | login | Médio | sem limite de tentativas | contadores por IP+e-mail e por IP; 429 | `auth.py`, `api.py`, `config.py` | T-F003, T-F003b | médio (bloqueio indevido de usuário legítimo) | aberto | P1 |
| F-006 | LGPD | Médio | log com IP e URL | `log_request`/`log_message` próprios | `api.py` | execução real (log) | baixo | aberto | P1 |
| F-009 | doc | Baixo | `DOCUMENTACAO.md` desatualizada | atualizar texto | `DOCUMENTACAO.md` | revisão | nenhum | aberto | P2 |
| F-004 | segurança | Médio | CORS `*` | aviso na subida; definir domínio na hospedagem | `__main__.py`, README | execução (aviso) | nenhum | aberto | P1 (parcial) |
| F-002 | prod. | Alto | PostgreSQL/deploy não verificados | **não corrigível aqui** | — | — | — | aberto | P0 (pendente) |
| F-005 | LGPD | Médio | senhas fictícias em código público | **mantida** (aceita por ser fictícia) | — | — | — | aberto | P2 |
| F-007 | qualidade | Médio | sem teste de front-end | **não corrigível aqui** (sem navegador) | — | — | — | aberto | P1 (pendente) |
| F-008 | apresentação | Médio | sem capturas, nome da equipe e URL | **depende da equipe** | — | — | — | aberto | P1 (pendente) |
| F-010 | demo | Baixo | demo sempre TRE-PB | **mantida**, documentada | — | — | — | aberto | P2 |
| F-011 | processo | Baixo | auditoria não independente | **não corrigível por mim** | — | — | — | aberto | — |

Ordem seguida: crítico/alto corrigível (F-001) → segurança e LGPD (F-003, F-006, F-004) → documentação (F-009, PNG, apresentação).
