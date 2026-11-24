# Falhas operacionais — UC32 / #29

O painel `/deshboard/falhas` é exclusivo de ADMIN. O menu administrativo e o
painel inicial oferecem acesso à tela. Usuários comuns recebem apenas a mensagem
genérica de falha em suas reflexões e podem solicitar outra tentativa.

## Endpoints e autorização

- `GET /admin/operational-failures`: listagem paginada.
- `GET /admin/operational-failures/{source}/{failure_id}`: diagnóstico e rastreabilidade.
- `GET /journal/entries/{id}/analysis/failures`: compatibilidade legada, agora ADMIN;
  retorna a listagem administrativa filtrada pela entrada.

Todos os endpoints de diagnóstico validam o papel no backend. A origem de dados
não é consultada quando o papel é USER. A rota legada também recusa o proprietário
com 403. Não basta alterar o papel no sessionStorage: ele só controla a apresentação;
a API determina o papel pelo token autenticado.

A consulta comum `GET /journal/entries/{id}/analysis` mantém a verificação de
propriedade e não retorna diagnóstico. O reenvio pelo proprietário permanece em
`POST /journal/entries/{id}/analysis`. A consulta administrativa não concede acesso ao conteúdo do diário. O detalhe
da falha mais recente permite confirmar reprocessamento pela operação do UC33.

## Origens e estados

| Origem | Dados consultados | Rastreamento |
| --- | --- | --- |
| `journal` | Registros `failed` em `journal_schema.analysis` | ID da falha e da entrada; estado atual da entrada |
| `work_ingestion` | Ingestões com falha ou código registrado | ID da ingestão e da obra |
| `work_chunk` | Trechos de ingestão com falha ou código registrado | ID do trecho e da ingestão |
| `inbox` | Eventos recebidos com falha ou código registrado | Chave consumidor:evento e ID do evento |
| `outbox` | Eventos com `failed_at` ou estado FAILED | ID do evento |

Os registros das análises individuais permanecem consultáveis após recuperação,
com o estado atual `analyzed`, por exemplo. As demais origens representam os
registros existentes em suas tabelas; não é criado um histórico retroativo de
cada tentativa nem recuperado um erro apagado por processamento posterior.
Falhas sem registro persistido, incluindo falhas atuais da análise contextual,
não surgem automaticamente nesse painel. O registro de novas origens é uma
extensão separada; a consulta não inventa diagnósticos ausentes.

## Filtros e resposta

A listagem aceita `source`, `state`, `entity_id`, `since`, `until`, `limit` e
`offset`. Datas exigem fuso horário e o intervalo deve estar em ordem. `limit`
aceita 1–100 (padrão 20), `offset` é não negativo. O identificador é comparado
exatamente por parâmetro vinculado, sem interpolação SQL. A ordenação é por data
decrescente, origem e ID, com paginação de 20 itens na interface.

A resposta contém `failures`, `total`, `limit`, `offset`. Lista e detalhe incluem
origem, ID, ID do registro, ID relacionado, estado atual, datas, código, mensagem
segura e tentativas conhecidas. O detalhe ausente retorna 404; indisponibilidade
do banco retorna 503 com mensagem genérica. Filtros inválidos retornam 422.

Não são entregues texto ou título do diário, resumo da reflexão, identificação
pessoal, payloads de eventos, URLs/chaves de armazenamento, credenciais, stack
traces ou mensagens brutas. Mesmo mensagens JSON aparentemente válidas são
reconstruídas a partir de códigos conhecidos. Códigos desconhecidos ou dados
legados ilegíveis viram `unknown_error`, sem ecoar o valor original.

## Persistência e testes

Não há migração nova. O painel usa as tabelas existentes, incluindo as migrações
de ingestão/inbox que já foram alinhadas no card #14. O banco deve estar em dia.
Os modelos SQL de leitura de ingestão são locais a esta consulta; não alteram o
fluxo de processamento nem dependem do backend de cadastro de obras da main.

Cobertura relacionada a TA21 / TI07:

- Testes HTTP para ADMIN, USER, ausência de token e bloqueio da rota legada.
- Validação de filtros, limites, datas, detalhe inexistente e banco indisponível.
- Sanitização de mensagens, códigos desconhecidos, tentativas e dados legados.
- Testes do cliente frontend para autenticação, filtros, detalhes e erros.
- Integração PostgreSQL + HTTP para as cinco origens, paginação, recuperação,
  dados privados, entrada própria do usuário e verificação de limpeza.

O teste `tests/integration/test_operational_failures.py` exige
`OPERATIONS_TEST_DATABASE_URL`. As escritas fictícias usam uma transação externa
revertida, com verificação da limpeza ao final. Não há chamadas à IA. A collection
administrativa está em `Codigo/BACK/postman/Reflecta-Falhas-Administrativas.postman_collection.json`.


## Reprocessamento — UC33 / #30

`POST /admin/operational-failures/journal/{failure_id}/reprocess` exige ADMIN e
aceita somente a falha mais recente de uma entrada disponível. O detalhe informa
`can_admin_reprocess` e a política `reprocess`. Após confirmação, a tela mostra
que a análise entrou na fila e atualiza a lista. Não há reenvio de obras ou eventos
por essa operação. A cota do usuário não é reiniciada.
Consulte `Documentacao/reprocessamento-controlado.md` para a regra completa.
