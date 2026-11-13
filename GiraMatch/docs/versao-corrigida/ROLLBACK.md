# ROLLBACK

As versões estão marcadas no Git do projeto:

| Tag | Conteúdo |
|---|---|
| `v0-original` | commit `55b52a6` (original) |
| `v0-auditada` | commit `27d941d` (auditada, antes das correções) |
| `v1-corrigida` | versão corrigida |

## Voltar para a versão auditada sem apagar nada
```
git switch --detach v0-auditada     # só olhar/executar; volta com: git switch main
```
## Desfazer só as correções, mantendo o histórico
```
git revert --no-edit v0-auditada..v1-corrigida
```
## Restaurar o original em outra pasta
```
git archive v0-original -o GiraMatch_original.zip
```
Os ZIPs gerados ficam em `docs/` e **não** são versionados. A verificação de integridade está em `SHA256SUMS.txt`.
