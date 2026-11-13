# AS_BUILT — GiraMatch como foi construído

Legenda: **[C]** CONFIRMADA (código ou execução) · **[I]** INFERIDA · **[D]** DECLARADA (só na documentação) · **[N]** NÃO VERIFICADA.
Esta etapa **não emite parecer de aprovação ou reprovação**.

## Base e integridade
- Repositório Git local; origem remota configurada, **mas nenhum commit foi enviado** ao GitHub nesta sessão [C].
- **Original imutável:** commit `55b52a65e320ba58599dd92d38b895b75da7a9c1` ("GiraMatch: front-end e backend iniciais") [C].
  ZIP gerado com `git archive` desse commit: SHA-256 `541267f86678ad00ffea6dc5c86fa474fcff1acae4b9e039e8279e1dc42fbfd1` [C].
- **Versão analisada (as-built):** commit `09749e74f1901f063743ff05600c77fff673ed95` [C]. Entre os dois houve alterações feitas nesta mesma sessão (PostgreSQL, deploy, login de demo, chat, docs). Ver `CHANGES_FOR_EXECUTION.md`.
- Ambiente: Windows 11, Python 3.13.14, pytest 9.x, Node (só para `node --check`) [C].

## Cobertura da análise (limites)
- **Lidos integralmente:** `db.py`, `config.py`, `__main__.py`, `auth.py`, `index.html` (script), `render.yaml`, testes novos.
- **Lidos em parte / por busca:** `api.py` (trechos e lista de rotas), `matching.py`, `seed.py`, `app.js` (início, sessão, modo demo), `comite.html`, demais páginas HTML (só `grep` de chamadas à API e storage).
- **Não inspecionados linha a linha:** a lógica completa do motor de match e as demais telas. Nada aqui alega inspeção integral.
- **Não executados:** PostgreSQL, deploy, front-end em navegador real, Docker.

## Stack e componentes [C]
- Front-end: HTML + CSS + JavaScript puro, sem build nem dependências (9 páginas, `app.js`, `stylo.css`).
- API: Python 3.10+ com `http.server` (`ThreadingHTTPServer`), JSON/REST, 20 rotas.
- Banco: SQLite (padrão) ou PostgreSQL (se `DATABASE_URL` for `postgres://...`).
- Dependência externa só para PostgreSQL: `psycopg[binary]>=3.2` (`requirements.txt`).
- Testes: pytest (19 testes).

## Pontos de entrada e inicialização [C]
`python -m giramatch {iniciar|demo|usuario|servir}` na pasta `giramatch-backend/giramatch-backend`. Front-end: abrir `index.html`. Detalhes em `SETUP.md`.

## Fluxo principal implementado [C]
Login → cadastrar/importar demanda → matches recalculados → feed de sugestões → "Conectar"/"Agora não" → quando os dois conectam, cria comitê com tarefas (5 para IRP, 3 para capacitação) → mensagens e acompanhamento de tarefas.
Evidência: `test_conexao_dos_dois_lados_cria_comite`, `test_conversa_entre_os_dois_orgaos`, `test_nova_demanda_gera_match`.

## Banco de dados [C]
9 tabelas: `orgaos`, `usuarios`, `sessoes`, `demandas`, `matches`, `decisoes`, `comites`, `tarefas`, `mensagens` (`schema.sql` e `schema_pg.sql`).
No PostgreSQL, a camada `db.py` converte `?` em `%s` e usa `RETURNING id` para `lastrowid` [C, por leitura]; **execução em PostgreSQL: [N]**.

## Dados: reais, fictícios ou simulados
- Dados de `seed.py` (5 órgãos, 14+ demandas): **fictícios** [D no README; C pela leitura do cabeçalho do README e do `seed.py`].
- Modo demonstração do front-end: dados **simulados e estáticos** gravados em `localStorage` (`gm_demo_v3`) [C].
- Não há dados reais conhecidos no repositório [I]; não foi feita varredura de reidentificação.

## IA, modelos e prompts [C]
Não há IA generativa, modelo, prompt nem chamada a LLM. A similaridade usa termos em comum (regras). Busca por `openai|anthropic|gpt|llm|embedding|claude` só encontrou um comentário sobre "embeddings" como **trabalho futuro** em `matching.py`.

## Integrações externas [C]
Nenhuma em execução. PNCP, SSO e IA semântica: **apenas planejadas** [D].

## Variáveis de ambiente [C]
`DATABASE_URL`, `GIRAMATCH_DB`, `GIRAMATCH_HOST`, `GIRAMATCH_PORT`, `PORT`, `GIRAMATCH_CORS`, `GIRAMATCH_DEMO_SE_VAZIO`, `GIRAMATCH_PERMITIR_DEMO`, `GIRAMATCH_USUARIOS`. Ver `.env.exemplo`.

## Possíveis segredos/credenciais (localização redigida) [C]
| Local | Tipo | Observação |
|---|---|---|
| `giramatch/seed.py` (constante `SENHA_DEMO`) | senha de demonstração `***` | fictícia, documentada no README |
| `index.html` (objeto `CONTAS_EXTRAS`, ~linha 88) | e-mail + senha de conta de teste `***` | **visível a qualquer visitante do site** |
| `index.html` (função `contaDemo`) | verificação da senha de demonstração `***` | idem |
Nenhum token, chave de API ou `DATABASE_URL` real foi encontrado no repositório (varredura por padrões `key/secret/token/senha = "..."`) [C]. A varredura é por padrões e **não prova ausência total** [N].

## Demonstração: real, mock ou estática
- Com API: processamento **real** (API + banco) [C, testes em SQLite].
- Sem API (site publicado só com front-end, ou `API_PRODUCAO` vazio): **simulação estática no navegador**, sempre com a visão do TRE-PB, sem comunicação entre órgãos [C].

## Diferenças entre README, código e comportamento
1. `DOCUMENTACAO.md` ainda diz "SQLite" e API em `127.0.0.1:8000` (linhas 5, 30, 32, 58) [D], mas o código agora aceita PostgreSQL e o endereço da API é configurável [C].
2. O README do backend (original) dizia "Sem dependências"; no código atual `psycopg` é necessário **apenas** para PostgreSQL [C]. O README foi atualizado.
3. Em `comite.html`, a indicação de representantes é salva só no navegador (o próprio texto da tela avisa) [C].
4. `API_PRODUCAO` aponta para `https://giramatch-api.onrender.com`, URL **presumida e inexistente até o deploy** [C no código; N quanto à existência].
