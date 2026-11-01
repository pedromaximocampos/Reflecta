# Backend do Reflecta

## Parâmetros da IA e reprocessamento administrativo

Os padrões do ambiente local ficam em `.env.ai.local`, ignorado pelo Git.
O exemplo versionado utiliza `gpt-6-luna`, timeout de 60 segundos, máximo de
12.000 tokens de saída e esforço `low`.
A chave `OPENAI_API_KEY` é configurada somente no servidor.

Em **Falhas operacionais → Ver detalhes → Solicitar reprocessamento**, um
administrador pode escolher modelo, timeout (1–600 segundos), tokens de saída
(1–128.000) e esforço de raciocínio para aquela tentativa. O modelo deve estar
habilitado na conta e aceitar os parâmetros escolhidos.

- `GET /admin/operational-failures/analysis-settings` retorna os quatro parâmetros
  padrão, sem a chave, e exige ADMIN.
- `POST /admin/operational-failures/journal/{failure_id}/reprocess` aceita esses
  parâmetros em JSON (`model`, `timeout_seconds`, `max_output_tokens`,
  `reasoning_effort`). Sem body, usa os padrões atuais.
- A configuração fica na solicitação de auditoria e na entrada enquanto estiver
  pendente. O worker instancia um provedor para essa tentativa, incluindo o timeout
  da aplicação e a seleção de passagens, sem alterar o provedor das outras entradas.
- Solicitações duplicadas enquanto a análise estiver pendente não substituem os
  parâmetros nem criam outra tentativa. O limite de três pedidos do usuário permanece.
- A migration `d8c51a700003` une as linhas de compartilhamento e avatar e adiciona
  as colunas JSONB. Execute `alembic upgrade head` antes de iniciar a versão nova.

O backend do Reflecta será desenvolvido como uma única aplicação organizada em
módulos internos. Esta estrutura não representa uma arquitetura de
microserviços.

## Módulos

- `Auth`: autenticação e gerenciamento de conta.
- `Journal`: entradas de diário e histórico de reflexões.
- `AIProcessing`: interpretação e processamento de textos.
- `CatalogKnowledge`: catálogo de temas, obras e referências.
- `Recommendation`: recomendações culturais, leituras e práticas.
- `SharingProfessional`: compartilhamento e fluxos do profissional.
- `Notification`: notificações geradas pelos fluxos internos.
- `InternalEvents`: contratos e despacho de eventos entre módulos.

Os módulos são implementados incrementalmente nas respectivas entregas.

O Catalog já expõe o CRUD administrativo de temas e passagens, a criação de
obras e a solicitação de ingestão de PDF. O fluxo persiste o documento no S3,
publica o evento por Outbox/SNS/SQS e o módulo `AIProcessing` processa chunks
retomáveis. As sugestões da IA são validadas contra o texto original e os temas
ativos antes de o Catalog persistir passagens `PENDING_REVIEW` no Neo4j. O
administrador pode então ajustar o conteúdo e os temas, aprovar ou rejeitar a
sugestão, ativá-la ou desativá-la e removê-la logicamente.

## Worker de ingestão de obras

1. Copie `.env.ai.example` para `.env.ai.local` e preencha
   `OPENAI_API_KEY` e `OPENAI_MODEL`. O arquivo local é ignorado pelo Git.
2. Autentique o profile AWS restrito usado no `.env.dev`:

```powershell
aws sso login --profile reflecta-dev
```

3. Para executar diretamente no ambiente criado pelo `uv`:

```powershell
uv run python -m src.modules.ai_processing.bootstrap.workers.sqs.work_ingestion
```

4. Para executar o mesmo worker no Docker, a pasta local `.aws` é montada como
   somente leitura; nenhuma credencial é copiada para a imagem:

```powershell
docker compose -f docker-compose.api_workers.yml --profile ai up -d --build worker_work_ingestion
docker logs -f individuum-worker-work-ingestion
```

O worker valida a configuração OpenAI antes de iniciar o polling do SQS. Portanto,
uma chave ou um modelo ausente encerra a inicialização sem consumir a mensagem.
Em AWS, remova `AWS_PROFILE` e utilize uma IAM role em vez de arquivos locais.

Um teste isolado faz uma única chamada paga com texto fictício, sem acessar S3,
SQS, PostgreSQL ou Neo4j:

```powershell
uv run python -m src.modules.ai_processing.smoke_test_work_passages
```

