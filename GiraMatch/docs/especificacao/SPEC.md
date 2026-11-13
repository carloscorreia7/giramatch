# GiraMatch — Especificação do MVP (rev. 1.0)

> Baseada no protótipo existente. **Edital/critérios da banca não foram fornecidos**: este documento
> não afirma aderência à banca. Prazo não informado: premissa = fluxo demonstrável em até 5 minutos.

## Hierarquia das fontes
1. Edital/desafio e critérios oficiais — **NÃO DISPONÍVEL** (decisão pendente: enviar à equipe).
2. Proposta da equipe — `DOCUMENTACAO.md` e `giramatch-backend/giramatch-backend/README.md`.
3. Demais anexos — nenhum.

## Problema e usuários
Órgãos públicos planejam compras (PCA) e capacitações isoladamente e perdem escala. O GiraMatch sugere
**matches** entre demandas semelhantes de órgãos diferentes e organiza a cooperação.
Usuário: **gestor de contratações/planejamento** de cada órgão (ex.: TRE-PB, TJPB, TRT 13, JFPB, TRE-RN).

## Fluxo ponta a ponta (obrigatório)
Cadastrar demanda → receber match explicado → **Conectar** (os dois lados) → comitê com cronograma e conversa.

## Funcionalidades essenciais (máx. 3)
| ID | Prio | Funcionalidade | Critério de aceite |
|---|---|---|---|
| REQ-001 | P0 | Cadastrar/importar demanda | **Dado** um gestor logado, **quando** cadastra uma demanda válida (ou importa CSV), **então** ela é salva e os matches do órgão são recalculados. |
| REQ-002 | P0 | Match explicável | **Dado** demandas de órgãos diferentes, mesmo ano e natureza, **quando** score ≥ 60, **então** o match mostra score, motivos, caminho jurídico e alertas, e valores sigilosos não aparecem ao outro órgão. |
| REQ-003 | P0 | Conectar e cooperar | **Dado** um match sugerido, **quando** os dois órgãos escolhem Conectar, **então** nasce o comitê com cronograma e conversa compartilhada; se um recusa, ninguém é avisado da recusa. |

## Fora do escopo
Integração real com PNCP; IA semântica (embeddings); matches com 3+ órgãos; login institucional (SSO);
parâmetros de economia calibrados; qualquer uso em produção judicial.

## Arquitetura
- **Front-end:** HTML/CSS/JS puro (`*.html`, `app.js`, `stylo.css`).
- **API:** Python 3.10+ (`http.server`), REST/JSON, login por token Bearer.
- **Banco:** PostgreSQL (produção, via `DATABASE_URL`) ou SQLite (dev/testes).
- **Modo demonstração:** simula a API no navegador, dados só locais (sem compartilhamento entre órgãos).

## Dados
Tabelas: `orgaos`, `usuarios`, `sessoes`, `demandas`, `matches`, `decisoes`, `comites`, `tarefas`, `mensagens`
(ver `schema.sql` e `schema_pg.sql`).

## APIs
Lista completa no README do backend (`/api/auth/login`, `/api/demandas`, `/api/matches`,
`/api/matches/{id}/decisao`, `/api/comites`, `/api/comites/{id}/mensagens`, `/api/painel`).

## Integrações
| Item | Situação |
|---|---|
| API própria + banco | **Real** (código); PostgreSQL **não verificado** (só SQLite testado) |
| Modo demonstração | **Simulado** (dados fictícios no navegador) |
| PNCP, SSO, IA semântica | **Apenas planejado** |

## Premissas e riscos P0
- Os dados são **fictícios**; os percentuais de economia são **ilustrativos**.
- **R1:** deploy em PostgreSQL ainda não executado → pode falhar no primeiro build.
- **R2:** plano gratuito do Render "dorme" → primeira chamada lenta na demo.
- **R3:** o chat entre órgãos só funciona com a API publicada (não no modo demonstração).
- **R4:** a URL da API em `app.js` é uma suposição até o Render gerar a real.
