# INVENTORY — arquivos e módulos (commit 09749e7)

Contagem de linhas medida por `wc -l` [C].

## Raiz (front-end e entrega)
| Arquivo | Linhas | Finalidade |
|---|---|---|
| `index.html` | 120 | Login e entrada em modo demonstração |
| `dashboard.html` | 68 | Painel de indicadores e pedidos de conexão |
| `nova-demanda.html` | 159 | Cadastro/edição de demanda (e importação) |
| `minhas-demandas.html` | 80 | Lista de demandas do órgão |
| `matches.html` | 53 | Feed de matches |
| `match-detalhe.html` | 98 | Detalhe do match (comparação, motivos, caminho jurídico) |
| `convites.html` | 42 | Pedidos de conexão |
| `comite.html` | 106 | Comitê, conversa e representantes (estes só no navegador) |
| `acompanhamento.html` | 93 | Tarefas do comitê |
| `app.js` | 554 | Núcleo: API, sessão, layout, utilitários, **modo demonstração** |
| `stylo.css` | 496 | Estilos |
| `logo-*.png` | — | Logos |
| `render.yaml` | 27 | Definição de deploy (API + PostgreSQL) — **não executada** |
| `DOCUMENTACAO.md` | 295 | Documentação da equipe (parcialmente desatualizada) |
| `docs/especificacao/*` | — | SPEC, RULES, TESTS, GUARDRAILS, HARNESS, EVIDÊNCIAS, ARQUITETURA.mmd |
| `docs/apresentacao.html` | 159 | Apresentação de 3 slides (offline) |
| `docs/as-built/*` | — | Este conjunto |

## Backend (`giramatch-backend/giramatch-backend/`)
| Arquivo | Linhas | Finalidade |
|---|---|---|
| `giramatch/api.py` | 686 | Rotas REST, validação, servidor HTTP |
| `giramatch/matching.py` | 349 | Motor de match |
| `giramatch/seed.py` | 173 | Dados fictícios |
| `giramatch/db.py` | 119 | Conexão SQLite/PostgreSQL, utilitários de banco |
| `giramatch/__main__.py` | 111 | Linha de comando (`iniciar`, `demo`, `usuario`, `servir`) |
| `giramatch/auth.py` | 54 | Senhas e sessões |
| `giramatch/config.py` | 47 | Parâmetros e variáveis de ambiente |
| `giramatch/schema.sql` / `schema_pg.sql` | 117 / 115 | Tabelas |
| `tests/test_api.py` | 206 | 10 testes de API |
| `tests/test_matching.py` | 64 | 9 testes do motor |
| `exemplos/pca_exemplo.csv` | 4 | CSV de exemplo (fictício) |
| `requirements.txt`, `.env.exemplo`, `.gitignore`, `README.md` | — | Dependências, variáveis, ignorados, documentação |

## Árvore resumida
```
GiraMatch/            (origem: commit 55b52a6 → versão analisada 09749e7)
├─ *.html (9), app.js, stylo.css, logo-*.png, render.yaml, DOCUMENTACAO.md
├─ docs/  (especificacao/, as-built/, apresentacao.html)
└─ giramatch-backend/giramatch-backend/
   ├─ giramatch/ (api, matching, seed, db, auth, config, __main__, schema*.sql)
   ├─ tests/  ├─ exemplos/  └─ requirements.txt, .env.exemplo, README.md
```
Arquivo `giramatch.db` (SQLite local) existe na pasta do backend mas **não é versionado** (`*.db` ignorado) e **não foi inspecionado** [C].
