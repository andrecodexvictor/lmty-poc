# LMTY POC — Relatório de Testes Ampliado

## 1. Objetivo

Esta rodada ampliou o POC para validar o framework LMTY e a camada MAL — **Model Attachment Layer** — em casos de uso operacionais, além de introduzir kernels nativos leves em Rust e C, uma fronteira de Pareto multidimensional e uma avaliação controlada de coding baseada em prompts públicos do HumanEval.

A meta de engenharia foi evitar “spaghetti code”: cada componente possui uma responsabilidade estreita, contratos simples, dados declarativos e quality gates reproduzíveis. A auditoria Python terminou com complexidade ciclomática máxima 2.

## 2. Casos de uso do framework e da MAL

Foram executados seis casos de uso, três do framework e três da MAL.

| Camada | Caso | Verificação |
|---|---|---|
| Framework | Classificação de tarefa visual | Rota visual, browser e visual verification |
| Framework | Reparo de bug | Rota de reprodução e test runner |
| Framework | Controle de performance | Rota de medição e test runner |
| MAL | Estado por sessão | Reutilização de sessão e trace associado |
| MAL | Capability boundary | Ferramentas limitadas pelo attachment |
| MAL | Fallback generalista | Rota segura para tarefa sem domínio específico |

**Resultado:** 6 de 6 casos aprovados. O resultado completo, com traces individuais, está em `reports/use_cases.json`.

## 3. Kernels nativos

### Rust

O kernel Rust está em `native/rust_kernel`. Ele oferece classificação, orçamento de contexto, orçamento de ferramentas e decisão compacta. O módulo não possui dependências externas e é compilado por Cargo.

### C

O kernel C está em `native/c_kernel`. A implementação utiliza tabela de regras e busca linear curta, evitando uma cadeia de condicionais de domínio. O teste é compilado com `-std=c11 -O2 -Wall -Wextra`.

| Kernel | Testes | Resultado |
|---|---:|---|
| C | 2 asserções principais | Aprovado |
| Rust | 2 testes unitários | Aprovado |

Os kernels nativos são candidatos a substituir apenas o roteamento e os cálculos pequenos no caminho crítico. Eles não substituem o runtime de políticas, verificadores ou o modelo de fronteira.

## 4. Fronteira de Pareto

A fronteira multidimensional considera qualidade e confiabilidade como objetivos de maximização; tokens, latência e complexidade como objetivos de minimização.

```text
maximize: quality, reliability
minimize: tokens, latency, complexity
```

O resultado atual contém três pontos não dominados porque existe um trade-off explícito entre overhead e complexidade:

| Candidato | Qualidade | Confiabilidade | Tokens | Latência | Complexidade |
|---|---:|---:|---:|---:|---:|
| `baseline-general` | 1.00 | 1.00 | 948 | 0.03 | 1.2 |
| `frontend-balanced` | 1.00 | 1.00 | 560 | 0.02 | 6.8 |
| `frontend-compact` | 1.00 | 1.00 | 350 | 0.05 | 5.4 |

A presença dos três candidatos na fronteira é esperada: o baseline minimiza a complexidade do artefato, o candidato compacto minimiza tokens e o candidato balanceado apresenta menor latência observada nesta execução. O arquivo reproduzível é `reports/pareto_multidimensional.json`.

## 5. Avaliação de coding com dados públicos

Foi utilizado o conjunto público HumanEval, obtido do repositório oficial `openai/human-eval` [1]. Foram selecionadas cinco tarefas do arquivo `HumanEval.jsonl.gz`. O modelo configurado foi `gpt-5-mini`, e as respostas foram avaliadas estaticamente quanto à presença de saída, assinatura da função e ausência de fences Markdown.

| Métrica | Resultado |
|---|---:|
| Fonte | `openai/human-eval` |
| Tarefas | 5 |
| Modelo | `gpt-5-mini` |
| Score estático médio | 1.0000 |
| Execução de código gerado | Desabilitada |

O score estático **não é pass@1** e não representa correção funcional. A execução foi desabilitada deliberadamente porque o próprio harness oficial alerta que código gerado é não confiável e deve ser executado somente em sandbox robusto [1]. O artefato bruto está em `reports/public_coding_eval.json`, incluindo prompts identificadores, completions, tokens e latência.

A próxima avaliação deve utilizar o executor oficial em sandbox isolado, com limites de CPU, memória, filesystem, rede, processos e tempo. Somente então será legítimo publicar pass@1 ou pass@k.

## 6. Complexidade e estilo de implementação

A auditoria atual cobre os módulos Python de runtime, compiler, evals, models e o novo Pareto.

| Indicador | Resultado |
|---|---:|
| Funções auditadas | 43 |
| Complexidade máxima | 2 |
| Complexidade média | 1.233 |
| Funções acima do limite | 0 |

A regra foi implementada em `scripts/complexity_audit.py` e deve permanecer como quality gate. Para Rust e C, os kernels também foram escritos com tabelas, funções curtas e contratos estreitos, embora a auditoria numérica automatizada atual seja Python/AST.

## 7. Limitações e validade

Os verificadores de frontend continuam sendo heurísticos no POC. Os kernels nativos ainda não estão ligados ao runtime Python por FFI; eles são implementações de referência e microcomponentes testáveis. A avaliação HumanEval não executa código e, por isso, deve ser interpretada como teste de integração LLM–benchmark, não como avaliação de correção.

Também não se deve interpretar a qualidade estática perfeita em cinco tarefas como evidência de capacidade geral. A amostra é pequena e foi usada para validar o caminho de dados, logging, orçamento e separação segura entre geração e execução.

## 8. Próxima etapa recomendada

A próxima etapa técnica é construir um executor isolado para um subconjunto público de HumanEval, integrar o kernel Rust por uma biblioteca C-ABI ou PyO3, comparar o runtime Python com o kernel nativo em microbenchmarks e introduzir casos held-out que não participem da geração de políticas. O objetivo deve ser medir ganho real por tarefa, não apenas produzir código curto.

## Referências

[1]: https://github.com/openai/human-eval "OpenAI HumanEval — evaluation harness and public dataset reference"
