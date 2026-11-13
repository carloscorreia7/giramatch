# GiraMatch — Backend (API + banco de dados)

Backend do **GiraMatch**, solução de cooperação interinstitucional que usa o conceito de *match*
para conectar órgãos públicos com demandas semelhantes (itens do PCA, capacitações etc.).

- **Dependências:** Python 3.10+ (`http.server`). Só o modo PostgreSQL precisa de `psycopg` (`requirements.txt`).
- **Banco:** **PostgreSQL** em produção (variável `DATABASE_URL`); SQLite (`giramatch.db`) para desenvolvimento e testes.
- **API REST em JSON**, com login por token e CORS liberado para o front-end.
- **Motor de match explicável:** cada sugestão traz a nota de cada critério, os motivos,
  o caminho jurídico sugerido e os alertas.

> ⚠️ Protótipo para a maratona. Os **dados de demonstração são fictícios** (quantidades, valores,
> meses e códigos de catálogo inventados) e os **parâmetros de economia são ilustrativos** —
> calibrar com dados reais antes de qualquer uso. Fundamentos jurídicos devem ser validados
> pela assessoria jurídica.

## Publicar na internet (sem terminal)

O arquivo `render.yaml`, na raiz do repositório, cria a API e um banco PostgreSQL gerenciado no
[Render](https://render.com):

1. Suba o projeto para o GitHub.
2. No Render: **New → Blueprint** e escolha o repositório. Ele cria `giramatch-api` e `giramatch-db`.
3. A API cria as tabelas sozinha e, com `GIRAMATCH_DEMO_SE_VAZIO=1`, carrega os dados fictícios na primeira subida.
4. Copie a URL da API (ex.: `https://giramatch-api.onrender.com`) para `API_PRODUCAO` no início de `app.js` e publique o front-end (GitHub Pages, Netlify, Vercel...).
5. Em `GIRAMATCH_CORS`, troque `*` pelo endereço do site publicado.

Para criar logins sem terminal, defina no painel do Render `GIRAMATCH_USUARIOS=TJPB|Nome|email@tjpb.jus.br|SenhaForte123` (vários separados por `;`; o órgão precisa existir). Eles são criados/atualizados a cada subida da API.

Para dados reais: ponha `GIRAMATCH_DEMO_SE_VAZIO=0` e crie os usuários pelo **Shell** do Render
(`python -m giramatch usuario ...`). Outras hospedagens servem, desde que definam `DATABASE_URL` e `PORT`.
No plano gratuito do Render a API "dorme" após alguns minutos sem uso (a primeira chamada demora) e o banco gratuito expira; para uso contínuo, use plano pago.

Para testar no PostgreSQL: `TEST_DATABASE_URL=postgres://... python -m pytest` (**apaga** as tabelas desse banco).

## Como rodar localmente

```bash
python -m giramatch demo      # cria giramatch.db com 5 órgãos e 14 demandas fictícias
python -m giramatch servir    # API em http://127.0.0.1:8000
python -m pytest -q           # testes (precisa do pytest)
```

Logins de demonstração (senha `demo123`):

| Órgão | E-mail |
|---|---|
| TRE-PB | `gestor@trepb.giramatch.demo` |
| TRT 13 | `gestor@trt13.giramatch.demo` |
| JFPB | `gestor@jfpb.giramatch.demo` |
| TJPB | `gestor@tjpb.giramatch.demo` |
| TRE-RN | `gestor@trern.giramatch.demo` |

Variáveis: `GIRAMATCH_LOGIN_MAX_FALHAS`, `GIRAMATCH_LOGIN_MAX_FALHAS_IP`, `GIRAMATCH_LOGIN_JANELA_S` (limite de tentativas de login), `DATABASE_URL`, `PORT`, `GIRAMATCH_DB`, `GIRAMATCH_HOST`, `GIRAMATCH_PORT`, `GIRAMATCH_CORS`, `GIRAMATCH_DEMO_SE_VAZIO` (veja `.env.exemplo`).

## Estrutura

```
giramatch/
  schema.sql    tabelas (SQLite)
  schema_pg.sql tabelas (PostgreSQL)
  db.py         conexão: SQLite ou PostgreSQL
  config.py     pesos do match, limiar, parâmetros de economia
  matching.py   motor de match (regras explicáveis)
  api.py        rotas da API e servidor HTTP
  auth.py       senhas (PBKDF2) e sessões
  seed.py       dados de demonstração
tests/          testes do motor e da API
exemplos/       CSV de exemplo para importar um PCA
```

## Banco de dados

| Tabela | Para quê |
|---|---|
| `orgaos` | Instituições da rede (sigla, ramo, **esfera** federal/estadual, UF, município, se é cooperada) |
| `usuarios`, `sessoes` | Acesso dos gestores |
| `demandas` | Itens do PCA, capacitações e outras necessidades (código CATMAT/CATSER, quantidade, unidade, valor, **valor sigiloso**, mês previsto, local, fim do contrato atual, critérios sustentáveis) |
| `matches` | Sugestões entre duas demandas: score, notas, motivos, caminho jurídico, alertas, economia |
| `decisoes` | "Conectar" ou "Agora não" de cada órgão |
| `comites` | Comitê de cooperação criado quando os dois lados conectam |
| `tarefas` | Cronograma do comitê (especificação → ETP/TR → IRP → licitação → ata) |
| `mensagens` | Conversa entre as equipes no comitê |

## Como o match funciona

Para cada par de demandas de **órgãos diferentes**, do **mesmo ano** e da **mesma natureza**:

| Critério | Peso | Como é medido |
|---|---|---|
| Similaridade | 45% | Mesmo código de catálogo = 100%; senão, termos em comum na descrição |
| Tempo | 25% | Diferença entre os meses previstos no PCA (zera em 6 meses) |
| Território | 15% | Mesmo município / mesmo estado (pesa mais para serviços) |
| Sustentabilidade | 15% | Critérios sustentáveis em comum |
| Bônus | +5 | Serviços cujos contratos atuais terminam com até 90 dias de diferença |

Sugestões com score **≥ 60** viram match. Tudo isso fica em `config.py`.

**Caminho jurídico sugerido**
- Contratações: **IRP** (Lei 14.133/2021, art. 86), com um gerenciador e participantes.
- Se um órgão é **federal** e o outro **estadual**, o gerenciador sugerido é sempre o **federal**,
  porque órgão federal não pode aderir a ata de órgão estadual/distrital/municipal (art. 86, §8º).
  A sugestão vem com alerta para confirmar a participação com a assessoria jurídica.
- Entre órgãos da mesma esfera, gerencia quem tem a compra prevista primeiro.
- Capacitações: **capacitação compartilhada** via acordo de cooperação técnica.

**Alertas automáticos**
- `interfederativo` — regra do art. 86, §8º.
- `me_epp` — os valores, somados, passam de R$ 80 mil e podem afastar a exclusividade para ME/EPP
  (LC 123/2006, art. 48, I): avaliar itens separados ou cota reservada.
- `prazo` — previsões a mais de 3 meses de distância.
- `unidades` — unidades de medida diferentes.

**Segurança do login**
- Depois de 8 senhas erradas (mesmo IP e e-mail) em 5 minutos, o login responde **429**; também há um limite por IP (30). Os contadores ficam na memória do processo (reiniciar zera; com vários processos, cada um conta separado).
- Se o banco estiver indisponível, a API responde **503** com mensagem genérica.
- O log do servidor não registra IP nem parâmetros de URL.

**Privacidade e sigilo**
- O valor de uma demanda marcada como `valor_sigiloso` (orçamento sigiloso, art. 24) **só aparece
  para o próprio órgão**; o outro lado vê `null` e a economia em reais não é calculada.
- Um órgão só vê matches dos quais participa.
- Quando um órgão clica em **Conectar**, o outro é avisado (`pedido_recebido: true` no match) e vê um alerta
  até responder. **Recusas nunca são reveladas**: se o outro lado disser "Agora não", ninguém é avisado.

## Endpoints

Todas as rotas, exceto `health` e `login`, exigem `Authorization: Bearer <token>`.

| Método | Rota | O que faz |
|---|---|---|
| GET | `/api/health` | Status da API |
| POST | `/api/auth/login` | `{email, senha}` → `{token, usuario, orgao}` |
| POST | `/api/auth/logout` | Encerra a sessão |
| GET | `/api/me` | Usuário e órgão logados |
| GET | `/api/orgaos` | Órgãos da rede |
| GET | `/api/demandas?ano=&natureza=` | Demandas do meu órgão |
| POST | `/api/demandas` | Cria demanda (e recalcula os matches) |
| GET/PUT/DELETE | `/api/demandas/{id}` | Consulta, edita, exclui (não exclui se já há comitê) |
| POST | `/api/demandas/importar` | Importa PCA em CSV (corpo = texto do CSV) |
| GET | `/api/matches?pendentes=1` | **Feed** de sugestões ainda não avaliadas, por score |
| GET | `/api/matches?status=conectado` | Filtra por status (`sugerido`, `conectado`, `recusado`) |
| GET | `/api/matches/{id}` | Detalhe do match |
| POST | `/api/matches/{id}/decisao` | `{decisao: "conectar" \| "recusar"}` → `{deu_match, match}` |
| POST | `/api/matches/gerar` | Recalcula as sugestões do meu órgão |
| GET | `/api/comites` | Meus comitês de cooperação |
| GET | `/api/comites/{id}` | Comitê com tarefas, mensagens e match |
| POST | `/api/comites/{id}/mensagens` | `{texto}` |
| PATCH | `/api/comites/{id}/tarefas/{tarefa_id}` | `{concluida, prazo}` |
| GET | `/api/painel` | Indicadores da rede e do meu órgão |

### Exemplo

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"gestor@trepb.giramatch.demo","senha":"demo123"}' | python -c "import sys,json;print(json.load(sys.stdin)['token'])")

