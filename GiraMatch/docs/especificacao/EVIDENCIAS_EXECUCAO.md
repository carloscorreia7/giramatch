# Evidências de execução

Ambiente: Windows 11, Python 3.13.14, pytest 9.x, SQLite. Data: 12/11/2026. Banco de demo usado: arquivo temporário (o `giramatch.db` do projeto não foi tocado).
Pasta: `giramatch-backend/giramatch-backend`.

| # | Comando | Resultado | Código de saída | Evidência |
|---|---|---|---|---|
| 1 | `python -m pip install pytest "psycopg[binary]"` | instalado | 0 | saída do pip |
| 2 | `python -m pytest -q` | **19 passed** em ≈15 s (SQLite) | 0 | `...................  [100%]` |
| 3 | `python -m giramatch --db <temp>/demo.db demo` | banco criado, **39 matches sugeridos** | 0 | "Banco de demonstração criado… 39 matches sugeridos." |
| 4 | `python -m giramatch --db <temp>/demo.db servir` (porta 8765) | API no ar | — | ver 5 a 7 |
| 5 | `GET /api/health` | HTTP 200, `{"status":"ok","versao":"0.1.0"}` | — | resposta JSON |
| 6 | login `gestor@trepb.giramatch.demo` + `GET /api/matches?pendentes=1` | **25 matches pendentes** do TRE-PB | — | contagem retornada |
| 7 | login com credenciais inválidas | HTTP 401 (negativo) | — | status HTTP |

## Fluxo principal (REQ-001 a REQ-003)
Coberto pelos testes automatizados de ponta a ponta na API (`test_conexao_dos_dois_lados_cria_comite`,
`test_conversa_entre_os_dois_orgaos`, `test_recusa_encerra_match`, `test_nova_demanda_gera_match`).
Verificação positiva, negativa (texto vazio, órgão de fora, login errado) e de ausência de dados
(comitê novo sem mensagens) incluídas.

## NÃO EXECUTADO
- **PostgreSQL** (nenhum servidor disponível; um binário portátil foi bloqueado e não contornado). `TEST_DATABASE_URL` não foi usada.
- **Deploy no Render** e URL pública da API.
- **Front-end no navegador:** nenhuma captura de tela real foi feita (sem ferramenta de navegador nesta sessão); só verificação de sintaxe (`node --check`) e do modo demonstração por script.
- **Docker:** não há Docker neste ambiente; alternativa documentada: comandos Python acima.
- Testes de IA (injeção, alucinação): **não se aplicam**, o MVP não usa IA generativa.

## Limitações
Dados fictícios; economia ilustrativa; edital e critérios da banca não fornecidos; conversa entre órgãos só com API publicada.
