# LMTY POC — Relatório Técnico

## 1. Escopo

Este relatório documenta o POC LMTY implementado no nível **L0/L1**. O sistema demonstra a aplicação de um attachment comportamental a um modelo congelado, utilizando manifesto declarativo, roteamento por classe de tarefa, seleção de ferramentas, compilação de contexto, verificadores, estado de sessão, telemetria e otimização black-box.

O POC não simula acesso a logits, prefixos K/V ou ativações internas. Esses níveis permanecem como extensões futuras dependentes de uma ABI do provedor.

## 2. Módulos implementados

| Módulo | Responsabilidade | Evidência |
|---|---|---|
| `lmty.models.schema` | Tipos `Task`, `Decision`, `AttachmentPackage` e `RuntimeResponse` | Estruturas tipadas e serializáveis |
| `lmty.runtime.package` | Leitura e validação de pacotes `.lmty` | `manifest.json` e políticas JSON |
| `lmty.runtime.policy` | Classificação de tarefas, roteamento, seleção de tools e contexto | Rotas frontend por classe |
| `lmty.runtime.verification` | Verificadores determinísticos de POC | Typecheck, tests, a11y, visual e security |
| `lmty.runtime.engine` | Inferência aplicada, estado, reparo e traces | Runtime L0/L1 |
| `lmty.evals.benchmark` | Benchmark frontend e agregação de métricas | 6 tarefas controladas |
| `lmty.compiler.optimizer` | Scoring multiobjetivo e fronteira Pareto | Três candidatos avaliados |
| `scripts.complexity_audit` | Auditoria AST de complexidade McCabe | Quality gate com máximo 2 |

## 3. Algoritmo de execução

O runtime resolve o pacote, cria ou recupera o estado da sessão, classifica a tarefa, escolhe a rota, filtra ferramentas autorizadas, compila a cápsula de contexto, executa o modelo, verifica a resposta e registra um trace. Quando a verificação falha e a política permite, uma segunda chamada é realizada com instrução de reparo.

A política é deliberadamente externa aos pesos do modelo. O objeto de especialização é aplicado na fronteira entre harness e modelo.

## 4. Algoritmo de compilação

Cada candidato possui orçamento de contexto, limite de ferramentas, política de retry, ferramentas obrigatórias e possíveis sobrescritas de rota. Para cada candidato, o POC calcula:

```text
quality = média dos scores de verificação
reliability = fração de respostas aprovadas
tokens = context_budget + 18 × número_de_ferramentas + 4 × max_tool_calls
complexity = 2 × número_de_route_overrides + número_de_ferramentas + max_tool_calls / 10
reward = 0.45 × quality + 0.35 × reliability
         − 0.0005 × tokens − 0.001 × latency − 0.01 × complexity
```

A fronteira Pareto remove candidatos dominados. Um candidato `A` domina `B` quando possui reward pelo menos igual, complexidade no máximo igual e melhora estritamente pelo menos uma dessas dimensões.

## 5. Resultado do benchmark

O benchmark inicial contém seis tarefas frontend: implementação, bug, interface visual, acessibilidade, performance e implementação de componente.

| Métrica | Resultado observado |
|---|---:|
| Tarefas | 6 |
| Qualidade média | 1.0000 |
| Confiabilidade | 1.0000 |
| Caracteres médios de saída | 108.00 |
| Latência média observada | inferior a 1 ms no modelo simulado do POC |

Os valores de qualidade e confiabilidade representam o **verificador textual do POC**, não desempenho de engenharia frontend real. A próxima etapa deve substituir o modelo simulado e os verificadores heurísticos por execução real de TypeScript, testes, browser e acessibilidade.

## 6. Comparação dos candidatos

| Candidato | Tokens estimados | Complexidade | Reward | Situação |
|---|---:|---:|---:|---|
| `baseline-general` | 948 | 1.2 | 0.3140 | Fronteira, baixo controle especializado |
| `frontend-balanced` | 560 | 6.8 | 0.4520 | Dominado pelo candidato compacto |
| `frontend-compact` | 350 | 5.4 | 0.5710 | Selecionado pelo compilador |

O resultado demonstra o mecanismo de seleção, mas não deve ser interpretado como prova científica de superioridade. Como o modelo do POC é determinístico e os verificadores são simplificados, a variação de qualidade ainda é limitada. O valor atual é validar o pipeline e tornar explícitas as equações.

## 7. Complexidade ciclomática

A auditoria AST utiliza uma aproximação McCabe: cada função começa em 1 e recebe incremento por `if`, loops, handlers de exceção e operadores booleanos. O quality gate foi definido em **máximo 2 por função**.

| Indicador | Resultado |
|---|---:|
| Funções auditadas | 39 |
| Complexidade máxima | 2 |
| Complexidade média | 1.231 |
| Funções acima do limite | 0 |

A métrica é um guardrail de manutenção. Ela não substitui revisão arquitetural, testes, análise de acoplamento ou inspeção de comportamento.

## 8. Limitações conhecidas

O modelo executor atual é um stub determinístico. Os verificadores não compilam código, não iniciam browser e não executam testes reais. O benchmark não contém tarefas de produção nem conjunto held-out independente. O scoring privilegia overhead estimado e ainda precisa incorporar custo real de tokens, chamadas externas, tool latency e resultados objetivos de execução.

Portanto, este POC prova a **forma operacional** da arquitetura, não a tese completa de que uma especialização complexa pode ser comprimida sem perda em um attachment pequeno.

## 9. Próximos experimentos

A próxima iteração deve conectar um provider compatível com Responses, substituir o modelo stub por chamadas configuráveis, executar projetos frontend isolados em sandbox, introduzir casos held-out imutáveis, registrar custos reais, adicionar canary/rollback e comparar L0/L1 contra prompt longo, RAG/MCP sem política otimizada e harness manual.
