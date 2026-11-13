# GiraMatch — Documentação das funcionalidades

> Plataforma de relacionamento interinstitucional que usa o conceito de **match** para identificar interesses e necessidades comuns entre órgãos públicos, transformando planejamentos individuais em oportunidades de cooperação, compartilhamento de recursos e iniciativas conjuntas.

**Estado atual:** protótipo funcional (front-end em HTML/CSS/JS + API em Python com SQLite ou PostgreSQL). Os dados de demonstração são **fictícios**; os percentuais de economia são **ilustrativos**; os fundamentos jurídicos devem ser validados pela assessoria jurídica de cada órgão.

---

## 1. Visão geral

O fluxo central do sistema:

1. O órgão **cadastra demandas** (itens do PCA, serviços, capacitações).
2. O motor **sugere matches** com demandas compatíveis de outros órgãos, mostrando o percentual de compatibilidade e *por quê*.
3. Cada órgão decide **Conectar** ou **Agora não**.
4. Quando **os dois conectam**, nasce um **comitê de cooperação** com cronograma, conversa e acompanhamento.

> Como num aplicativo de match, a decisão do outro órgão **só é revelada quando os dois conectam**.

A IA/regras apenas **apoiam** a decisão; quem decide é sempre o gestor (aviso exibido nas telas de match).

---

## 2. Arquitetura

| Camada | Tecnologia | Onde |
|---|---|---|
| Front-end | HTML + CSS + JavaScript puro (sem dependências) | pasta `GiraMatch/` |
| API | Python 3.10+ (`http.server`), JSON/REST, login por token | `giramatch-backend/giramatch-backend/giramatch/` |
| Banco | SQLite (arquivo `giramatch.db`, desenvolvimento) ou PostgreSQL (`DATABASE_URL`, hospedagem) | SQLite: criado por `python -m giramatch demo`; PostgreSQL: tabelas criadas pela API ao subir |

O navegador **nunca** acessa o banco: ele chama a API (`http://127.0.0.1:8000/api/...`), e a API lê/grava no banco. Sem API (modo demonstração) o site usa dados fictícios guardados só no navegador. Para publicar, veja `giramatch-backend/giramatch-backend/README.md` (seção "Publicar na internet").

### Arquivos do front-end

| Arquivo | Função |
|---|---|
| `index.html` | Tela 1 — Login |
| `dashboard.html` | Tela 2 — Dashboard |
| `nova-demanda.html` | Tela 3 — Nova demanda (e edição) |
| `minhas-demandas.html` | Tela 4 — Minhas demandas |
| `matches.html` | Tela 5 — Matches |
| `match-detalhe.html` | Tela 6 — Detalhes do match |
| `convites.html` | Tela 7 — Convites |
| `comite.html` | Tela 8 — Comitê |
| `acompanhamento.html` | Tela 9 — Acompanhamento |
| `app.js` | Núcleo: chamadas à API, sessão, menu, componentes, modo demonstração |
| `stylo.css` | Estilos compartilhados |
| `logo-giramatch.png` / `logo-giramatch-claro.png` | Logo (original e versão com "Gira" branco para o menu escuro) |

---

## 3. Como executar

```powershell
cd "C:\Users\arthu\OneDrive\Área de Trabalho\GiraMatch\giramatch-backend\giramatch-backend"
python -m giramatch demo      # cria giramatch.db com 5 órgãos e demandas fictícias
python -m giramatch servir    # API em http://127.0.0.1:8000 (deixe o terminal aberto)
```

Depois abra `frontend/index.html`. Se o navegador acusar erro de CORS ao abrir o arquivo direto, sirva a pasta: `cd frontend && python -m http.server 5500` e acesse `http://localhost:5500`.

### Comandos da linha de comando

