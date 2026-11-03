# Diagnóstico administrativo e reprocessamento

Os motivos técnicos das falhas são exclusivos de administradores. O usuário comum
consulta apenas o estado da própria análise e pode solicitar nova tentativa.

## Usuário: consultar estado e reenviar

Importe `Reflecta-Journal-Reprocessamento.postman_collection.json` e selecione o
environment Reflecta Local. Faça login, preencha `journalId`, consulte o estado e,
se for `analysis_failed`, solicite reprocessamento. A collection não consulta motivos.

- `GET /journal/entries/{journalId}/analysis`: estado e resultado do proprietário.
- `POST /journal/entries/{journalId}/analysis`: nova tentativa com body `{"expected_revision": "reprocess.revision obtida no GET"}`, retorna 202.
- Entradas analisadas retornam 409 ao solicitar novamente.
- Repetir o envio de uma entrada pendente não duplica a fila.

## Administrador: consultar diagnósticos

Acesse `/deshboard/falhas` com uma conta ADMIN ou importe a collection
`Reflecta-Falhas-Administrativas.postman_collection.json`. Use token de administrador.

```sh
curl --request GET '{{baseUrl}}/admin/operational-failures?source=journal&entity_id={{journalId}}&limit=20&offset=0' \
  --header 'Authorization: Bearer {{accessToken}}'
```

```sh
curl --request GET '{{baseUrl}}/admin/operational-failures/journal/{{failureId}}' \
  --header 'Authorization: Bearer {{accessToken}}'
```

Lista e detalhe exigem ADMIN. O endpoint legado
`GET /journal/entries/{journalId}/analysis/failures` também exige ADMIN e retorna
a listagem administrativa filtrada pela entrada, sem exigir propriedade.
Usuários comuns recebem 403 inclusive para entradas próprias.

A listagem aceita origem, estado atual, identificador do registro/evento e período
com fuso horário (`since` / `until`), além de `limit` (1–100) e `offset` (>=0).
As mensagens são reconstruídas de códigos conhecidos. Conteúdo do diário, título,
e-mail, token, payload de evento, mensagens brutas e dados do armazenamento não
são retornados. Diagnósticos legados ou desconhecidos retornam `unknown_error`.

O usuário tem até três solicitações de reprocessamento por entrada. A análise
inicial e repetições internas do worker não contam. Após a terceira falha, novas
solicitações do usuário retornam 403. Uma revisão antiga retorna 409 sem consumir
cota. A collection captura `analysisRevision` no passo 1.

Administradores podem confirmar uma nova tentativa nos detalhes da falha mais
recente ou usar `POST /admin/operational-failures/journal/{failureId}/reprocess`.
A operação retorna 202 e não reinicia a cota do usuário.

## Novos temas

`Reflecta-Novos-Temas.json` contém o body de um lote de temas para
`POST /catalog/themes`, que também exige ADMIN. Não reenviar indiscriminadamente.
