# TRACEABILITY (preliminar)

**Base de conformidade: AUSENTE.** O edital/desafio e os critérios da banca não foram fornecidos. Os IDs abaixo vêm de `docs/especificacao/SPEC.md`, que **foi escrito a partir do próprio protótipo** (não é fonte independente). Portanto, esta rastreabilidade mostra consistência interna, não aderência a um edital.

| ID | Requisito (SPEC) | Arquivo / função | Teste / evidência | Situação |
|---|---|---|---|---|
| REQ-001 | Cadastrar/importar demanda | `api.py`: `criar_demanda`, `inserir_demanda`, `validar_demanda`, `importar_demandas` | T-06, T-07 | Verificado em SQLite |
| REQ-002 | Match explicável com sigilo | `matching.py`: `gerar_matches`; `api.py`: `ver_match`, `listar_matches` | T-02, T-03, T-08, T-11..T-19 | Verificado em SQLite |
| REQ-003 | Conectar e cooperar (comitê + conversa) | `api.py`: `decidir`, `criar_comite`, `enviar_mensagem`, `obter_comite`; `comite.html` | T-04, T-05, T-10 | Verificado em SQLite (API); **front-end: não verificado em navegador** |
| — | Login por órgão | `auth.py`, `api.py` (login) | T-01, T-09 | Verificado em SQLite |
| — | Deploy sem terminal | `render.yaml`, `db.py` (PostgreSQL), `__main__.py` | — | **NÃO VERIFICADO** |
| — | Modo demonstração | `app.js` (`Demo`), `index.html` | verificação estática e script Node | Parcial (sem navegador) |