| Comando | O que faz |
|---|---|
| `python -m giramatch iniciar` | Cria as tabelas (banco vazio) |
| `python -m giramatch demo` | **Apaga** e recria o banco com dados de demonstração |
| `python -m giramatch servir` | Sobe a API (`--host`, `--porta`) |
| `python -m giramatch usuario --orgao TJPB --nome "..." --email ... --senha "..."` | Cria usuário de um órgão já cadastrado (ou atualiza a senha se o e-mail existir; senha mínima de 8 caracteres) |

Variáveis opcionais: `GIRAMATCH_DB`, `GIRAMATCH_HOST`, `GIRAMATCH_PORT`, `GIRAMATCH_CORS`.

### Contas de demonstração (senha `demo123`)

| Órgão | E-mail |
|---|---|
| TRE-PB | `gestor@trepb.giramatch.demo` |
| TRT 13 | `gestor@trt13.giramatch.demo` |
| JFPB | `gestor@jfpb.giramatch.demo` |
| TJPB | `gestor@tjpb.giramatch.demo` |
| TRE-RN | `gestor@trern.giramatch.demo` |

### Modo demonstração (sem servidor)

Se a API estiver fora do ar, o login oferece **"Entrar em modo demonstração (TRE-PB)"**. Os dados são fictícios e ficam só no navegador (`localStorage`). Limitações desse modo: importação de CSV indisponível e os matches **não são recalculados** ao cadastrar/editar demandas. Uma etiqueta "Modo demonstração" aparece no topo.

---

## 4. Funcionalidades por tela

### Estrutura comum (telas 2 a 9)

- **Menu lateral** (azul-escuro) com as seções *Visão geral* (Painel, Minhas demandas, Nova demanda) e *Cooperação* (Matches, Convites, Comitês, Acompanhamento).
- **Selo de convites pendentes** no item "Convites" (número de matches ainda não respondidos).
- Rodapé com **sigla do órgão**, nome do usuário e botão **Sair**.
- Proteção de acesso: sem login, qualquer tela redireciona para o `index.html`. Se a sessão expirar (12 h), o usuário volta ao login com aviso.
- Layout responsivo: no celular o menu vira gaveta (botão ☰).

### 1. Login — `index.html`
- Autenticação por e-mail e senha (`POST /api/auth/login`); a instituição do usuário é identificada pelo cadastro.
- **Indicador de status da API** (verde conectada / vermelho indisponível).
- Atalhos das **5 contas de demonstração** (preenchem e-mail e senha).
- Campo **Endereço da API** (padrão `http://127.0.0.1:8000`, ajustável e salvo no navegador).
- Botão de **modo demonstração** quando a API está indisponível.
- Mensagens de erro claras (senha incorreta, API fora do ar, sessão expirada).

### 2. Dashboard — `dashboard.html`
- Indicadores do órgão: **demandas cadastradas**, **matches novos para avaliar**, **convites aguardando resposta**, **comitês**.
- **Melhores oportunidades:** os 3 matches de maior compatibilidade ainda não respondidos, com botões *Conectar* / *Agora não*.
- **Resultado do órgão:** economia estimada dos matches conectados e processos (licitações) evitados.
- **Rede GiraMatch:** órgãos cooperados, demandas na rede, matches conectados, economia estimada.
- **Próximos passos:** tarefas pendentes mais próximas dos comitês do órgão.
- Aviso de que as sugestões são automáticas e a decisão é dos gestores.

### 3. Nova demanda — `nova-demanda.html`
Formulário **dinâmico por categoria** (escolhida no início):

| Categoria | Natureza / tipo | Campos específicos |
|---|---|---|
| Material / bem | contratação / material | código CATMAT, categoria, quantidade, unidade, valor, sigilo, critérios sustentáveis |
| Serviço | contratação / serviço | código CATSER, quantidade, unidade, valor, sigilo, **fim do contrato atual**, município/UF de execução, critérios sustentáveis |
| Capacitação | capacitação | tema, nº de vagas (unidade fixa "vaga"), valor, município/UF |
| Outra necessidade | outra / outro | descrição, categoria, quantidade, unidade, valor |

