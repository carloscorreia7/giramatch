# ARCHITECTURE — componentes, integrações, fluxos e dependências

Imagem: [arquitetura_as_built.png](arquitetura_as_built.png) (gerada por script, sem ferramenta de diagramação externa).
Fonte editável equivalente (Mermaid): [../especificacao/ARQUITETURA.mmd](../especificacao/ARQUITETURA.mmd).

## Componentes [C]
| Componente | Tecnologia | Responsabilidade |
|---|---|---|
| Front-end | HTML/CSS/JS puro | telas, sessão (`sessionStorage`), chamadas `fetch` à API, modo demonstração |
| API | Python `http.server` | roteamento, autenticação, regras de negócio, transação por requisição |
| Motor de match | `matching.py` | pontua pares de demandas, gera motivos, caminho jurídico e alertas |
| Autenticação | `auth.py` | PBKDF2-SHA256 (200 000 iterações), token Bearer, validade 12 h |
| Persistência | `db.py` | SQLite ou PostgreSQL (escolhido pelo endereço do banco) |
| Seed | `seed.py` | 5 órgãos fictícios e suas demandas |

## Fluxos [C]
1. **Login:** `POST /api/auth/login` → token → front guarda em `sessionStorage`.
2. **Demanda:** `POST /api/demandas` (ou importação CSV) → `gerar_matches` recalcula as sugestões do órgão.
3. **Match:** `GET /api/matches?pendentes=1` (feed) → `POST /api/matches/{id}/decisao`.
4. **Comitê:** quando as duas decisões são "conectar", cria `comites` + `tarefas`; `POST /api/comites/{id}/mensagens`; o front consulta o comitê a cada 5 s.
5. **Sem API:** `GM.api` desvia para `Demo.chamar` (simulação local).

## Camadas de proteção observadas [C]
- Cada requisição: nova conexão, `commit` no sucesso e `rollback` em erro.
- Corpo limitado a 2 MB; erros em JSON; exceções inesperadas viram 500 genérico (stack trace só no log do servidor).
- Valor sigiloso ocultado ao outro órgão; órgão só vê matches e comitês de que participa.

## Dependências
- Padrão da biblioteca Python: `http.server`, `sqlite3`, `hashlib`, `hmac`, `secrets`, `csv`, `json`, `re`, `unicodedata`, `math`, `argparse`.
- Externa (opcional): `psycopg[binary]` para PostgreSQL.
- Front-end: nenhuma biblioteca externa [C]; fontes/ícones locais.

## Integrações e serviços externos
Nenhum em uso [C]. Hospedagem **prevista** (Render, `render.yaml`): [N].
