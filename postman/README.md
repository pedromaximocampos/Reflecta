# Teste do fluxo de análise do diário no Postman

Importe os dois arquivos pelo botão **Import** do Postman:

- `Reflecta-Journal-IA.postman_collection.json`
- `Reflecta-Local.postman_environment.json`

Selecione o environment **Reflecta Local — análise do journal** e preencha `email`
e `password` com uma conta existente. A URL padrão é `http://localhost:8000`.
Mantenha senha e token apenas nos valores locais do Postman, sem compartilhá-los.

## Ordem das chamadas

| Passo | Chamada | Resultado |
| --- | --- | --- |
| 0 | Fazer login | Salva `accessToken`; HTTP Basic, sem body |
| 1 | Criar entrada de diário | Salva `journalId`; entrada em `draft` |
| 2 | Solicitar análise de IA usando journalId | HTTP 202 e `pending_analysis`; sem body |
| 3 | Consultar andamento | Repita enquanto `pending_analysis` |
| 4 | Visualizar retorno final | Confere `analyzed`, resumo, interpretação, sentimentos, tom e frases; salva `analysisId` |
| 5 | Conferir entrada persistida | Confirma `analyzed` na entrada original |

Os passos 1–5 herdam Bearer `{{accessToken}}`. O passo 0 usa Basic Authentication.
IDs e token são capturados automaticamente; não é necessário copiar respostas.

### Envio manual

Execute na ordem usando **Send**. No passo 3, observe `status` e repita a consulta
até `analyzed`. Depois execute 4 e 5. Abra **Body → Pretty → JSON** para visualizar
os dados da análise e **Test Results** para ver as verificações.

### Collection Runner

Execute a collection inteira, com **uma iteração** e o environment selecionado.
O passo 3 consulta a cada `pollIntervalMs` (5.000 ms) até `maxPollAttempts` (24
consultas). Ao concluir, segue para 4 e 5. O controle de próxima chamada funciona
no Runner; o botão Send não executa automaticamente as outras chamadas.

Em `analysis_failed`, erro HTTP ou limite de consultas, a execução é interrompida.
O limite de espera não prova falha da IA: o worker pode estar parado ou a fila
ocupada. Para consultar novamente manualmente, use o passo 3. Para reiniciar a
contagem, defina `pollCount=0`.

Se a entrada estiver em `analysis_failed`, execute o passo 2 novamente e depois o
3. Não use o passo 1 se quiser repetir a análise da mesma entrada. Uma entrada já
`analyzed` não pode ser reenviada por este fluxo: para outro teste, crie uma nova.

## Pré-requisitos e observações

- API, PostgreSQL, Neo4j e worker `src.modules.ai_processing.worker` em execução.
- Provedor configurado em `.env.ai.local` no backend.
- A entrada fictícia criada fica no histórico do usuário. Cada nova execução do
  passo 1 cria outra entrada; cada solicitação processada pode consumir a API de IA.
- Use até 20.000 caracteres. Novas entradas entram automaticamente na fila de análise.
- A resposta pode conter temas vazios, o que é válido. Associações dependem dos
  temas ativos e do relato; não se compara a resposta da IA com um texto fixo.
- A API exige proprietário autenticado. Esta collection não exige papel ADMIN.
- As falhas antigas não possuem diagnóstico retroativo. As novas falhas tratadas
  pelo worker são registradas em `journal_schema.analysis.analysis_error`.
- A consulta do resultado não retorna diagnóstico detalhado. Motivos técnicos são
  exclusivos de ADMIN em `/admin/operational-failures` e no painel `/deshboard/falhas`.

A explicação detalhada do processamento está em
`Documentacao/fluxo-analise-journal.md` na raiz do repositório.

## Consultar falhas e reenviar uma análise

Importe a collection separada `Reflecta-Journal-Reprocessamento.postman_collection.json`.
Use o mesmo environment e preencha `journalId` da entrada com falha.
Consulte o passo a passo e os cURLs em `Diagnostico-e-Reprocessamento.md`.
A collection do proprietário consulta apenas estado e resultado. Para diagnósticos,
use uma conta ADMIN e a collection `Reflecta-Falhas-Administrativas.postman_collection.json`.
O endpoint legado `/analysis/failures` agora recusa usuários comuns com 403.
