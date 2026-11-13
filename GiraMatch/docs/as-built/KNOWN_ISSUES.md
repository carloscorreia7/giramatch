# KNOWN_ISSUES

> **Atualizado na versão corrigida (`v1-corrigida`).** K-05 (limite de login) e K-06 (log com IP/URL) foram corrigidos; a falha de banco indisponível (F-001) também. Situação completa em `docs/versao-corrigida/AUDIT_REMEDIATION_MATRIX.md`.

Legenda de confiança: [C] confirmada · [I] inferida · [N] não verificada.

## Falhas e riscos
| ID | Item | Conf. |
|---|---|---|
| K-01 | **Senhas de demonstração e de teste ficam visíveis no código público do site** (`index.html`). Aceitável só por serem fictícias. | C |
| K-02 | **PostgreSQL nunca foi executado.** A camada de compatibilidade (`?`→`%s`, `RETURNING id`, schema próprio) foi escrita sem teste real. | C |
| K-03 | `GIRAMATCH_CORS` tem padrão `*` (qualquer origem). | C |
| K-04 | Um único processo `http.server` com nova conexão por requisição: adequado para demo, não para carga. | I |
| K-05 | ~~Sem limite de tentativas de login~~ **CORRIGIDO** (F-003): 8 falhas → 429. Contadores em memória. | C |
| K-06 | ~~Log com IP e URL~~ **CORRIGIDO** (F-006): log só com método, caminho e status (verificado em execução). | C |
| K-07 | Sessões expiradas só são removidas quando o token é reutilizado; a tabela pode crescer. | I |
| K-08 | O comando `demo` em SQLite **apaga o arquivo** do banco indicado. | C |

## Lacunas e limitações
- **Modo demonstração** sempre abre com a visão do TRE-PB, qualquer que seja a conta; não há troca de órgão. [C]
- **Chat entre órgãos** só funciona com a API publicada; no modo demonstração não há interlocutor. [C]
- **Representantes do comitê** ficam só no navegador (sem tabela no banco). [C]
- `DOCUMENTACAO.md` está parcialmente desatualizada (cita só SQLite e `127.0.0.1:8000`). [C]
- `API_PRODUCAO` em `app.js` usa uma URL presumida que não existe até o deploy. [C]
- Sem integrações reais (PNCP, SSO), sem IA; percentuais de economia são ilustrativos. [C/D]
- Nenhum teste automatizado do front-end. [C]

## Não verificável nesta análise
PostgreSQL; deploy no Render; comportamento em navegador real; capturas de tela; conteúdo do `giramatch.db` local; leitura linha a linha de todo `api.py`/`matching.py`/páginas HTML; citação da alteração "Res. CNJ 674/2026" (vinda de documento externo, não confirmada).
