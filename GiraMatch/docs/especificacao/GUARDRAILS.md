# Guardrails

## Validações e erros
- Entradas validadas em `validar_demanda` (mês 1–12, natureza e tipo permitidos, valores numéricos).
- Corpo da requisição limitado a 2 MB; a importação de CSV informa as linhas com erro e importa o resto.
- Erros previsíveis retornam JSON `{"erro": ...}` com status adequado (401, 404, 405, 413); falhas inesperadas dão 500 sem expor detalhes.
- Cada requisição roda em transação: erro faz *rollback*.

## Decisões e respostas jurídicas indevidas
- O sistema **sugere**; a decisão de cooperar é sempre do gestor (aviso exibido nas telas de match).
- Nenhuma tela trata o caminho jurídico como conclusivo: há alerta para confirmar com a assessoria jurídica.
- A economia exibida é **estimativa ilustrativa**, nunca valor garantido.
- Não há texto gerado por IA, então não há risco de alucinação no MVP atual.

## Segredos e dados
- `DATABASE_URL` e senhas reais só em variáveis de ambiente (painel do Render), nunca no repositório.
- Não colocar dados reais, processos sigilosos ou credenciais institucionais.
- `GIRAMATCH_CORS=*` é aceitável só para o protótipo; depois, restringir ao endereço do site.
