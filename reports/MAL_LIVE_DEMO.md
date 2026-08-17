# MAL — Demonstração em execução

## Cenário

O attachment `frontend@0.1.0` foi executado em uma sessão persistente chamada `mal-live-demo`. Foram enviadas duas tarefas consecutivas de debugging na mesma sessão:

1. Investigar um bug de hydration e reproduzir o erro.
2. Continuar o diagnóstico e preparar um teste de regressão.

A sessão recebeu somente as capacidades `filesystem`, `test_runner` e `typecheck`. A capacidade `browser` não foi disponibilizada.

## Resultado observado

| Invariante | Resultado |
|---|---|
| Attachment resolvido | `frontend@0.1.0` |
| Rota selecionada | `reproduce → isolate → patch → regression` |
| Ferramenta de testes habilitada | Sim |
| Browser habilitado | Não |
| Verificação da chamada 1 | Aprovada, score 1.0 |
| Verificação da chamada 2 | Aprovada, score 1.0 |
| Sessão persistente | Sim |
| Número de chamadas no estado | 2 |
| Número de traces | 2 |

O runtime preservou o estado da sessão entre as chamadas, reaplicou a mesma política de debugging e respeitou o capability boundary. Os identificadores dos traces gerados nesta execução estão em `reports/mal_live_demo.json`.

## O que funcionou de fato

O que foi executado de fato na VM foi o fluxo do Attachment Runtime: carregamento do pacote `.lmty`, resolução da política, classificação, roteamento, filtragem de ferramentas, compilação do contexto, manutenção do estado, verificação e emissão de traces.

## Limite atual do POC

O modelo executor padrão ainda é um stub determinístico e os verificadores atuais usam um contrato textual de POC. Portanto, esta demonstração comprova o funcionamento real da **MAL como camada de controle e estado**, mas não comprova ainda a execução real de um bug em um projeto externo, nem a execução de testes TypeScript ou browser. Para isso, o próximo módulo deve conectar `test_runner`, `filesystem` e `browser` a executores isolados com logs e códigos de saída reais.

## Reprodução

```bash
cd lmty-poc
PYTHONPATH=. python3 scripts/demo_mal_live.py
```

O comando regenera `reports/mal_live_demo.json` e imprime o resultado completo da sessão.