- Campos comuns: **ano do PCA**, **mês previsto**, descrição.
- **Orçamento sigiloso** (Lei 14.133, art. 24): o valor só é visível para o próprio órgão.
- **Critérios sustentáveis** como etiquetas, com sugestões clicáveis.
- Ao cadastrar, a API recalcula os matches e a tela informa quantas novas sugestões surgiram.
- **Importar PCA em CSV** (separador `;` ou `,`; obrigatórias `ano`, `descricao`, `mes_previsto`; critérios separados por `|`). Linhas com erro são listadas; as demais são importadas. Exemplo em `exemplos/pca_exemplo.csv`.
- A mesma tela serve para **editar** (`nova-demanda.html?id=N`).

### 4. Minhas demandas — `minhas-demandas.html`
- Lista com descrição, código de catálogo, categoria, previsão (mês/ano), quantidade, valor (ou 🔒 sigiloso) e **situação** (*Sem match*, *N matches*, *Em comitê*).
- **Filtros:** busca por texto, natureza e ano.
- **Acompanhar:** expande os matches ligados à demanda, com compatibilidade, órgão parceiro e estado, com link para o detalhe.
- **Editar** (abre o formulário preenchido) e **Excluir** (com confirmação). Demandas já em comitê **não podem ser excluídas** (a API recusa com explicação).

### 5. Matches — `matches.html`
- Cartões com **anel de compatibilidade (%)**, demanda própria, órgão parceiro, quantidade/previsão da outra demanda, os principais motivos, economia estimada e estado.
- **Abas:** Todos · Para responder · Aguardando · Conectados · Dispensados (com contadores).
- **Filtros:** natureza e **compatibilidade mínima** (60–100%).
- **Ordenação:** compatibilidade, economia estimada ou prazo no PCA.
- Ações rápidas **Conectar** / **Agora não** direto no cartão. Ao formar o match aparece o aviso **"É um match!"** com atalho para o comitê.

### 6. Detalhes do match — `match-detalhe.html`
- **Cabeçalho:** compatibilidade em destaque, estado, partes envolvidas e ações.
- **Comparação lado a lado** das duas demandas (órgão, esfera, descrição, natureza, código, quantidade, previsão, valor, local, fim do contrato, critérios sustentáveis); campos coincidentes ficam destacados em verde. Valores sigilosos do outro órgão aparecem como "🔒 valor sigiloso".
- **Por que é compatível:** lista de motivos em linguagem simples e **nota por critério** com barras (Similaridade 45%, Proximidade no PCA 25%, Território 15%, Critérios sustentáveis 15%).
- **Caminho sugerido:** modelo (IRP ou capacitação compartilhada), órgão gerenciador, participantes e fundamentos legais.
- **Pontos de atenção** (alertas jurídicos/operacionais — ver seção 5).
- **Ganho estimado:** economia em R$ e %, ou só o ganho de escala quando há valor sigiloso.
- Aviso de que a decisão é do gestor.

### 7. Convites — `convites.html`
Acompanhamento das manifestações de interesse, em abas:

| Aba | Significado |
|---|---|
| Para responder | Sugestões ainda sem decisão do órgão (**Conectar** = aceitar; **Agora não** = recusar) |
| Aguardando resposta | O órgão já conectou; falta o outro lado (a resposta só é revelada quando os dois conectam) |
| Aceitos (comitês) | Os dois conectaram; comitê criado |
| Recusados | Sugestões dispensadas |

### 8. Comitê — `comite.html`
- **Lista de comitês** do órgão e seleção do ativo (`?id=N`).
- **Órgãos participantes**, com marcação de **gerenciador** e participante.
- **Representantes do comitê:** indicação de nome, cargo/unidade, órgão, papel (titular, suplente, assessoria jurídica, área técnica) e e-mail; remoção. ⚠️ *Salvo apenas no navegador* (ver seção 8).
- **Conversa do comitê** entre as equipes (mensagens de até 4.000 caracteres, gravadas no banco).
- Painel lateral com **andamento** (tarefas concluídas), **caminho jurídico** e atalho para o match.

