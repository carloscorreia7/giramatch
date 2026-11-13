# Regras de negócio, restrições e limites

## Regras do match
- Só pares de **órgãos diferentes**, **mesmo ano** e **mesma natureza**.
- Pesos: similaridade 45%, tempo 25%, território 15%, sustentabilidade 15%; bônus +5 para contratos que terminam juntos. Limiar: **60** (`config.py`).
- Contratação → IRP (Lei 14.133/2021, art. 86). Capacitação → capacitação compartilhada via acordo de cooperação técnica.
- Federal + estadual → gerenciador sempre o **federal** (art. 86, §8º), com alerta para confirmar com a assessoria jurídica.
- Alerta ME/EPP quando a soma passa de R$ 80 mil (LC 123/2006, art. 48, I); alerta de prazo (> 3 meses) e de unidades diferentes.

## Privacidade e sigilo
- `valor_sigiloso`: o valor só aparece para o próprio órgão; o outro vê `null` e não há economia em reais.
- Um órgão só vê matches dos quais participa.
- Recusas **nunca** são reveladas.
- O pedido de conexão é avisado ao outro lado; a decisão é sempre humana.

## Dados e LGPD
- Todos os dados do projeto são **sintéticos**. É **proibido** carregar processos sigilosos, dados pessoais reais ou credenciais institucionais.
- Senhas com PBKDF2-SHA256; sessões com expiração de 12 h.
- As contas de demonstração (`demo123`) e a de teste existem **só para o protótipo**; as senhas do modo demonstração ficam visíveis no código do site.

## Limites de uso
- Protótipo: **não** homologado para produção judicial. Os fundamentos jurídicos devem ser validados pela assessoria de cada órgão.
- Sem IA generativa no MVP (o match usa regras explicáveis). Se houver IA no futuro: documentar finalidade, modelo, custo, revisão humana e testes de alucinação e prompt injection, e avaliar a Res. CNJ 615/2025 e sua alteração (a citada alteração nº 674/2026 **não foi verificada** aqui).
