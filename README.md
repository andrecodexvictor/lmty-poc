# Let Me Tune You — POC

POC executável da arquitetura LMTY para attachments comportamentais L0/L1. O projeto inclui runtime, pacote `frontend.lmty`, benchmark, compilador black-box, traces, cálculos e relatórios versionados.

## Execução

```bash
cd lmty-poc
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 scripts/complexity_audit.py
PYTHONPATH=. python3 scripts/run_poc.py
```

A execução gera ou atualiza os arquivos em `reports/`:

| Arquivo | Conteúdo |
|---|---|
| `benchmark.json` | Métricas agregadas do benchmark |
| `optimizer_scores.json` | Cálculos por candidato |
| `pareto_frontier.json` | Candidatos não dominados |
| `frontend.compiled.lmty.json` | Artefato escolhido pelo compilador |
| `runtime_traces.json` | Traces das execuções |
| `complexity_audit.json` | Auditoria de complexidade |
| `POC_TECHNICAL_REPORT.md` | Relatório técnico detalhado |

## Estrutura

```text
lmty/
├── models/          contratos de dados
├── runtime/         loader, policy, verification e engine
├── evals/           benchmark e métricas
└── compiler/        scoring, Pareto e compilação
examples/            pacotes .lmty de referência
scripts/             execução e quality gates
tests/               testes unitários
reports/             cálculos, traces e relatórios reproduzíveis
```

## Extensões nativas e benchmarks

Os kernels leves em `native/` possuem implementações equivalentes em Rust e C. Eles podem ser testados com `make -C native c-test` e `make -C native rust-test`. Os casos de uso do framework e da MAL são definidos em `tests/use_cases.json` e executados por `scripts/run_use_cases.py`. A fronteira Pareto multidimensional é gerada por `scripts/run_pareto.py`.

O benchmark de coding público usa os prompts do HumanEval obtidos em `vendor/human-eval`. O comando `PYTHONPATH=. python3 scripts/run_public_coding_eval.py --limit 5` chama o modelo configurado e faz análise estática segura. A execução do código gerado permanece desabilitada até existir um sandbox robusto.

## Política de complexidade

O projeto adota como meta operacional **complexidade ciclomática McCabe máxima 2 por função**. O auditor AST não conta compreensões como ramificações independentes; conta decisões condicionais, loops, handlers de exceção e operadores booleanos. O resultado deve ser verificado antes de cada commit.

## Escopo técnico

O POC implementa especialização comportamental e stateful. Não afirma suporte a logits, prefixos K/V ou activation steering. Esses níveis exigem uma ABI do provedor e ficam fora do primeiro marco executável.

## Evolução: LMTY Attachment Studio

O POC é o núcleo executável da arquitetura. A aplicação complementar **LMTY Attachment Studio** transforma seus conceitos em uma superfície web: ingestão JSONL/CSV, compilação de artifacts `.lmty`, sessão MAL, traces, Pareto, memória externa, grafo de abstração e CLI. A documentação matemática em níveis baixo, médio e alto está no repositório do Studio, junto do critério estrutural de aceitação e dos relatórios de cenários.

Essa separação é deliberada: este repositório mantém runtime, kernels C/Rust e benchmark reproduzível; o Studio gerencia e explica o ciclo de vida operacional desses componentes.
