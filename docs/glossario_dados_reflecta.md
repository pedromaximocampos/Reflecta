# Glossário de Dados — Reflecta

Este documento apresenta o glossário de dados do sistema Reflecta, considerando a organização atual em **monólito modular** com persistência híbrida entre **PostgreSQL** e **Neo4j**.

O PostgreSQL é utilizado para armazenar os dados transacionais, sensíveis e operacionais do sistema. Já o Neo4j é utilizado para representar o grafo de conhecimento, responsável por relacionar temas, passagens, obras e autores.

---

## 1. Visão Geral da Persistência

### PostgreSQL

O PostgreSQL concentra os dados transacionais do Reflecta, separados logicamente por schemas de módulo:

| Schema | Responsabilidade |
|---|---|
| auth_schema | Usuários, credenciais, sessões e recuperação de senha. |
| journal_schema | Entradas de diário, análises, sentenças, temas identificados, passagens associadas e vetores semânticos. |
| recommendation_schema | Itens recomendáveis e recomendações personalizadas. |
| sharing_schema | Compartilhamentos com profissionais e atividades orientadas. |
| event_schema | Outbox, eventos processados, logs de notificação e auditoria. |

### Neo4j

O Neo4j representa o grafo de conhecimento curado do Reflecta:

| Nó | Responsabilidade |
|---|---|
| Theme | Tema utilizado para classificar reflexões e relacionar conteúdos. |
| Passage | Passagem filosófica, literária ou cultural associável a temas. |
| Work | Obra filosófica, literária ou cultural cadastrada no catálogo. |
| Author | Autor associado a uma obra. |

---

## 2. auth_schema

### USERS

Representa o usuário cadastrado no sistema Reflecta.

| Campo | Descrição |
|---|---|
| id | Identificador único do usuário. |
| email | Endereço de e-mail utilizado para autenticação e comunicação. |
| name | Nome do usuário. |
| avatar_url | URL da imagem de perfil do usuário, quando cadastrada. |
| status | Situação atual da conta, como ativa, inativa ou excluída. |
| created_at | Data e hora de criação do usuário. |
| updated_at | Data e hora da última atualização do usuário. |
| last_login_at | Data e hora do último acesso realizado pelo usuário. |

### AUTH_CREDENTIALS

Armazena as credenciais de autenticação do usuário.

| Campo | Descrição |
|---|---|
| user_id | Identificador do usuário associado às credenciais. |
| credential_type | Tipo de autenticação utilizada, como senha local ou provedor externo. |
| password_hash | Hash da senha do usuário. |
| password_salt | Valor utilizado para reforçar a segurança do hash da senha. |
| mfa_enabled | Indica se a autenticação multifator está habilitada. |
| created_at | Data e hora de criação das credenciais. |
| updated_at | Data e hora da última atualização das credenciais. |

### AUTH_SESSIONS

Representa as sessões de acesso ativas ou encerradas do usuário.

| Campo | Descrição |
|---|---|
| id | Identificador único da sessão. |
| user_id | Identificador do usuário associado à sessão. |
| issued_at | Data e hora em que a sessão foi criada. |
| expires_at | Data e hora de expiração da sessão. |
| revoked_at | Data e hora em que a sessão foi revogada, quando aplicável. |
| ip | Endereço IP utilizado no acesso. |
| user_agent | Informações do navegador ou dispositivo utilizado. |

### PASSWORD_RESETS

Controla solicitações de redefinição de senha.

| Campo | Descrição |
|---|---|
| id | Identificador único da solicitação. |
| user_id | Identificador do usuário que solicitou a redefinição. |
| token_hash | Hash do token de redefinição de senha. |
| expires_at | Data e hora de expiração do token. |
| used_at | Data e hora em que o token foi utilizado. |
| created_at | Data e hora de criação da solicitação. |

---

## 3. journal_schema

### JOURNAL_ENTRIES

Representa uma entrada textual criada pelo usuário no diário do Reflecta.

