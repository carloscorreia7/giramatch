# RESIDUAL_RISKS

| Risco | Achado | Impacto | Medida compensatória | Efeito no parecer | Recomendação |
|---|---|---|---|---|---|
| PostgreSQL e deploy nunca executados | F-002 | a demo compartilhada pode falhar no primeiro deploy | rodar a suíte com `TEST_DATABASE_URL`; checar `/api/health` publicado | **impede** declarar ESTADO OK | executar antes de apresentar |
| Front-end sem teste em navegador; escape de HTML presumido | F-007 | falha visual ou XSS não detectados | revisão manual das páginas e teste com dois navegadores | impede ESTADO OK | teste ponta a ponta com capturas |
| Apresentação sem capturas reais, nome da equipe e URL | F-008 | demo menos convincente | preencher e capturar | pendência | antes do evento |
| CORS `*` por padrão | F-004 | qualquer site pode chamar a API | definir `GIRAMATCH_CORS` na hospedagem | ressalva | fazer no deploy |
| Contadores de login em memória | F-003 | reiniciar zera; vários processos contam separado; proxy mascara o IP | aceitável para o protótipo | ressalva | contador no banco se escalar |
| Senhas fictícias em código público | F-005 | credenciais de demo legíveis | dados 100% fictícios | ressalva | nunca reutilizar as senhas |
| Traceback de erros 500 no stderr | F-006 | pode registrar contexto | log da hospedagem restrito | ressalva | revisar logs reais |
| Modo demonstração mostra sempre o TRE-PB | F-010 | confusão com contas de outros órgãos | documentado | ressalva | trocar de órgão só com a API |
| Auditoria e correção feitas pelo mesmo agente | F-011 | viés de confirmação | relatório transparente, testes reproduzíveis | **impede qualquer "certificação"** | revisão cruzada humana |
| Edital não fornecido | — | aderência à banca desconhecida | — | avaliação só técnica | enviar o edital |
| Alteração "Res. CNJ 674/2026" não verificada | — | citação possivelmente imprecisa | MVP sem IA, norma pouco relevante hoje | ressalva | confirmar na fonte oficial |
