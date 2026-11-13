# ROTEIRO DE DEMONSTRAÇÃO — 5 MINUTOS

**Projeto:** GiraMatch
**Versão/commit:** `v1-corrigida` = `d7f7b10`
**Apresentador:** [preencher]

**Antes de começar (fora do tempo):** abra o site 2–3 min antes (a API "dorme" no plano gratuito). Dois navegadores, ou um normal e um anônimo, já logados: **TRE-PB** (`gestor@trepb.giramatch.demo`) e **TRT 13** (`gestor@trt13.giramatch.demo`), senha `demo123`. Dados 100% fictícios. Ensaie uma vez: o roteiro **não foi testado no navegador**.

## 0:00–0:40 — Problema e usuário
- Problema: órgãos públicos planejam compras e capacitações isoladamente e perdem escala, tempo e economia.
- Usuário-alvo: gestor de contratações e planejamento de tribunais e órgãos do sistema de Justiça.
- Impacto observado: **não temos medição real**; a economia exibida é ilustrativa. Não prometer valores.

## 0:40–1:10 — Proposta de valor
- O que o MVP resolve: sugere parcerias entre órgãos com demandas parecidas e organiza a cooperação.
- Diferencial demonstrável: cada match vem **explicado** (score, motivos, caminho jurídico sugerido, alertas).
- Limite de escopo: sem integração com PNCP; regras jurídicas ainda **sem validação por jurista**; o sistema sugere, o gestor decide.

## 1:10–3:40 — Demonstração do fluxo real
1. Abrir/iniciar: site publicado (API no ar). Local: `python -m giramatch demo` e `python -m giramatch servir`, depois `index.html`.
2. Entrada fictícia: demanda **"Notebooks corporativos"** do TRE-PB, que forma par com o TRT 13 (par verificado nos testes; confirme na tela do feed).
3. Ações na tela: TRE-PB abre o feed → abre o match (score, motivos, caminho IRP, alertas) → clica em **Conectar** → no TRT 13 aparece o pedido de conexão → TRT 13 clica em **Aceitar** → abre o comitê com o cronograma → uma mensagem de cada lado.
4. Resultado observado: comitê criado com 5 tarefas; a mensagem de um órgão aparece no outro em até 5 s.
5. Intervenção humana: cada órgão decidiu por conta própria; nada foi conectado automaticamente.

## 3:40–4:20 — Exceção e controle
- Falha controlada: login com senha errada.
- Mensagem e comportamento: "E-mail ou senha incorretos."; depois de 8 erros seguidos o sistema bloqueia por alguns minutos (429).
- Controle de dados/segurança: valor marcado como **sigiloso** não aparece para o outro órgão; **"Agora não" não revela a recusa** a quem fez o pedido.

## 4:20–5:00 — Limitações e fechamento
- Funcionalidades simuladas: o **modo demonstração** (sem servidor) é simulado e rotulado na tela.
- Limitações conhecidas: dados fictícios; economia ilustrativa; sem validação jurídica; PostgreSQL e deploy ainda não verificados.
- Próximo passo realista: validar as regras com jurista; integrar PNCP; login institucional.
- Mensagem final: "Dois órgãos se encontraram, se conectaram e conversaram, e a decisão foi sempre humana."

## Contingência
- Gravação/capturas disponíveis: **nenhuma** (ainda não existem; gravar após o ensaio).
- Como estão identificadas: o modo demonstração mostra a etiqueta "Modo demonstração" no topo; qualquer gravação deve ter a legenda "GRAVAÇÃO".
- Procedimento se a internet/API falhar: entrar pelo botão **"Entrar em modo demonstração"** (um navegador, dados fictícios, sem conversa entre órgãos) e dizer em voz alta: *"Esta é a demonstração simulada; a conversa entre órgãos depende do servidor."* Não apresentar isso como integração real.
