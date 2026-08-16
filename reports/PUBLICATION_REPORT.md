# LMTY POC — Relatório de Publicação

## Repositório

| Campo | Valor |
|---|---|
| Repositório | `andrecodexvictor/lmty-poc` |
| URL | https://github.com/andrecodexvictor/lmty-poc |
| Visibilidade | Privado |
| Branch principal | `main` |
| Commit inicial | `cd244ce` |
| Mensagem | `feat: add LMTY L0 L1 proof of concept` |

## Conteúdo publicado

O repositório contém o runtime L0/L1, o pacote de exemplo `frontend.lmty`, o benchmark, o compilador black-box, testes unitários, workflow de CI, auditoria de complexidade, cálculos de scoring, fronteira Pareto, artefato compilado, traces e relatórios técnicos.

## Quality gates locais

| Gate | Resultado |
|---|---|
| Testes unitários | 3 testes aprovados |
| Complexidade máxima | 2 |
| Complexidade média | 1.231 |
| Funções acima do alvo | 0 |
| Benchmark executado | Sim |
| Relatório técnico versionado | Sim |
| Workflow GitHub Actions | Configurado |

O workflow `.github/workflows/quality.yml` repete os testes, a auditoria de complexidade e a execução reprodutível do POC em pushes e pull requests.