### 9. Acompanhamento — `acompanhamento.html`
- **Barra de progresso** da iniciativa (etapas concluídas).
- **Cronograma:** tarefas geradas automaticamente (ver abaixo); marcar como concluída e **alterar o prazo** (gravado no banco); sinalização de **atrasada**; responsável por etapa.
- **Registro de decisões:** texto, data e autor. ⚠️ *Salvo apenas no navegador.*
- **Documentos:** nome, tipo (ETP, termo de referência, IRP, edital, ata de registro de preços, acordo de cooperação, parecer jurídico, outro) e link opcional (SEI, PNCP, nuvem; só `http/https`). ⚠️ *Registro de metadados, sem envio de arquivo; salvo apenas no navegador.*
- **Evolução da iniciativa:** linha do tempo reunindo criação do comitê, decisões, documentos e mensagens.
- Seletor para trocar de iniciativa quando há mais de um comitê.

**Cronograma gerado ao formar o match**
- *Contratações (IRP):* alinhar especificação e critérios sustentáveis → ETP e termo de referência conjuntos → publicar a IRP (mín. 8 dias úteis) → realizar a licitação → assinar a ata e emitir o contrato de cada órgão.
- *Capacitações:* definir conteúdo/formato/vagas → formalizar no acordo de cooperação técnica → realizar a capacitação compartilhada.
- Os prazos são distribuídos a partir do mês previsto no PCA.

---

## 5. Motor de match (regras)

Um match só é formado entre demandas de **órgãos diferentes**, do **mesmo ano** e da **mesma natureza**.

| Critério | Peso | Como é medido |
|---|---|---|
| Similaridade | 45% | Mesmo código de catálogo = 100%; senão, termos em comum na descrição (mínimo 40%) |
| Tempo | 25% | Diferença entre os meses previstos no PCA (zera em 6 meses) |
| Território | 15% | Mesmo município / mesmo estado (pesa mais para serviços) |
| Sustentabilidade | 15% | Critérios sustentáveis em comum |
| Bônus | +5 | Serviços com contratos atuais terminando com até 90 dias de diferença |

Sugestões com **score ≥ 60** viram match. Os pesos ficam em `giramatch/config.py`.

**Caminho jurídico sugerido**
- *Contratações:* **IRP** (Lei 14.133/2021, art. 86), com um órgão gerenciador e participantes.
- *Federal × estadual:* o gerenciador sugerido é sempre o **federal** (órgão federal não pode aderir a ata de órgão estadual/distrital/municipal — art. 86, §8º).
- *Mesma esfera:* gerencia quem tem a compra prevista primeiro (desempate pela maior quantidade).
- *Capacitações:* **capacitação compartilhada** por acordo de cooperação técnica.

**Alertas automáticos**

| Alerta | Quando aparece |
|---|---|
| `interfederativo` | Um órgão federal e outro não federal (art. 86, §8º) — confirmar participação com a assessoria jurídica |
| `me_epp` | Valores somados passam de R$ 80 mil e podem afastar a exclusividade ME/EPP (LC 123/2006, art. 48, I) |
| `prazo` | Previsões a mais de 3 meses de distância |
| `unidades` | Unidades de medida diferentes (a similaridade perde 20 pontos) |

**Economia estimada (ilustrativa):** `6% + 8% × log2(volume total ÷ maior quantidade)`, limitada a 20%. Só é calculada em reais se **nenhum** dos valores for sigiloso e as unidades forem iguais.

---

## 6. Privacidade e segurança

- Cada órgão **só vê matches e comitês dos quais participa**; acessar o de terceiros retorna "não encontrado".
- **Valor sigiloso** nunca é enviado ao outro órgão (`null`); a economia em R$ não é calculada.
- A decisão do outro órgão só aparece quando os dois conectam.
- Senhas guardadas com **PBKDF2** (hash + sal); sessão por token com validade de 12 h; o front guarda a sessão em `sessionStorage`.
- Todo texto vindo da API é escapado antes de ser exibido no navegador.
- O CORS da API está aberto (`*`) **apenas para o protótipo**.