| Campo | Descrição |
|---|---|
| id | Identificador único da entrada de diário. |
| user_id | Identificador do usuário dono da entrada. |
| title | Título opcional da reflexão. |
| content_text | Texto da reflexão registrada pelo usuário. |
| context_tags | Tags ou informações contextuais associadas à entrada, como domínio, local ou pessoas mencionadas. |
| status | Estado da entrada, como pending_analysis, analyzed ou analysis_failed. |
| created_at | Data e hora de criação da entrada. |
| updated_at | Data e hora da última atualização da entrada. |
| deleted_at | Data e hora de exclusão lógica da entrada, quando aplicável. |

### ANALYSIS

Armazena o resultado da análise textual realizada pela IA sobre uma entrada de diário.

| Campo | Descrição |
|---|---|
| id | Identificador único da análise. |
| journal_entry_id | Identificador da entrada de diário analisada. |
| summary | Resumo gerado a partir da reflexão textual. |
| main_message | Mensagem central ou interpretação principal da análise. |
| content_meta | Metadados estruturados da análise, como temas, padrões, práticas sugeridas ou informações complementares. |
| status | Estado da análise, como concluída, pendente ou com falha. |
| analyzed_at | Data e hora em que a análise foi concluída. |
| analysis_error | Descrição do erro ocorrido durante o processamento, quando houver. |
| created_at | Data e hora de criação do registro de análise. |
| updated_at | Data e hora da última atualização da análise. |

### JOURNAL_SENTENCES

Representa as sentenças extraídas de uma entrada textual.

| Campo | Descrição |
|---|---|
| id | Identificador único da sentença. |
| journal_entry_id | Identificador da entrada de diário de origem. |
| analysis_id | Identificador da análise associada. |
| sentence_index | Posição da sentença dentro do texto original. |
| sentence_text | Texto da sentença extraída. |
| start_offset | Posição inicial da sentença no texto original. |
| end_offset | Posição final da sentença no texto original. |
| created_at | Data e hora de criação do registro. |

### SENTENCE_THEMES

Relaciona sentenças do diário com temas identificados pela IA ou confirmados pelo usuário.

| Campo | Descrição |
|---|---|
| sentence_id | Identificador da sentença analisada. |
| theme_id | Identificador lógico do tema correspondente no Neo4j. |
| theme_slug | Identificador textual único do tema. |
| confidence | Grau de confiança da associação entre sentença e tema. |
| source | Origem da associação, como IA, usuário ou regra interna. |
| confirmed_by_user | Indica se o tema foi confirmado pelo usuário. |
| created_at | Data e hora de criação da associação. |

### SENTENCE_PASSAGES

Relaciona uma sentença do diário a uma passagem do grafo de conhecimento.

| Campo | Descrição |
|---|---|
| id | Identificador único da associação. |
| sentence_id | Identificador da sentença associada. |
| passage_id | Identificador lógico da passagem armazenada no Neo4j. |
| confidence | Grau de confiança da associação entre sentença e passagem. |
| reason | Justificativa textual da associação. |
| payload_snapshot | Cópia dos dados relevantes da passagem no momento da associação. |
| created_at | Data e hora de criação da associação. |

### ENTRY_EMBEDDINGS

Armazena o vetor semântico de uma entrada de diário.

| Campo | Descrição |
|---|---|
| entry_id | Identificador da entrada de diário associada. |
| embedding | Vetor semântico da entrada textual. |
| model_name | Nome ou versão do modelo utilizado para gerar o vetor. |
| created_at | Data e hora de criação do vetor. |

### SENTENCE_EMBEDDINGS

Armazena o vetor semântico de uma sentença específica.

| Campo | Descrição |
|---|---|
| sentence_id | Identificador da sentença associada. |
| embedding | Vetor semântico da sentença. |
| model_name | Nome ou versão do modelo utilizado para gerar o vetor. |
| created_at | Data e hora de criação do vetor. |

---

## 4. recommendation_schema

### RECOMMENDATION_ITEMS

Representa um conteúdo recomendável cadastrado ou disponibilizado pelo sistema.

| Campo | Descrição |
|---|---|
| id | Identificador único do item recomendável. |
| title | Título do conteúdo recomendado. |
| type | Tipo do conteúdo, como livro, filme, prática, obra ou referência cultural. |
| description | Descrição do item recomendável. |
| image_url | URL da imagem associada ao conteúdo, quando houver. |
| external_url | Link externo relacionado ao conteúdo, quando houver. |
| status | Estado do item, como ativo, inativo ou em revisão. |
| metadata | Dados complementares do item recomendável. |
| created_at | Data e hora de criação do item. |
| updated_at | Data e hora da última atualização do item. |