curl -s "localhost:8000/api/matches?pendentes=1" -H "Authorization: Bearer $TOKEN"
curl -s -X POST localhost:8000/api/matches/1/decisao -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"decisao":"conectar"}'
curl -s -X POST localhost:8000/api/demandas/importar -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: text/csv' --data-binary @exemplos/pca_exemplo.csv
```

Resposta de um match (resumida):

```json
{
  "id": 1, "score": 96, "status": "sugerido",
  "motivos": [
    "Mesmo item no catálogo (CATMAT-DEMO-0001)",
    "Previsões no PCA com 1 mês de diferença",
    "Os dois em João Pessoa/PB",
    "Critérios sustentáveis em comum: eficiência energética, logística reversa, restrição de substâncias perigosas"
  ],
  "caminho": { "modelo": "irp", "gerenciador": "TRE-PB", "participantes": ["TRT 13"], "fundamentos": ["..."] },
  "alertas": [],
  "volume_total": 300, "economia_pct": 0.119, "economia_valor": 226100.0
}
```

### Importação de CSV

Separador `;` ou `,`, primeira linha com os nomes das colunas (veja `exemplos/pca_exemplo.csv`).
Obrigatórias: `ano`, `descricao`, `mes_previsto`. Critérios sustentáveis separados por `|`.
Linhas com erro são informadas em `erros` e as demais são importadas.

## Próximos passos

1. **Integração com o PNCP** — puxar os PCAs publicados em vez de importar CSV
   (conferir antes o formato e a cobertura da API de consultas do PNCP para os tribunais).
2. **IA semântica** — trocar a similaridade por termos (`matching.similaridade`) por embeddings
   de um modelo de linguagem, para achar itens equivalentes com descrições diferentes.
3. **Matches com 3 ou mais órgãos** — hoje o match é entre pares; agrupar os pares do mesmo item
   num único comitê.
4. **Produção** — login institucional (SSO), HTTPS, perfis de acesso, logs de auditoria,
   e governança de IA conforme a Res. CNJ 615/2025.
