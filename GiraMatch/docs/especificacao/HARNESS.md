# Harness — instalar, executar e testar

Legenda: ✅ executado nesta sessão · ⏳ previsto, **não executado**.

| Passo | Comando (pasta `giramatch-backend/giramatch-backend`) | Situação |
|---|---|---|
| Instalar | `python -m pip install pytest "psycopg[binary]"` | ✅ |
| Testes (SQLite) | `python -m pytest -q` → 28 passed | ✅ |
| Reset dos dados de demo (local) | `python -m giramatch demo` | ✅ |
| Subir a API (local) | `python -m giramatch servir` | ✅ |
| Teste de saúde | `GET /api/health` → `{"status":"ok"}` | ✅ (local) |
| Testes em PostgreSQL | `TEST_DATABASE_URL=postgres://... python -m pytest` (apaga as tabelas) | ⏳ **NÃO VERIFICADO** |
| Deploy | Render → New → Blueprint → `render.yaml` | ⏳ |
| Evidências | ver `EVIDENCIAS_EXECUCAO.md` | ✅ (local) |

## Hospedagem sem terminal
O `render.yaml` cria a API e o PostgreSQL. Na subida, a API cria as tabelas e, com `GIRAMATCH_DEMO_SE_VAZIO=1`,
carrega dados fictícios. Usuários extras: `GIRAMATCH_USUARIOS=ORGAO|Nome|email|senha;...`.

## Roteiro de demonstração (≈ 5 min, honesto)
1. Entrar como TRE-PB (navegador A) e como TJPB (navegador B, janela anônima), **com a API publicada**.
2. O TRE-PB abre o feed e vê um match com score e motivos.
3. O TRE-PB clica em Conectar; o TJPB vê o pedido, aceita e abre o comitê.
4. Trocar uma mensagem entre os dois (aparece em até 5 s).
5. Dizer à banca: dados **fictícios**, economia **ilustrativa**, decisão sempre **humana**.

Sem a API publicada, a demo é só o modo demonstração (um navegador, sem conversa entre órgãos).