### RECOMMENDATIONS

Representa uma recomendação personalizada gerada para um usuário.

| Campo | Descrição |
|---|---|
| id | Identificador único da recomendação. |
| user_id | Identificador do usuário que recebeu a recomendação. |
| journal_entry_id | Identificador da entrada de diário relacionada, quando aplicável. |
| recommendation_item_id | Identificador do item recomendável sugerido. |
| reason | Justificativa da recomendação. |
| source_themes | Temas utilizados como base para geração da recomendação. |
| status | Estado da recomendação, como disponível, visualizada ou salva. |
| created_at | Data e hora de criação da recomendação. |
| viewed_at | Data e hora em que a recomendação foi visualizada. |
| saved_at | Data e hora em que a recomendação foi salva pelo usuário. |

---

## 5. sharing_schema

### SHARED_EXPORTS

Representa uma página ou pacote de exportação compartilhado com um profissional de saúde.

| Campo | Descrição |
|---|---|
| id | Identificador único da exportação compartilhada. |
| user_id | Identificador do usuário que gerou o compartilhamento. |
| token_hash | Hash do token de acesso à página de exportação. |
| s3_url | URL do arquivo ou página exportada no S3. |
| period_start | Data inicial do período compartilhado. |
| period_end | Data final do período compartilhado. |
| permissions | Permissões e escopo dos dados autorizados pelo usuário. |
| status | Estado do compartilhamento, como ativo, expirado ou revogado. |
| expires_at | Data e hora de expiração do acesso. |
| created_at | Data e hora de criação do compartilhamento. |
| revoked_at | Data e hora de revogação do compartilhamento, quando aplicável. |

### PROFESSIONAL_ACTIVITIES

Representa uma atividade ou reflexão guiada sugerida pelo profissional de saúde.

| Campo | Descrição |
|---|---|
| id | Identificador único da atividade. |
| shared_export_id | Identificador do compartilhamento que originou a atividade. |
| user_id | Identificador do usuário que recebeu a atividade. |
| title | Título da atividade ou reflexão guiada. |
| description | Descrição da atividade sugerida. |
| status | Estado da atividade, como pendente ou concluída. |
| created_at | Data e hora de criação da atividade. |
| completed_at | Data e hora de conclusão da atividade, quando aplicável. |

---

## 6. event_schema

### OUTBOX_EVENTS

Armazena eventos internos gerados pelos módulos do monólito modular.

| Campo | Descrição |
|---|---|
| id | Identificador único do evento. |
| event_type | Tipo do evento interno. |
| aggregate_type | Tipo da entidade relacionada ao evento. |
| aggregate_id | Identificador da entidade relacionada ao evento. |
| payload | Dados do evento em formato estruturado. |
| status | Estado do evento, como pendente, processado ou falho. |
| attempts | Número de tentativas de processamento. |
| next_attempt_at | Data e hora da próxima tentativa de processamento. |
| last_error | Último erro ocorrido durante o processamento. |
| created_at | Data e hora de criação do evento. |
| processed_at | Data e hora de processamento do evento. |

### PROCESSED_EVENTS

Controla eventos já processados pelos consumidores internos, garantindo idempotência.

| Campo | Descrição |
|---|---|
| event_id | Identificador do evento processado. |
| consumer_name | Nome do consumidor ou worker responsável pelo processamento. |
| processed_at | Data e hora em que o evento foi processado. |

### NOTIFICATION_LOGS

Registra tentativas de envio de notificações.

| Campo | Descrição |
|---|---|
| id | Identificador único do log de notificação. |
| user_id | Identificador do usuário associado à notificação, quando aplicável. |
| event_id | Identificador do evento que originou a notificação. |
| channel | Canal de envio utilizado, como e-mail. |
| recipient | Destinatário da notificação. |
| template | Template utilizado na mensagem. |
| status | Estado da notificação, como enviada ou com falha. |
| error | Descrição do erro ocorrido no envio, quando houver. |
| sent_at | Data e hora de envio da notificação. |
| created_at | Data e hora de criação do log. |

