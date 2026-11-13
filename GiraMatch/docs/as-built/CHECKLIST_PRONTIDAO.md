# Checklist de prontidão para a auditoria técnica

- [x] Entrada e ambiente identificados (Windows 11, Python 3.13.14, SQLite)
- [x] Integridade do original registrada (commit `55b52a6`, SHA-256 do ZIP em `AS_BUILT.md`)
- [x] Comando de inicialização identificado (`python -m giramatch servir`)
- [x] Fluxo principal mapeado (`AS_BUILT.md`, `TRACEABILITY.md`)
- [x] Dependências e serviços externos descritos (nenhum serviço externo)
- [x] Segredos localizados com valores redigidos (`AS_BUILT.md`)
- [x] Lacunas explicitadas (`KNOWN_ISSUES.md`)
- [x] Evidências referenciadas (`../especificacao/EVIDENCIAS_EXECUCAO.md`; original: 17 passed; atual: 19 passed)
- [ ] **Edital e critérios da banca** (necessários para avaliar aderência funcional)
- [ ] Testes em **PostgreSQL**
- [ ] Deploy executado e URL pública
- [ ] Teste ponta a ponta no **navegador** e capturas reais
- [ ] Leitura integral de `api.py`, `matching.py` e das páginas HTML pelo auditor

Nenhum parecer de aprovação ou reprovação é emitido nesta etapa.

## Comandos
```
cd giramatch-backend/giramatch-backend
python -m pip install pytest "psycopg[binary]"
python -m pytest -q
python -m giramatch demo && python -m giramatch servir
```