---

## 7. API (resumo das rotas)

Todas, exceto `health` e `login`, exigem `Authorization: Bearer <token>`.

| Método | Rota | Função |
|---|---|---|
| GET | `/api/health` | Status da API |
| POST | `/api/auth/login` | `{email, senha}` → `{token, usuario, orgao}` |
| POST | `/api/auth/logout` | Encerra a sessão |
| GET | `/api/me` · `/api/orgaos` | Usuário logado · órgãos da rede |
| GET/POST | `/api/demandas` | Lista (`?ano=&natureza=`) · cria (e recalcula matches) |
| GET/PUT/DELETE | `/api/demandas/{id}` | Consulta · edita · exclui (409 se houver comitê) |
| POST | `/api/demandas/importar` | Importa CSV (corpo = texto do CSV) |
| GET | `/api/matches` | Lista (`?pendentes=1`, `?status=conectado`) |
| GET | `/api/matches/{id}` | Detalhe do match |
| POST | `/api/matches/{id}/decisao` | `{decisao: "conectar" \| "recusar"}` → `{deu_match, match}` |
| POST | `/api/matches/gerar` | Recalcula as sugestões do órgão |
| GET | `/api/comites` · `/api/comites/{id}` | Comitês · comitê com tarefas, mensagens e match |
| POST | `/api/comites/{id}/mensagens` | `{texto}` |
| PATCH | `/api/comites/{id}/tarefas/{tarefa_id}` | `{concluida, prazo}` |
| GET | `/api/painel` | Indicadores da rede e do órgão |

---

## 8. Banco de dados

| Tabela | Conteúdo |
|---|---|
| `orgaos` | Sigla, nome, ramo, esfera (federal/estadual/distrital/municipal), UF, município, se é cooperado |
| `usuarios`, `sessoes` | Gestores e tokens de acesso |
| `demandas` | Itens do PCA, capacitações e outras necessidades |
| `matches` | Sugestões entre duas demandas: score, notas, motivos, caminho, alertas, economia, status |
| `decisoes` | "Conectar" ou "Agora não" de cada órgão |
| `comites` | Comitê criado quando os dois lados conectam |
| `tarefas` | Cronograma do comitê |
| `mensagens` | Conversa entre as equipes |

---

## 9. Limitações conhecidas e próximos passos

**O que ainda não está no banco (hoje só no navegador):**
- Indicação de **representantes** do comitê
- Registro de **decisões** do acompanhamento
- Registro de **documentos** (e não há envio de arquivos)

Para serem compartilhados entre os órgãos, precisam de novas tabelas e rotas na API.

**Outras limitações:** o convite "recebido" não existe como entidade própria (as abas de Convites derivam das decisões de cada órgão); o modo demonstração não recalcula matches nem importa CSV; os parâmetros de economia não foram calibrados com dados reais.

**Roteiro sugerido**
1. Persistir representantes, decisões e documentos no backend.
2. Integração com o **PNCP** (puxar PCAs publicados em vez de importar CSV).
3. **IA semântica** para similaridade (embeddings), em vez de comparação por termos.
4. Matches com **3 ou mais órgãos** (um comitê para o mesmo item).
5. **Produção:** PostgreSQL, login institucional (SSO), HTTPS, perfis de acesso, logs de auditoria e governança de IA (Res. CNJ 615/2025).

---

## 10. Base legal citada no sistema

- Lei 14.133/2021, art. 86 (intenção de registro de preços), art. 12, VII (PCA) e art. 24 (orçamento sigiloso)
- Res. TSE 23.702/2022, art. 14 (compras compartilhadas)
- LC 123/2006, art. 48, I (exclusividade ME/EPP até R$ 80 mil)
- Res. CNJ 615/2025 (governança de IA no Judiciário)