O núcleo interno de interpretação textual (UC19), seu contrato e as pendências
de configuração do provedor de IA estão documentados em [docs/uc19.md](docs/uc19.md).

## Cor dos temas

Os endpoints de listagem e consulta de `/catalog/themes` retornam `color` em
hexadecimal `#RRGGBB`. A cor é gerada automaticamente pelo backend com saturação
alta e não pode ser escolhida ou editada pelo administrador. O contrato ainda
tolera e ignora `color` em requisições antigas de criação/edição, inclusive se o
valor vier vazio ou nulo.

A propriedade é persistida no nó `Theme` do Neo4j e protegida pela constraint
`theme_color_unique`. Para reparar uma base anterior e criar a constraint, execute:

```powershell
uv run python -m src.modules.catalog.infrastructure.persistence.neo4j.backfill_theme_colors
```

O comando é idempotente: mantém cores válidas e exclusivas e substitui apenas
cores ausentes, inválidas ou repetidas. Temas antigos ainda usam `#8B5CF6` apenas
como fallback temporário de leitura antes da migração.

A interpretação de IA apenas correlaciona frases a temas ativos já cadastrados,
sem criar ou modificar temas. As análises novas guardam a cor do catálogo no
snapshot de metadados, e cada associação retornada em `analysis.sentences` inclui
essa cor. Alterações posteriores na cor não reescrevem análises históricas.

## Diagnóstico de falhas da análise do diário

Quando o worker encerra uma análise com falha, ele grava uma linha em
`journal_schema.analysis` com `status = 'failed'`. O campo existente
`analysis_error` contém JSON com `code`, `message` e `attempts` (quantidade de
execuções do caso de uso nesse ciclo do worker). `created_at` registra a data.
Não é necessária uma nova migration.

O código distingue timeout, rede, autenticação, permissão, recurso/modelo não
encontrado, quota, limite de requisições, parâmetros inválidos, indisponibilidade,
resposta incompleta/recusada/inválida, temas ou segmentação inválidos, alteração do
catálogo, entrada inválida e erros dos bancos. Erros não classificados recebem
`unexpected_error`. Mensagens são fixas: não são persistidos o texto da reflexão,
respostas brutas do provedor, credenciais ou strings de exceções.

Exemplo de `analysis_error`:

```json
{"code":"provider_timeout","message":"O provedor excedeu o tempo limite da análise.","attempts":1}
```

Consulta para diagnóstico:

```sql
SELECT id, journal_entry_id, created_at,
       analysis_error::jsonb ->> 'code' AS error_code,
       analysis_error::jsonb ->> 'message' AS error_message,
       analysis_error::jsonb ->> 'attempts' AS attempts
FROM journal_schema.analysis
WHERE status = 'failed'
ORDER BY created_at DESC;
```

O registro e a transição da entrada para `analysis_failed` são atômicos. Um worker
com snapshot antigo não adiciona uma falha à entrada atualizada. Solicitar
novamente e concluir com sucesso preserva as falhas anteriores; a consulta pública
da análise continua retornando apenas resultados `completed`.

Falhas anteriores à implementação não recebem causas retroativas. Falhas de
inicialização/configuração do worker, cancelamentos e conflitos não são registradas
como análises fracassadas. Se o próprio banco estiver indisponível, não é possível
garantir a gravação do diagnóstico. A política de retry permanece inalterada.

### Consultar falhas por HTTP

`GET /journal/entries/{journal_entry_id}/analysis/failures?limit=20` retorna
`entry_id`, `status`, `can_reprocess` e `failures` (do mais recente ao mais antigo).
Cada falha inclui `id`, `code`, `message`, `attempts` e `failed_at`.
O limite aceita 1 a 100. Exige Bearer do proprietário; não há acesso cruzado por
papel ADMIN. Entradas inexistentes, excluídas ou de outro usuário retornam 404.
Falhas antigas sem registro retornam histórico vazio.

Para uma entrada em `analysis_failed`, reenvie
`POST /journal/entries/{journal_entry_id}/analysis`, sem body. Retorna 202 e preserva
os diagnósticos anteriores. Entradas já `analyzed` retornam 409.
A collection `postman/Reflecta-Journal-Reprocessamento.postman_collection.json`
separa esse fluxo do teste de criação. Veja os cURLs em
`postman/Diagnostico-e-Reprocessamento.md`.
