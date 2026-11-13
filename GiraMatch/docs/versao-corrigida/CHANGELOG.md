# CHANGELOG — v1-corrigida (a partir de v0-auditada `27d941d`)

## Corrigido
- **F-001** `giramatch/api.py`: `conectar()` agora fica dentro de `try`. Se o banco não abre, a API responde **503** com mensagem genérica e só registra o **tipo** do erro (não a mensagem, que pode conter endereço/credenciais).
- **F-003** `giramatch/auth.py`, `api.py`, `config.py`: limite de tentativas de login. 8 falhas (mesmo IP + e-mail) em 5 min → **429**, mesmo com a senha certa; limite extra de 30 por IP; login válido zera o contador do par. Configurável por `GIRAMATCH_LOGIN_MAX_FALHAS`, `GIRAMATCH_LOGIN_MAX_FALHAS_IP`, `GIRAMATCH_LOGIN_JANELA_S`.
- **F-006** `giramatch/api.py`: o log do servidor passou a registrar só `MÉTODO /caminho -> status`, sem IP e sem parâmetros de URL (verificado em execução).
- **F-004 (parcial)** `giramatch/__main__.py`: aviso na subida quando o banco é PostgreSQL e `GIRAMATCH_CORS=*`.
- **F-009** `DOCUMENTACAO.md`: banco SQLite **ou** PostgreSQL, modo demonstração e link para a seção de publicação.

## Testes
- `tests/test_auditoria.py`: teste de banco indisponível deixou de ser `xfail` e passou a verificar 503 genérico; teste "sem limite de login" substituído por 2 testes de bloqueio.
- `tests/conftest.py` (novo): zera o contador de login antes de cada teste.
- Resultado: **28 passed** (antes: 26 passed + 1 xfailed).

## Artefatos
- README do backend (segurança do login, variáveis), `.env.exemplo`, as-built (`KNOWN_ISSUES`, `SETUP`, `TEST_PLAN`), `TESTS.md`, `HARNESS.md`, PNG da arquitetura e apresentação (contagem de testes e menção ao 429/503).

## Não alterado
Front-end (`index.html`, `app.js`, páginas), `render.yaml`, esquema do banco, regras do match. Nenhum teste foi desativado e nenhum requisito foi alterado.

## v1.1-login (depois do congelamento `v1-corrigida`, a pedido da equipe: "o login tem que funcionar")
- `app.js`: a chamada de login tem limite de 10 s; sem resposta, é tratada como "servidor indisponível".
- `index.html`: com o servidor fora do ar ou sem resposta, as contas de demonstração entram em **modo demonstração (simulado, com etiqueta visível)** em qualquer endereço, não só em `localhost`. Senha errada com o servidor no ar continua dando "E-mail ou senha incorretos." (não cai na demonstração).
- Teste: script Node simulando servidor fora do ar, sem resposta, normal e senha errada (4 cenários OK). **Não testado em navegador.**
- Efeito: o login não depende mais do Render estar no ar, mas, nesse caso, **não há conversa entre órgãos** (modo demonstração).

## v1.1b-login (a pedido: "volte a ideia de antes, em que eu conseguia logar")
- `app.js`: `API_PRODUCAO` voltou a ser vazio. O site publicado não depende de servidor: as contas de demonstração entram direto (modo demonstração, dados fictícios).
- `app.js`: no login, resposta 404/502/503/504 (endereço de API inexistente ou serviço acordando) também conta como "sem servidor" e cai na demonstração. Antes, um 404 de um endereço que não existe mostrava só "Erro 404" e bloqueava o login.
- Testado por script Node (publicado → API vazia; localhost → API local; 404/502/503/504 → demonstração; 401 → erro de senha; 200 → login normal). **Não testado em navegador.**
- Para usar a API real depois, basta colocar a URL em `API_PRODUCAO`.

## v1.1c-demandas (a pedido: "quando ela criar uma nova demanda eu quero que apareça aqui")
- A demanda cadastrada já aparecia em "Minhas demandas" (API e modo demonstração), mas no **modo demonstração** cada novo login apagava os dados e recriava os originais. `app.js`: `Demo.iniciar()` agora **mantém** o que já foi cadastrado; novo `Demo.reiniciar()` volta aos dados originais.
- `index.html`: link "Restaurar os dados originais da demonstração" (com confirmação).
- Testes: script Node (criar → aparece → sair e entrar → continua → restaurar → some) e `test_nova_demanda_aparece_em_minhas_demandas` (API). **29 passed.** Não testado em navegador.
- Limite: no modo demonstração os dados ficam só no navegador (limpar dados do site apaga).

## v1.2-painel (requisitos RF07 a RF12 do dashboard)
| RF | Antes | Agora |
|---|---|---|
| RF07 contagens | demandas, matches novos, convites, comitês | idem, com rótulos "Demandas ativas" e "Cooperações (comitês)" |
| RF08 notificações | só alerta de convite recebido (balão) | + cartão **Notificações** (convites recebidos e novos matches) com contador e "marcar novos matches como lidos" |
| RF09 demandas recentes | **não existia** (a página buscava e não mostrava) | cartão **Demandas mais recentes** (5, mais nova primeiro) |
| RF10 acesso rápido ao cadastro | botão "+ Nova demanda" | mantido |
| RF11 maior compatibilidade | top 3 por score | + selo "★ Maior compatibilidade: X%" no primeiro |
| RF12 filtros | **não existia** | filtros **ano, trimestre e categoria** (valem para números, matches, demandas e notificações; ficam salvos no navegador) |
- Arquivo: `dashboard.html`. Teste: script Node em modo demonstração (todos os RF) + `test_painel_campos_usados_pela_tela` (API). **30 passed.** **Não testado em navegador.**
- Interpretações minhas (confirmar): "demandas ativas" = todas as cadastradas (não há status de arquivada); "período" = ano e trimestre do **mês previsto no PCA**; "categoria" = material, serviço, capacitação ou outro; "novo match" = sugestão ainda sem decisão e não marcada como lida.
- Os cartões "Resultado do seu órgão" e "Rede GiraMatch" continuam com os totais (não filtrados).