### AUDIT_LOGS

Registra ações relevantes para rastreabilidade e auditoria.

| Campo | Descrição |
|---|---|
| id | Identificador único do registro de auditoria. |
| user_id | Identificador do usuário associado à ação, quando aplicável. |
| action | Ação realizada no sistema. |
| entity_type | Tipo da entidade afetada. |
| entity_id | Identificador da entidade afetada. |
| details | Detalhes adicionais da ação, sem armazenar conteúdo sensível. |
| created_at | Data e hora do registro da ação. |

---

## 7. Grafo de Conhecimento — Neo4j

### Theme

Representa um tema utilizado pelo Reflecta para classificar reflexões e relacionar conteúdos.

| Campo | Descrição |
|---|---|
| theme_id | Identificador único do tema. |
| slug | Identificador textual único do tema. |
| label | Nome de exibição do tema. |
| description | Descrição do significado do tema. |
| is_active | Indica se o tema está ativo para uso pela IA. |
| created_at | Data e hora de criação do tema. |
| updated_at | Data e hora da última atualização do tema. |

### Passage

Representa uma passagem filosófica, literária ou cultural utilizada como referência contextual.

| Campo | Descrição |
|---|---|
| passage_id | Identificador único da passagem. |
| locator | Localização da passagem na obra, como capítulo, página ou seção. |
| short_text | Texto curto ou trecho representativo da passagem. |
| paraphrase | Paráfrase da passagem, quando necessário. |
| interpretation_note | Nota interpretativa sobre o significado da passagem. |
| status | Estado da passagem, como pendente, aprovada ou rejeitada. |
| priority | Prioridade de uso da passagem nas associações. |
| created_at | Data e hora de criação da passagem. |
| updated_at | Data e hora da última atualização da passagem. |

### Work

Representa uma obra filosófica, literária ou cultural cadastrada no catálogo.

| Campo | Descrição |
|---|---|
| work_id | Identificador único da obra. |
| slug | Identificador textual único da obra. |
| title | Título da obra. |
| synopsis | Sinopse ou descrição da obra. |
| type | Tipo da obra, como livro, filme, artigo ou conteúdo cultural. |
| language | Idioma da obra. |
| cover_image_url | URL da imagem de capa armazenada no S3. |
| source_file_url | URL do arquivo da obra, quando houver. |
| status | Estado da obra, como ativa, em processamento ou em revisão. |
| created_at | Data e hora de criação da obra. |
| updated_at | Data e hora da última atualização da obra. |

### Author

Representa o autor de uma obra cadastrada no catálogo.

| Campo | Descrição |
|---|---|
| author_id | Identificador único do autor. |
| name | Nome do autor. |
| normalized_name | Nome normalizado para evitar duplicidade. |
| description | Breve descrição do autor. |
| created_at | Data e hora de criação do autor. |
| updated_at | Data e hora da última atualização do autor. |

---

## 8. Relacionamentos do Grafo Neo4j

| Relacionamento | Descrição |
|---|---|
| Passage RELATES_TO Theme | Indica que uma passagem está associada a um ou mais temas. |
| Passage BELONGS_TO Work | Indica que uma passagem pertence a uma obra. |
| Work WRITTEN_BY Author | Indica que uma obra foi escrita ou produzida por um autor. |

---

## 9. Observações sobre Persistência Híbrida

O PostgreSQL é utilizado para armazenar dados transacionais, sensíveis e operacionais do Reflecta, como usuários, entradas de diário, análises, recomendações, compartilhamentos e eventos internos.

O Neo4j é utilizado para armazenar o grafo de conhecimento curado, permitindo representar relações entre temas, passagens, obras e autores de forma mais natural.

As tabelas `SENTENCE_THEMES`, `SENTENCE_PASSAGES` e `RECOMMENDATION_ITEMS` podem armazenar referências lógicas para elementos do Neo4j. Essas referências não são chaves estrangeiras relacionais, mas identificadores utilizados pela aplicação para conectar dados transacionais do PostgreSQL ao grafo de conhecimento.

As entradas privadas do journaling permanecem armazenadas no PostgreSQL e não são replicadas para o Neo4j.
