# Checklist de transferência — GiraMatch (preenchido)

Legenda: [x] comprovado · [ ] pendente · [~] parcial · n/a não se aplica.
Versão: tag `v1-corrigida`. Preenchido por quem também desenvolveu o projeto (**sem independência**).

## Insumos
- [ ] **Enunciado do desafio, regulamento e critérios da banca** — não fornecidos. Sem isso, não há avaliação de aderência.
- [x] Descrição da solução, usuário e fluxo — `DOCUMENTACAO.md`, `docs/especificacao/SPEC.md` (gestor de contratações; cadastrar → match → conectar → comitê).
- [x] Código atual — repositório completo; ZIP em `docs/GiraMatch_v1_corrigida.zip`.
- [~] Prazo, SO, RAM/CPU, Docker, internet — SO: Windows 11; Python 3.13.14; Docker: **não disponível**; internet: disponível nesta sessão. **Prazo restante e RAM/CPU: não informados.**
- [x] Dados fictícios, sem dados pessoais ou sigilosos — `seed.py`, `exemplos/pca_exemplo.csv`; nada real foi usado.
- n/a IA/API externa — o MVP não usa IA nem API externa.
- n/a HTML de exemplo — não foi fornecido e não é necessário.

## Avaliação mínima do MVP
- [x] `REQ-001` caso válido — `test_nova_demanda_gera_match`, `test_importar_csv` (SQLite).
- [x] `REQ-001` entrada inválida — `test_req001_entrada_invalida_e_sem_login` (mês 13 e descrição vazia → 422; sem login → 401), `test_req001_json_malformado`.
- [x] Real × simulado identificados — real: API + banco (testado em SQLite); simulado: modo demonstração do navegador; planejado: PNCP, SSO, IA (`SPEC.md`, `AS_BUILT.md`, slide 3).
- [x] Autorização e acesso (vários órgãos) — `test_nao_ve_match_de_terceiros`, `test_valor_sigiloso_escondido_do_outro_orgao`, comitê de terceiro → 404, token expirado/inventado → 401, limite de login → 429.
- n/a LLM (prompt injection, resposta sem referência) — sem LLM; a decisão de cooperar é sempre humana (conectar/recusar).
- [~] Segredos e dados sensíveis fora do código, ZIP, tela, logs e apresentação —
  código, ZIP e `.env` limpos (varredura por padrões); logs sem IP/URL (verificado em execução).
  **Exceção:** as credenciais **fictícias** de demonstração (`demo123` e a conta de teste) aparecem em `index.html`, na tela de login e na apresentação. Nunca reutilize essas senhas.
- [x] Testes com comando, resultado e ambiente — `docs/especificacao/EVIDENCIAS_EXECUCAO.md`, `docs/versao-corrigida/FINAL_VALIDATION.md` (**28 passed**, SQLite). PostgreSQL, deploy e navegador: **NÃO EXECUTADO**.
- [~] Diagrama e slides consistentes com o software — PNG e slide 2 batem com a arquitetura (20 rotas, mesmos componentes), mas a apresentação **não foi aberta em navegador** e o slide 3 **não tem capturas reais**.
- [x] Decisão final com pendências e riscos residuais — `FINAL_VALIDATION.md` (**ESTADO NÃO OK — validação incompleta**) e `RESIDUAL_RISKS.md`.

## Roteiro de demonstração de 5 minutos (adaptado ao GiraMatch)
Pré-requisito: API publicada e acordada (abra o site 2–3 min antes; no plano gratuito ela "dorme"), com dois navegadores logados: TRE-PB e TJPB.

| Tempo | O que mostrar |
|---|---|
| 0:00–0:40 | Problema: órgãos compram e capacitam isoladamente e perdem escala. Usuário: gestor de contratações. |
| 0:40–1:10 | Benefício: o sistema **sugere** parcerias e explica o porquê. Sem prometer economia real: os valores são ilustrativos. |
| 1:10–3:40 | **Fluxo real:** TRE-PB abre o feed e vê um match (score, motivos, caminho jurídico, alertas) → clica em Conectar → no TJPB aparece o pedido → TJPB aceita → comitê com cronograma → uma mensagem de cada lado (aparece em até 5 s). |
| 3:40–4:20 | **Exceção e controle:** "Agora não" não revela a recusa ao outro lado; valor sigiloso não aparece para o outro órgão; a decisão é sempre do gestor. |
| 4:20–5:00 | Resultado: fluxo funcionando entre dois órgãos. Limites: dados fictícios, economia ilustrativa, sem integração real com PNCP. Próximo passo: PNCP e login institucional. |

Plano B se a API não responder: usar o **modo demonstração** (um navegador, sem conversa entre órgãos) e **dizer isso à banca**.

## Pendências antes de apresentar
1. Enviar o edital e o prazo.
2. Publicar a API, rodar os testes em PostgreSQL e anotar o `/api/health`.
3. Ensaiar o roteiro acima com dois navegadores e tirar as capturas para o slide 3.
4. Preencher nome da equipe e URL na apresentação; definir `GIRAMATCH_CORS`.
5. Pedir revisão cruzada a outra pessoa da equipe.
