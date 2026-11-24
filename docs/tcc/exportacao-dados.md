# Exportação dos dados do titular — UC07

O usuário autenticado pode baixar uma cópia dos dados mantidos pelo Reflecta em
“Perfil e privacidade”. A exportação é diferente do compartilhamento de uma
análise com profissional: ela é destinada ao próprio titular, contém o conjunto
dos seus dados e não cria link público.

## Formatos

- **ZIP**: formato recomendado para pessoas. Contém `manifest.json`, informações
  do perfil, reflexões e análises, análises contextuais, compartilhamentos,
  orientações, um arquivo explicativo e a foto de perfil quando disponível.
- **JSON**: documento autocontido para portabilidade. Quando existe foto, o
  conteúdo é representado em Base64 junto de seu tipo MIME.

Os dois formatos usam UTF-8, datas ISO 8601 e o mesmo `schema_version`. O ZIP é
apenas uma apresentação separada do mesmo conjunto lógico de dados.

## API

```http
GET /account/data-export?format=zip
Authorization: Bearer <access-token>
```

`format` aceita `zip` ou `json` e usa `zip` por padrão. A resposta possui
`Content-Disposition: attachment`, `Cache-Control: no-store`,
`Pragma: no-cache` e `X-Content-Type-Options: nosniff`.

O endpoint é síncrono porque o volume esperado no TCC é pequeno e a operação é
rara. Nenhuma fila, worker, migration ou chamada ao provedor de IA participa do
fluxo. O arquivo é construído em memória e não permanece no S3 ou no banco.

## Dados incluídos

- dados cadastrais e metadados não secretos da conta;
- entradas ativas e logicamente excluídas que ainda estejam armazenadas;
- análises individuais, frases, temas e passagens associadas;
- análises contextuais de períodos;
- snapshots e metadados dos compartilhamentos criados pelo titular;
- atividades e reflexões guiadas recebidas;
- foto de perfil, quando o objeto estiver disponível no S3.

Se apenas a foto estiver indisponível, os demais dados ainda são entregues e o
`manifest` registra um aviso. A exportação não contém URL pré-assinada, pois ela
expiraria e não representaria uma cópia portável.

## Dados deliberadamente excluídos

- senha e hash da senha;
- access token, refresh token, sessões e hash de token de compartilhamento;
- códigos de verificação, recuperação, exclusão e redefinição de senha;
- embeddings e configurações internas do processamento;
- outbox, inbox, logs e falhas operacionais;
- catálogo global de obras, temas e passagens não relacionado às análises.

O módulo `data_export` apenas orquestra capacidades públicas de Auth, Journal e
Sharing. Cada módulo continua responsável por selecionar e sanitizar os dados
que possui.
