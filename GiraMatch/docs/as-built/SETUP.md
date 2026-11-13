# SETUP

Legenda: ✅ executado nesta sessão · ⏳ não executado. Observação estática ≠ compilação ≠ inicialização ≠ teste ponta a ponta.

## Pré-requisitos
- Python 3.10+ (testado: 3.13.14, Windows 11) ✅. Docker: **não disponível** neste ambiente.
- Para PostgreSQL: `psycopg[binary]` e um banco acessível por `DATABASE_URL` ⏳.

## Instalação (pasta `giramatch-backend/giramatch-backend`)
```
python -m pip install pytest "psycopg[binary]"     ✅
```
O modo SQLite não exige nada além do Python (o `pytest` só serve para os testes).

## Configuração
Copie `.env.exemplo` para o ambiente do servidor/hospedagem; **não** versione valores reais. Variáveis: `DATABASE_URL`, `PORT`, `GIRAMATCH_CORS`, `GIRAMATCH_DEMO_SE_VAZIO`, `GIRAMATCH_USUARIOS` (ver `AS_BUILT.md`).

## Execução local
```
python -m giramatch demo       # cria giramatch.db com dados fictícios (APAGA o arquivo existente)   ✅ (em banco temporário)
python -m giramatch servir     # API em http://127.0.0.1:8000                                         ✅ (porta 8765, banco temporário)
```
Depois abra `frontend/index.html` (ou sirva a pasta: `cd frontend && python -m http.server 5500`) ⏳ (sem navegador nesta sessão).

## Testes
```
python -m pytest -q            # 28 passed (SQLite)   ✅ (versão corrigida)
```

## Encerramento
`Ctrl+C` no terminal da API. Para limpar a demo local, apague `giramatch.db`.

## Hospedagem (prevista) ⏳
`render.yaml` (Render → New → Blueprint). Não executado; URL da API desconhecida.
