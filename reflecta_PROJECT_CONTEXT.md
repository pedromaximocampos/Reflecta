# Reflecta - Project Context

> Documento de contexto técnico e de produto para desenvolvimento assistido por IA.
>
> **Objetivo:** permitir que qualquer pessoa ou agente de IA que abra o repositório entenda o que o Reflecta é, quais decisões já foram tomadas, quais artefatos são fontes de referência, quais limites arquiteturais devem ser respeitados, quais pontos ainda estão em aberto e como evoluir a implementação sem reescrever o projeto com base em suposições.

---

## 0. Como este documento deve ser interpretado

Este arquivo é uma **fonte de contexto consolidada**, não uma prova automática de que tudo descrito aqui já está implementado no código.

Existem três categorias de informação neste projeto:

1. **Decisão vigente** - deve ser preservada durante a implementação, salvo decisão explícita em contrário.
2. **Modelo/documentação vigente a validar no código** - faz parte do projeto atual, mas a implementação precisa ser conferida no repositório.
3. **Ponto em aberto/inconsistência conhecida** - não deve ser resolvido silenciosamente por uma IA. Deve ser analisado e, se a solução alterar contrato, domínio, persistência ou arquitetura, documentado antes da mudança.

### Regra central

**Nunca assumir que um item documentado já existe no código.**

Ao iniciar uma tarefa, a IA deve comparar:

`PROJECT_CONTEXT.md -> AGENTS.md -> IMPLEMENTATION_STATUS.md -> código/migrations/testes -> diagramas/documentação relevante`

Se o código contradizer a documentação, não escolher um lado silenciosamente. Identificar a divergência e verificar se o código representa uma decisão mais nova ou uma implementação incompleta.

---

# 1. Identidade do projeto

## 1.1 Nome atual

**Reflecta**.

O material conceitual mais antigo utilizava o nome **Individuum** e chamava a IA de **Sophia**. Esses nomes pertencem à evolução histórica do produto e não devem ser reintroduzidos automaticamente no código, interfaces ou documentação atual.

## 1.2 Natureza do projeto

O Reflecta é simultaneamente:

- um **Trabalho de Conclusão de Curso (TCC) de Engenharia de Software**;
- um sistema que deve ser efetivamente desenvolvido;
- um produto de journaling/reflexão com IA e curadoria de conhecimento.

Por ser um TCC, a implementação deve manter rastreabilidade com os modelos já produzidos: casos de uso, classes, dados, componentes, estados, interfaces e testes.

O código não deve evoluir de forma totalmente independente da documentação acadêmica. Mudanças relevantes de domínio ou arquitetura devem gerar atualização dos artefatos correspondentes.

---

# 2. Visão do produto

## 2.1 Problema

O journaling pode ser útil para reflexão e autoconhecimento, porém a pessoa pode ter dificuldade para:

- manter continuidade;
- aprofundar o que escreveu;
- perceber temas e padrões recorrentes;
- relacionar suas experiências a conhecimentos que ainda não conhece;
- transformar registros isolados em material útil para reflexão futura;
- compartilhar, de maneira controlada, uma síntese com um profissional de saúde.

## 2.2 Proposta atual

O Reflecta oferece um espaço privado de journaling no qual o usuário registra reflexões textuais. A aplicação utiliza IA para analisar semanticamente as entradas e relacioná-las a um catálogo curado de temas, passagens, obras, autores e conteúdos culturais.

O sistema deve permitir que o usuário:

- registre reflexões;
- consulte seu histórico;
- visualize análise produzida pela IA;
- revise/gerencie temas sugeridos;
- receba recomendações culturais;
- visualize referências filosóficas e literárias relacionadas;
- compartilhe uma síntese autorizada com um profissional de saúde;
- receba atividades ou reflexões orientadas pelo profissional por meio desse compartilhamento;
- exporte seus dados;
- gerencie e exclua sua conta.

O sistema também possui funções administrativas para curadoria de temas, obras, autores, passagens e conteúdos recomendáveis.

## 2.3 Diferencial do Reflecta

O diferencial atual não é apenas "diário com IA". O núcleo do produto é a combinação de:

**journaling privado + interpretação estruturada por IA + conhecimento curado + recomendações culturais/filosóficas + compartilhamento controlado com profissional.**

A inteligência artificial deve auxiliar a interpretação e a associação, mas o catálogo de conhecimento funciona como mecanismo de controle e curadoria. A IA não deve inventar livremente todo o conhecimento recomendado quando existe uma base curada destinada a esse propósito.

## 2.4 Posicionamento conceitual herdado

O material inicial do produto enfatizava:

- autoconhecimento;
- filosofia aplicada à vida;
- psicologia simbólica;
- reflexão;
- aprendizado por auto-observação;
- uma experiência introspectiva e humanista.

Esse DNA conceitual continua útil para decisões de UX e produto, mas funcionalidades históricas não presentes no TCC atual não devem ser tratadas como escopo vigente.

---

# 3. Escopo atual e itens fora de escopo

## 3.1 Escopo atual confirmado pelos artefatos recentes

### Usuário final

- criar conta;
- entrar no sistema;
- gerenciar perfil;
- excluir conta;
- exportar conta/dados;
- criar entrada de diário;
- editar entrada de diário;
- excluir entrada de diário;
- visualizar histórico de reflexões;
- visualizar análise da IA;
- gerenciar temas sugeridos pela IA;
- receber recomendações culturais;
- visualizar referências literárias e filosóficas;
- compartilhar síntese com profissional.

### Profissional de saúde

- acessar conteúdo compartilhado por link/token;
- visualizar somente informações autorizadas;
- cadastrar atividade ou reflexão guiada associada ao compartilhamento/usuário.

### Administrador

- acessar área administrativa;
- gerenciar catálogo de temas;
- gerenciar referências filosóficas/literárias;
- gerenciar obras;
- gerenciar autores;
- gerenciar passagens;
- gerenciar recomendações culturais;
- revisar passagens sugeridas pela IA;
- aprovar/rejeitar passagem;
- ajustar temas de uma passagem;
- ajustar conteúdos associados a temas;
- visualizar falhas operacionais;
- solicitar reprocessamento quando aplicável.

### Sistema/IA

- interpretar conteúdo textual;
- construir/atualizar contexto do usuário;
- consultar catálogo de temas ativos;
- produzir saída estruturada validável;
- gerar vetores semânticos quando necessário;
- sugerir leituras e práticas;
- selecionar passagem relacionada ao tema/reflexão;
- explicar associação entre passagem e reflexão;
- processar obra e sugerir passagens candidatas para revisão humana;
- sinalizar falhas de processamento.

## 3.2 Journaling atual é textual

O arquivo `casos de uso usuario-final.puml` registra explicitamente:

> A entrada de diário será textual. Entradas por áudio e imagem foram removidas do escopo atual.

Portanto, **áudio e imagem não fazem parte do escopo atual do journaling**, mesmo que ideias ou documentos históricos mencionem diário multimídia.

Não implementar upload/transcrição/análise de áudio ou imagem sem uma nova decisão explícita.

## 3.3 Ideias históricas que NÃO devem entrar no MVP automaticamente

O documento conceitual antigo do Individuum menciona possibilidades como:

- mini rede social;
- posts/blogs entre usuários;
- comentários;
- plano premium/freemium;
- publicidade;
- múltiplos diários;
- personalização premium;
- caderno de símbolos;
- monetização por livros;
- cursos;
- mentores anunciados;
- WhatsApp/pushs avançados;
- funcionalidades multimídia.

Esses itens representam visão futura/ideação histórica. **Não são requisitos atuais do TCC** e não devem influenciar migrations, entidades ou endpoints do MVP sem aprovação explícita.

---

# 4. Atores e fronteiras de acesso

## 4.1 Usuário Final

É o dono das entradas privadas e das informações derivadas delas.

Regras fundamentais:

- um usuário só pode acessar entradas que lhe pertencem;
- análise, frases, temas, passagens e recomendações derivadas devem respeitar a propriedade da entrada/usuário;
- compartilhamento com profissional exige autorização explícita do usuário;
- exclusão, exportação e revogação devem ser tratadas como operações de domínio relevantes, não como simples detalhes de interface.

## 4.2 Profissional de Saúde

No modelo atual, o profissional acessa uma **Página de Exportação por link/token seguro**. A documentação não estabelece de forma consistente um cadastro/login próprio para esse ator.

Portanto, até existir decisão em contrário:

- não criar automaticamente uma entidade `ProfessionalUser`;
- não exigir login de profissional se o fluxo vigente utiliza token;
- o profissional deve enxergar somente os dados autorizados pelo usuário;
- token expirado/revogado/inválido deve impedir acesso;
- qualquer atividade sugerida deve ser vinculada ao compartilhamento e ao usuário correto.

### Ponto em aberto

A UI/documentação menciona e-mail e identificação do profissional, mas o modelo atual de dados não representa completamente essa identidade. Ver seção de inconsistências.

## 4.3 Administrador

Para o MVP, a permissão administrativa é representada por um único `UserRole` no agregado `User`, com os valores `USER` e `ADMIN`, persistido na coluna `users.role`.

Regras vigentes:

- cadastro público sempre cria `USER`;
- promover ou rebaixar um usuário exige caso de uso administrativo autenticado;
- a autorização deve consultar o papel do usuário, e não confiar em valor enviado pelo cliente;
- uma tabela de permissões granular não faz parte deste incremento e só deve ser introduzida se os requisitos superarem os dois papéis atuais.

A autenticação carrega o papel persistido no Auth a cada request e o propaga por meio de um `AuthenticatedPrincipal`; a camada HTTP disponibiliza um guard `require_role`. O guard já protege o CRUD administrativo de temas; ainda faltam aplicá-lo às futuras rotas administrativas, distinguir access/refresh token e implementar o bootstrap e a alteração administrativa de papel.

## 4.4 Sistema de IA

"Sistema de IA" é ator sistêmico/modelagem de comportamento, não necessariamente um microserviço separado.

No desenho atual, a IA é utilizada pelo **AI Processing Module dentro do monólito modular**, com adaptadores para um provedor externo de LLM/embeddings.

---

# 5. Arquitetura vigente

## 5.1 Estilo de implantação

**Monólito modular.**

Esta é uma decisão importante.

O Reflecta não deve ser transformado em microsserviços por iniciativa da IA.

Características esperadas:

- um backend principal implantável como unidade;
- módulos internos com responsabilidades bem delimitadas;
- separação lógica e de dependências entre módulos;
- schemas PostgreSQL separados por responsabilidade;
- comunicação síncrona entre módulos somente por interfaces explícitas;
- processamento assíncrono interno por eventos, Outbox e workers;
- integrações externas atrás de adapters/ports.

## 5.2 Visão macro

Fluxo geral:

`Atores -> Frontend Web -> API Gateway/BFF -> Backend Reflecta (monólito modular)`

Módulos atuais:

1. Auth Module
2. Journal Module
3. AI Processing Module
4. Catalog / Knowledge Module
5. Recommendation Module
6. Sharing / Professional Module
7. Notification Module
8. Internal Event Dispatcher / Internal Events Module

Persistência/infraestrutura:

- PostgreSQL;
- pgvector/vetores semânticos no PostgreSQL quando utilizados;
- Neo4j;
- Amazon S3;
- Processed Events no PostgreSQL;
- provedor externo de IA/LLM/embeddings;
- Amazon SES para e-mail.

## 5.3 API Gateway/BFF

Os diagramas utilizam a expressão `API Gateway / BFF` como fronteira de entrada do backend.

Não assumir que isso exige um serviço AWS API Gateway separado ou um processo de deployment independente. No estado atual dos artefatos, pode ser uma responsabilidade lógica da camada HTTP/BFF.

A escolha física precisa respeitar a implementação real do repositório.

---

# 6. Clean Architecture + DDD

> **Decisão fornecida para a etapa de desenvolvimento:** o código deve seguir Clean Architecture + princípios de Domain-Driven Design, aplicados dentro do monólito modular.

O objetivo não é criar burocracia arquitetural. É impedir que regras de negócio fiquem presas ao framework, banco, SDK de IA, AWS ou controllers.

## 6.1 Princípio de dependência

Dependências devem apontar para dentro:

`Presentation/Infrastructure -> Application -> Domain`

O domínio não conhece:

- framework web;
- ORM;
- PostgreSQL;
- Neo4j;
- S3;
- SES;
- SDK de LLM;
- biblioteca HTTP;
- detalhes de filas/workers.

## 6.2 Domain Layer

Responsável por:

- entidades;
- value objects;
- invariantes;
- regras de transição de estado;
- políticas puramente de domínio;
- domain events quando fizer sentido;
- contratos de repositório/port quando a linguagem/organização adotada colocar essas abstrações no domínio.

Exemplos do modelo conceitual:

- `User`;
- `JournalEntry`;
- `Analysis`;
- `Recommendation`;
- `SharedExport`;
- `ProfessionalActivity`;
- `OutboxEvent` como modelo operacional/eventual, dependendo da divisão adotada.

Uma entidade não deve ser apenas um DTO anêmico se existe comportamento importante já modelado, por exemplo:

- `JournalEntry.edit(...)`;
- `markPendingAnalysis()`;
- `markAnalyzed()`;
- `markAnalysisFailed()`;
- `delete()`;
- `Recommendation.markViewed()`;
- `Recommendation.save()`;
- `SharedExport.revoke()`;
- `SharedExport.isAccessible()`.

## 6.3 Application Layer

Responsável por casos de uso/orquestração:

- receber comandos/requests independentes de HTTP;
- carregar agregados através de ports;
- invocar regras de domínio;
- coordenar transações;
- interagir com outros módulos por interfaces públicas;
- solicitar persistência;
- publicar evento/outbox quando a operação exige continuação assíncrona.

Exemplos:

- `CreateJournalEntry`;
- `EditJournalEntry`;
- `DeleteJournalEntry`;
- `GetJournalHistory`;
- `GetJournalAnalysis`;
- `ConfirmSuggestedTheme`;
- `CreateSharedExport`;
- `RevokeSharedExport`;
- `SuggestProfessionalActivity`;
- `CreateRecommendation`.

## 6.4 Infrastructure Layer

Implementa detalhes externos:

- repositories PostgreSQL;
- repositories Neo4j;
- ORM/mapeamento;
- migrations;
- S3 adapter;
- SES adapter;
- LLM adapter;
- embedding adapter;
- geração/validação de token;
- workers e scheduler, quando dependentes do framework;
- observabilidade;
- configurações de ambiente.

## 6.5 Presentation / Interface Layer

Responsável por:

- controllers/routes;
- autenticação/autorização de borda;
- serialização e desserialização;
- validação sintática de request;
- mapping para input/output de casos de uso;
- códigos HTTP;
- contratos públicos da API.

Controller não deve executar query direta no banco ou conter regra central do domínio.

## 6.6 Modularidade + DDD

Cada módulo deve ser tratado como uma fronteira de negócio interna.

Regra:

> **Um módulo não acessa diretamente repository/tabela/schema privado de outro módulo.**

Exemplos:

- Recommendation não deve fazer SQL direto em `journal_schema`;
- Sharing não deve fazer SQL direto em tabelas internas de Journal;
- Journal não deve consultar Neo4j diretamente se a consulta pertence ao Catalog / Knowledge Module.

A comunicação deve ocorrer por uma interface pública do módulo, um application service/query port ou por evento interno, conforme a natureza do fluxo.

## 6.7 Estrutura lógica recomendada

A estrutura física precisa ser ajustada à linguagem/framework existentes, mas conceitualmente cada módulo deve se aproximar de:

```text
modules/
  journal/
    domain/
      entities/
      value_objects/
      policies/
      events/
      repositories_or_ports/
    application/
      use_cases/
      commands/
      queries/
      dto/
      ports/
    infrastructure/
      persistence/
      repositories/
      adapters/
    presentation/
      http/
      schemas/

  auth/
  ai_processing/
  catalog/
  recommendation/
  sharing/
  notification/
  internal_events/
```

Não reorganizar todo um repositório existente apenas para reproduzir exatamente essa árvore. Preservar o que já existe quando a mesma separação de responsabilidades puder ser obtida sem refatoração destrutiva.

### 6.7.1 Convenção física adotada no código atual

Para os módulos já iniciados, a raiz física adotada é `src/modules/`:

```text
src/
  modules/
    journal/
      domain/
      application/

    catalog/
      domain/
      application/
      infrastructure/
      presentation/
      bootstrap/
      public/

    auth/
      domain/
      application/
      infrastructure/
      presentation/
      bootstrap/
      public/

    internal_events/
      domain/
      application/
      infrastructure/
      bootstrap/
      public/

    notification/
      domain/
      application/
      infrastructure/
      bootstrap/

  shared/
    config/
    domain/
      errors/
      ports/
    infrastructure/
      persistence/
        mappers/
        postgresql/
      system/
    presentation/

  main/
    server/
```

- `auth.public` contém somente contratos que outros módulos podem referenciar;
- `journal` contém o domínio e o caso de uso embrionário já existentes; persistência, presentation e
  bootstrap só devem ser criados quando houver implementação real nessas camadas;
- `catalog` possui a primeira fatia vertical de CRUD administrativo de temas, com entidade, ports,
  casos de uso, UoW/repository Neo4j, composição e rotas protegidas; as demais entidades do catálogo
  ainda não estão implementadas. O slug é criado a partir do label e permanece estável nas atualizações;
- `catalog.public` será a fronteira de consultas/contratos consumidos por outros módulos e não deve
  expor driver, records ou repositories Neo4j;
- `internal_events` é o proprietário de Outbox, dispatcher, router, retry e contratos de eventos;
- `notification` reage a eventos e contém adapters/consumers de entrega de e-mail;
- `shared` contém somente configuração, contratos e adapters técnicos independentes de bounded context;
- `shared.infrastructure.persistence.mappers` contém apenas o contrato genérico de mapeamento usado
  por adapters de persistência; mappers concretos continuam pertencendo ao módulo e à tecnologia correspondente;
- `shared` não pode importar `modules` nem `main`, e módulos não podem importar `main`;
- `main` continua responsável pela aplicação FastAPI e pela composição final;
- migrations continuam centralizadas em `alembic/`, registrando explicitamente os models dos módulos.

Essa organização física não implica que os casos de uso estejam concluídos; o estado funcional deve ser
registrado somente em `reflecta_IMPLEMENTATION_STATUS.md`.

---

# 7. Responsabilidades dos módulos

## 7.1 Auth Module

Responsável por:

- cadastro;
- autenticação;
- perfil;
- credenciais;
- sessões;
- recuperação de senha;
- exclusão/anonimização coordenada da conta;
- avatar no S3;
- eventos relacionados ao ciclo da conta.

Persistência principal: `auth_schema` no PostgreSQL.

Entidades/modelos documentados:

- USERS;
- AUTH_CREDENTIALS;
- AUTH_SESSIONS;
- PASSWORD_RESETS.

Comportamentos conceituais:

- atualizar perfil;
- marcar usuário como excluído;
- alterar senha;
- revogar sessão;
- verificar expiração de sessão/reset.

### Eventos citados na documentação

- `UserRegistered`;
- `UserAccountDeleted`.

Os nomes devem ser verificados no código antes de serem considerados contrato técnico definitivo.

## 7.2 Journal Module

É o núcleo transacional do journaling.

Componentes documentados:

- Journal Controller;
- Theme Confirmation Controller;
- Journal Application Service;
- Analysis Service;
- Theme Confirmation Service;
- Journal Repository;
- Analysis Repository;
- Sentence Repository;
- Sentence Theme Repository;
- Sentence Passage Repository;
- Embedding Repository;
- Outbox Repository.

Responsabilidades:

- CRUD controlado de entradas;
- propriedade/autorização sobre entrada;
- status de análise;
- persistência de análise;
- decomposição/persistência de sentenças quando o pipeline exigir;
- associações sentença-tema;
- associações sentença-passagem;
- embeddings;
- confirmação/rejeição/ajuste de temas pelo usuário;
- emissão de eventos para análise/reanálise.

Persistência: `journal_schema`.

### Estados de JournalEntry documentados

- DRAFT (presente no diagrama de classes; verificar se será usado no MVP);
- PENDING_ANALYSIS;
- ANALYZED;
- ANALYSIS_FAILED;
- DELETED.

### Estados de Analysis

- PENDING;
- COMPLETED;
- FAILED.

### Eventos citados

- `JournalEntryCreated`;
- `JournalEntryUpdated`;
- `JournalEntryDeleted`;
- `JournalEntryAnalyzed`.

## 7.3 AI Processing Module

Responsável por integrar o domínio com provedores de IA sem permitir que SDK/provider invada os outros módulos.

Responsabilidades documentadas:

- interpretar entrada textual;
- gerar saída estruturada;
- validar saída;
- consultar temas ativos através do módulo apropriado;
- gerar embeddings;
- atualizar contexto semântico do usuário;
- processar conteúdo de obras;
- extrair/sugerir passagens candidatas;
- associar conteúdo do journaling a passagens quando o fluxo exigir;
- registrar/sinalizar falhas.

Integração externa:

- provedor LLM;
- provedor/modelo de embeddings.

Regra:

> A saída do LLM é dado não confiável até ser validada contra schema e regras do sistema.

Temas sugeridos pela IA devem se relacionar ao catálogo de temas ativos; não ampliar silenciosamente o vocabulário controlado criando temas novos sem fluxo administrativo.

## 7.4 Catalog / Knowledge Module

Responsável pelo conhecimento curado.

Componentes documentados:

- Catalog Controller;
- Theme Service;
- Work Service;
- Author Service;
- Passage Service;
- Admin Review Service;
- Knowledge Graph Repository;
- Outbox Repository.

Persistência canônica de conhecimento: **Neo4j**.

Arquivos: **S3** para PDFs/capas.

Nós atuais:

- Theme;
- Passage;
- Work;
- Author.

Relacionamentos atuais:

- `Passage -[:RELATES_TO]-> Theme`;
- `Passage -[:BELONGS_TO]-> Work`;
- `Work -[:WRITTEN_BY]-> Author`.

Regras importantes:

- entradas privadas do usuário não são armazenadas no Neo4j;
- o grafo contém conhecimento curado;
- passagem sugerida pela IA pode exigir revisão humana antes de ficar aprovada/ativa;
- administrador pode aprovar, rejeitar e ajustar associações de temas.

## 7.5 Recommendation Module

Componentes documentados:

- Recommendation Controller;
- Recommendation Worker;
- Recommendation Engine;
- Recommendation Repository;
- Outbox Repository.

Dependências lógicas:

- Journal Module para contexto/temas relevantes;
- Catalog / Knowledge Module para conhecimento e obras.

Persistência: `recommendation_schema` no PostgreSQL.

Responsabilidades:

- gerar/salvar recomendações personalizadas;
- explicar razão da recomendação;
- recuperar recomendações do usuário;
- marcar visualização/salvamento/descarte conforme domínio;
- complementar dados com o catálogo quando necessário.

A recomendação cultural geral não deve ser confundida com uma passagem contextual específica associada a uma sentença/entrada.

## 7.6 Sharing / Professional Module

Componentes documentados:

- Sharing Controller;
- Professional Access Controller;
- Consent Service;
- Share Token Service;
- Export Summary Service;
- Professional Access Service;
- Activity Assignment Service;
- Sharing Repository;
- Activity Repository;
- Consent Repository;
- Outbox Repository.

Persistência atual documentada:

- `sharing_schema`;
- S3 para exportações/sínteses.

Responsabilidades:

- selecionar escopo autorizado;
- validar período/permissões;
- consultar Journal Module para dados autorizados;
- gerar token seguro;
- armazenar somente hash do token quando possível conforme modelo;
- gerar/exportar conteúdo no S3;
- validar acesso profissional;
- revogar/expirar compartilhamento;
- receber atividade sugerida pelo profissional;
- associar atividade ao usuário/exportação;
- emitir evento para notificação.

Evento citado:

- `ProfessionalActivitySuggested`.

## 7.7 Notification Module

Componentes documentados:

- Notification Worker;
- Template Renderer;
- Email Adapter;
- Notification Log Repository.

Integração externa atual:

- Amazon SES.

Persistência/log:

- `NOTIFICATION_LOGS` no modelo atual de `event_schema`.

Responsabilidade:

- reagir a eventos;
- renderizar template;
- enviar e-mail por adapter;
- registrar tentativa/sucesso/falha;
- não transportar regra de negócio central de outros módulos.

## 7.8 Internal Events Module

Componentes documentados:

- Outbox Repository;
- Event Dispatcher;
- Event Router;
- Processed Event Repository.

Workers documentados:

- Journal Analysis Worker;
- Embedding Worker;
- Work Ingestion Worker;
- Reference Matching Worker;
- Recommendation Worker;
- Notification Worker.

Persistência:

- `OUTBOX_EVENTS`;
- `PROCESSED_EVENTS`.

Este mecanismo implementa processamento assíncrono **dentro do monólito modular**.

Decisão atualizada em 2026-08-31 para o fluxo de notificações Auth: o alvo de implantação é
`Outbox PostgreSQL -> dispatcher -> Amazon SQS -> AWS Lambda -> Notification handler -> Amazon SES`.
O handler e os contratos pertencem ao módulo Notification no mesmo repositório; a Lambda é apenas um
entrypoint/adaptador de execução, não um novo bounded context ou autorização para converter o sistema em
microsserviços. RabbitMQ/SMTP permanecem como caminho de transição enquanto o consumer SQS/Lambda e o
adapter SES não estiverem implementados, testados e aptos ao cutover. A extensão dessa escolha para
Journal/IA continua exigindo decisão arquitetural explícita.

---

# 8. Persistência híbrida

## 8.1 PostgreSQL

Responsável pelos dados:

- transacionais;
- privados/sensíveis do journaling;
- operacionais;
- compartilhamentos;
- recomendações geradas;
- eventos internos;
- logs/auditoria.

Schemas atuais:

| Schema | Responsabilidade |
|---|---|
| `auth_schema` | Usuários, credenciais, sessões, reset de senha |
| `journal_schema` | Journaling, análise, sentenças, temas/passagens associados e embeddings |
| `recommendation_schema` | Itens recomendáveis e recomendações personalizadas |
| `sharing_schema` | Compartilhamentos e atividades profissionais |
| `event_schema` | Outbox, processed events, notifications, audit |

## 8.2 pgvector / Vector

Os modelos incluem:

- `ENTRY_EMBEDDINGS.embedding : VECTOR`;
- `SENTENCE_EMBEDDINGS.embedding : VECTOR`.

O uso pressupõe suporte a vetores no PostgreSQL, normalmente através de pgvector, mas a extensão, versão e migration real devem ser confirmadas no repositório antes de codificar.

## 8.3 Neo4j

Responsável exclusivamente pelo grafo de conhecimento curado.

Não armazenar diário privado no grafo.

A ligação PostgreSQL -> Neo4j é feita por **referências lógicas**, não foreign keys relacionais.

Exemplos:

- `SENTENCE_THEMES.theme_id/theme_slug -> Theme`;
- `SENTENCE_PASSAGES.passage_id -> Passage`;
- recommendation item pode conter referência lógica a Work/Theme conforme decisão final do modelo.

## 8.4 Amazon S3

Usos documentados:

- avatar de usuário;
- PDFs de obras;
- capas;
- exportações/sínteses compartilhadas;
- arquivo geral de exportação de conta/dados.

S3 deve ser acessado via adapter/port, não diretamente pelo domínio.

## 8.5 Amazon SES

Uso atual: envio de e-mail.

Exemplos mencionados:

- boas-vindas/confirmação de cadastro;
- notificação de atividade profissional sugerida;
- outros fluxos somente se documentados/necessários.

---

# 9. Modelo de dados atual

Esta seção resume o modelo documentado. O arquivo `glossario_dados_reflecta.md` e `diagrama-der-monolito-postgres-neo4j.puml` contêm o detalhamento dos campos.

## 9.1 auth_schema

### USERS

Campos documentados:

- id UUID PK;
- email unique;
- name;
- avatar_url;
- role (`USER` ou `ADMIN`);
- deleted_at nullable para exclusão lógica;
- created_at;
- updated_at;
- last_login_at.

A decisão vigente de ciclo de vida usa `deleted_at`, sem remoção física neste estágio. E-mail e username continuam globalmente únicos mesmo após exclusão lógica; eventual liberação ou anonimização desses identificadores requer política explícita posterior.

### AUTH_CREDENTIALS

- user_id PK/FK;
- credential_type;
- password_hash;
- password_salt;
- mfa_enabled;
- created_at;
- updated_at.

Observação: o diagrama de classes não mostra `password_salt`, enquanto DER/glossário mostram. O modelo de persistência deve ser conferido no código.

### AUTH_SESSIONS

- id;
- user_id;
- issued_at;
- expires_at;
- revoked_at;
- ip;
- user_agent.

### PASSWORD_RESETS

- id;
- user_id;
- token_hash;
- expires_at;
- used_at;
- created_at.

## 9.2 journal_schema

### JOURNAL_ENTRIES

- id;
- user_id;
- title;
- content_text;
- context_tags JSONB;
- status;
- created_at;
- updated_at;
- deleted_at.

`context_tags` pode guardar contexto estruturado, por exemplo domínio/local/pessoas, mas o schema definitivo do JSON deve ser versionado/validado pela aplicação; não espalhar JSON arbitrário sem contrato.

### ANALYSIS

- id;
- journal_entry_id;
- summary;
- main_message;
- content_meta JSONB;
- status;
- analyzed_at;
- analysis_error;
- created_at;
- updated_at.

### JOURNAL_SENTENCES

- id;
- journal_entry_id;
- analysis_id;
- sentence_index;
- sentence_text;
- start_offset;
- end_offset;
- created_at.

### SENTENCE_THEMES

- sentence_id;
- theme_id lógico Neo4j;
- theme_slug;
- confidence;
- source;
- confirmed_by_user;
- created_at.

### SENTENCE_PASSAGES

- id;
- sentence_id;
- passage_id lógico Neo4j;
- confidence;
- reason;
- payload_snapshot;
- created_at.

O snapshot existe para preservar contexto relevante da associação no momento em que ocorreu, sem transformar o PostgreSQL em fonte canônica da passagem.

### ENTRY_EMBEDDINGS

- entry_id;
- embedding;
- model_name;
- created_at.

### SENTENCE_EMBEDDINGS

- sentence_id;
- embedding;
- model_name;
- created_at.

## 9.3 recommendation_schema

### RECOMMENDATION_ITEMS

- id;
- title;
- type;
- description;
- image_url;
- external_url;
- status;
- metadata JSONB;
- created_at;
- updated_at.

### RECOMMENDATIONS

- id;
- user_id;
- journal_entry_id nullable;
- recommendation_item_id;
- reason;
- source_themes JSONB;
- status;
- created_at;
- viewed_at;
- saved_at.

## 9.4 sharing_schema

### SHARED_EXPORTS

- id;
- user_id;
- token_hash;
- s3_url;
- period_start;
- period_end;
- permissions JSONB;
- status;
- expires_at;
- created_at;
- revoked_at.

### PROFESSIONAL_ACTIVITIES

- id;
- shared_export_id;
- user_id;
- title;
- description;
- status;
- created_at;
- completed_at.

## 9.5 event_schema

### OUTBOX_EVENTS

- id;
- event_type;
- aggregate_type;
- aggregate_id;
- payload JSONB;
- status;
- attempts;
- next_attempt_at;
- last_error;
- created_at;
- processed_at.

Estados conceituais no diagrama de classes:

- PENDING;
- PROCESSING;
- PROCESSED;
- FAILED.

### PROCESSED_EVENTS

- event_id;
- consumer_name;
- processed_at.

### NOTIFICATION_LOGS

- id;
- user_id nullable;
- event_id;
- channel;
- recipient;
- template;
- status;
- error;
- sent_at;
- created_at.

### AUDIT_LOGS

- id;
- user_id nullable;
- action;
- entity_type;
- entity_id;
- details JSONB;
- created_at.

Regra documentada: detalhes de auditoria não devem conter conteúdo sensível do journaling.

---

# 10. Fluxos principais

## 10.1 Criar entrada de diário

Fluxo documentado:

1. usuário autenticado preenche título opcional, texto e contexto/tags;
2. Frontend envia ao BFF/API;
3. Journal Module valida usuário e conteúdo;
4. entrada é salva no PostgreSQL;
5. status inicial é `PENDING_ANALYSIS`;
6. evento `JournalEntryCreated` é registrado/publicado por Outbox;
7. resposta de sucesso não precisa aguardar o LLM;
8. análise acontece de maneira assíncrona.

Invariante:

- texto obrigatório não pode resultar em entrada válida vazia.

## 10.2 Editar entrada

1. verificar autenticação e propriedade;
2. alterar título/texto/tags conforme regras;
3. quando mudança exigir nova análise, voltar para `PENDING_ANALYSIS`;
4. emitir `JournalEntryUpdated`;
5. reprocessamento ocorre de forma assíncrona.

Ponto de atenção: definir no código quais mudanças exigem reanálise. Alterar texto certamente é candidato; demais campos precisam de regra explícita.

## 10.3 Excluir entrada

1. verificar proprietário;
2. aplicar exclusão lógica ou estratégia definida;
3. remover/desvincular efeitos derivados conforme política;
4. tratar recomendações associadas;
5. emitir `JournalEntryDeleted` quando implementado.

Não executar cascatas destrutivas sem decidir retenção/auditoria/LGPD.

## 10.4 Analisar entrada por IA

1. Event Dispatcher encontra evento pendente;
2. aplica controle de idempotência;
3. worker de análise é acionado;
4. AI Processing solicita dados ao Journal Module;
5. prepara request para o provedor;
6. IA retorna estrutura;
7. estrutura é validada;
8. temas devem ser compatíveis com catálogo ativo;
9. persistir Analysis/sentenças/associações pertinentes;
10. atualizar status da entrada;
11. gerar `JournalEntryAnalyzed`;
12. falha atualiza status/erro e segue política de retry.

## 10.5 Gerar recomendação

1. `JournalEntryAnalyzed` ou outro gatilho adequado ativa Recommendation Worker;
2. Recommendation Engine recebe temas/contexto do Journal;
3. consulta Catalog / Knowledge Module;
4. seleciona conteúdo compatível;
5. persiste recomendação em `recommendation_schema`;
6. disponibiliza para consulta do usuário.

Quando nenhum conteúdo adequado existir, retornar estado/lista vazia consistente; não inventar referência inexistente apenas para preencher UI.

## 10.6 Selecionar passagem contextual

A passagem contextual é uma referência específica associada a tema/frase/reflexão.

Fluxo conceitual:

1. temas relevantes são identificados;
2. Catalog retorna passagens candidatas aprovadas/adequadas;
3. sistema/IA seleciona ou classifica candidata;
4. associação é persistida em `SENTENCE_PASSAGES`;
5. `reason` explica a associação;
6. `payload_snapshot` preserva dados necessários daquele momento.

Não confundir com `Recommendation` cultural.

## 10.7 Ingestão/processamento de obra

A documentação indica capacidade de o administrador cadastrar obras e de a IA processar obras para sugerir passagens.

Fluxo esperado em alto nível, sem fixar nomes ainda não formalizados:

1. administrador cadastra obra/autor/arquivo;
2. arquivo da obra vai para S3;
3. conhecimento canônico da obra é gerenciado pelo Catalog;
4. um evento/worker de ingestão pode acionar AI Processing;
5. conteúdo é lido/processado;
6. IA propõe trechos/passagens e temas;
7. saída é validada;
8. passagens candidatas ficam pendentes de revisão;
9. administrador aprova, rejeita ou ajusta;
10. somente material aprovado deve ser usado como conhecimento confiável nas recomendações conforme política definida.

## 10.8 Compartilhar síntese

1. usuário escolhe conteúdo/período/permissões;
2. Sharing valida solicitação;
3. consulta Journal por interface pública;
4. gera token seguro;
5. persiste **hash**, não token puro, conforme modelo;
6. gera síntese/exportação;
7. salva artefato no S3;
8. registra `SHARED_EXPORTS`;
9. retorna link ao usuário;
10. profissional acessa link;
11. token é validado, além de status/expiração/revogação;
12. somente campos autorizados são exibidos.

## 10.9 Profissional sugere atividade

1. profissional está em página válida;
2. token/escopo são verificados;
3. envia título/descrição;
4. atividade é associada ao `shared_export_id` e usuário;
5. persiste em `PROFESSIONAL_ACTIVITIES`;
6. evento `ProfessionalActivitySuggested` pode acionar notificação;
7. usuário visualiza atividade/orientação na sua área.

## 10.10 Exclusão de conta

O Auth Module coordena a operação, mas não deve romper limites de módulos com SQL cruzado.

O fluxo vigente é deliberadamente dividido em duas etapas:

1. `POST /auth/request-delete` exige uma sessão autenticada e obtém o `user_id` exclusivamente do contexto de autenticação;
2. o Auth revoga qualquer solicitação ativa anterior, gera um código criptograficamente aleatório, persiste somente seu hash com expiração e registra `emails.user_deletion.requested` na Outbox na mesma transação;
3. o Notification transforma esse evento em um e-mail contendo um link para a tela de confirmação;
4. a confirmação chama `DELETE /auth/delete?code=...`; abrir o link por `GET` não pode excluir a conta automaticamente;
5. um código válido, não expirado, não revogado e ainda não usado marca `users.deleted_at`, confirma o código, revoga todas as sessões e registra `auth.user.deleted` na Outbox na mesma transação;
6. consumidores dos demais módulos deverão reagir a `auth.user.deleted` para aplicar suas próprias políticas, sem SQL cruzado pelo Auth.

O código de confirmação é de uso único e o valor bruto só existe durante a emissão e no evento necessário ao envio do e-mail. O banco armazena apenas `token_hash`. Respostas de código inexistente, expirado, revogado ou reutilizado não devem revelar qual condição ocorreu.

### Recuperação da conta excluída

A recuperação também usa duas etapas, mas nenhuma exige sessão, pois a exclusão revoga todas as sessões:

1. `POST /auth/request-recovery` recebe somente o e-mail e sempre responde de forma genérica, independentemente de o endereço não existir, pertencer a uma conta ativa ou pertencer a uma conta excluída;
2. apenas para uma conta com `deleted_at` preenchido, o Auth revoga uma solicitação ativa anterior, persiste o hash de um novo código e registra `emails.recovery_user.requested` na Outbox;
3. o Notification envia o link de recuperação pelo mesmo pipeline SNS/SQS/Lambda/SES;
4. `POST /auth/recovery?code=...` valida um código não expirado, não revogado e ainda não usado, limpa `users.deleted_at`, confirma o código e registra `auth.user.recovered` na Outbox, atomicamente;
5. a recuperação não cria sessão: o usuário deve efetuar login novamente com suas credenciais existentes.

No estado atual, a recuperação restaura somente a capacidade de autenticação. O comportamento de Journal, Sharing, Recommendation e arquivos após `auth.user.recovered` depende das políticas futuras de retenção e dos consumers de cada módulo. Não há prazo máximo de recuperação da conta além da expiração de cada código emitido; essa janela permanece uma decisão de produto/privacidade pendente.

A operação precisa coordenar, por interfaces/eventos:

- conta/credenciais/sessões;
- entries e dados derivados;
- recomendações;
- compartilhamentos/tokens;
- arquivos aplicáveis;
- auditoria e política de retenção/anonimização.

A documentação admite exclusão **ou anonimização**. A política jurídica/técnica final deve ser explicitada antes de implementar remoção definitiva irreversível.

---

# 11. Outbox, eventos e idempotência

## 11.1 Por que existe

Processos como análise de IA, geração de recomendação, ingestão de obras e envio de notificações não devem bloquear operações síncronas principais.

O projeto usa Outbox para registrar intenção de evento junto ao estado transacional e workers internos para executar continuação assíncrona.

## 11.2 Regra transacional

Quando uma alteração de estado exige evento, persistência de negócio e registro da Outbox devem, sempre que tecnicamente possível, participar da mesma transação PostgreSQL.

Exemplo:

`salvar JournalEntry + salvar JournalEntryCreated na Outbox -> commit único`

Evitar:

`commit entrada -> tentar publicar evento -> falhar -> entrada fica sem processamento`.

## 11.3 Processamento

No código atual, o caminho operacional de transição para notificações Auth ainda é:

`Outbox PostgreSQL -> worker dispatcher -> RabbitMQ -> consumer Notification -> SMTP`

O caminho-alvo decidido é:

`Outbox PostgreSQL -> worker dispatcher -> Amazon SQS -> AWS Lambda -> handler Notification -> Amazon SES`

O dispatcher permanece um processo do monólito modular. O código da Lambda deve ser versionado neste
repositório como entrypoint fino que reutiliza o handler de aplicação do módulo Notification. O gatilho SQS
só deve ser ativado após implementar idempotência, tratamento de falha parcial e testes do consumer.

Fluxo esperado:

1. worker seleciona evento PENDING/retry elegível;
2. marca/obtém lock conforme estratégia;
3. verifica idempotência para o consumidor;
4. executa handler;
5. registra processed event;
6. marca Outbox como PROCESSED;
7. em falha, incrementa attempts, registra last_error e calcula próxima tentativa;
8. após política máxima, estado final precisa permanecer auditável/visível para administração.

## 11.4 Ponto técnico a revisar: chave de PROCESSED_EVENTS

O DER atual mostra `event_id` como PK e também possui `consumer_name`.

Se **um mesmo evento puder ser consumido por mais de um handler/consumer**, `event_id` sozinho pode impedir registrar processamento independente por consumidor.

Antes de criar migration definitiva, verificar o roteamento real e decidir conscientemente se a identidade deveria ser algo como:

`(event_id, consumer_name)`

Isto é um **ponto de revisão técnica**, não uma autorização para alterar o modelo sem discussão.

## 11.5 Nomes de eventos citados nos artefatos

Nomes observados:

- UserRegistered;
- UserAccountDeleted;
- JournalEntryCreated;
- JournalEntryUpdated;
- JournalEntryDeleted;
- JournalEntryAnalyzed;
- ProfessionalActivitySuggested;
- CatalogThemeChanged;
- CatalogReferenceChanged;
- CulturalRecommendationChanged;
- CatalogManagementChanged.

Os documentos não formam ainda um catálogo de eventos totalmente consistente. Antes de tornar nomes payloads públicos/internos permanentes, criar um catálogo/ADR se necessário.

---

# 12. IA, segurança semântica e curadoria

## 12.1 A IA não é fonte de verdade do catálogo

O LLM pode:

- analisar;
- classificar;
- resumir;
- gerar candidatos;
- explicar associações;
- classificar relevância.

Mas temas, passagens, obras e autores curados pertencem ao Catalog / Knowledge Module.

## 12.2 Saída estruturada

Toda resposta utilizada programaticamente deve possuir contrato estruturado e validação.

Nunca fazer lógica crítica usando parsing frágil de texto livre se a operação precisa de campos estruturados.

## 12.3 Temas controlados

Quando a IA classifica uma entrada, ela deve trabalhar com temas permitidos/ativos ou com um fluxo explicitamente aprovado para tratamento de "sem correspondência".

Não criar `Theme` no Neo4j apenas porque o LLM retornou um termo novo.

## 12.4 Conteúdo sensível

O journaling é privado e potencialmente contém material sensível.

Consequências arquiteturais:

- não registrar `content_text` em logs comuns;
- não colocar texto privado em AuditLog.details;
- evitar payloads de Outbox com conteúdo integral se o consumidor puder recuperar por ID;
- não enviar mais conteúdo ao LLM do que o necessário para o caso de uso;
- revisar política de observabilidade para não capturar bodies sensíveis;
- proteger secrets e credenciais de serviços externos;
- não replicar entradas privadas para Neo4j.

## 12.5 Limites de interpretação

O produto é ferramenta de reflexão e apoio. A documentação do TCC descreve integração com profissional, mas não estabelece o sistema como substituto de profissional de saúde.

Prompts, textos de interface e respostas geradas devem evitar representar inferências da IA como diagnóstico clínico comprovado.

---

# 13. Segurança, privacidade e LGPD

Funcionalidades já relacionadas à privacidade:

- acesso autenticado ao journaling;
- propriedade de registros;
- exportação de dados;
- exclusão/anonimização;
- compartilhamento consentido;
- token com expiração/revogação;
- hash de token;
- password hash;
- sessões revogáveis;
- audit logs;
- logs sem conteúdo sensível;
- S3 para artefatos controlados.

## 13.1 Não assumir criptografia de conteúdo já implementada

O DER conceitual antigo descrevia `content_text` como texto cifrado. O glossário e DER atuais descrevem `content_text : TEXT`, sem especificar mecanismo de cifragem em nível de aplicação.

Logo:

- proteção de dados é requisito conceitual;
- **criptografia de campo/aplicação ainda precisa ser verificada no código/infra**;
- não afirmar na documentação técnica que existe criptografia específica sem prova na implementação.

## 13.2 Tokens

Para links compartilhados e reset de senha, o modelo favorece persistir hash do token.

Boas práticas que precisam ser implementadas de acordo com a stack:

- token com entropia adequada;
- expiração;
- comparação segura;
- revogação;
- não logar token puro;
- link sempre por HTTPS em produção.

## 13.3 Auditoria

Auditar ações relevantes sem copiar conteúdo privado.

Exemplos candidatos já sugeridos no material:

- ENTRY_CREATED;
- EXPORT_REQUESTED;
- compartilhamento criado/revogado;
- operação administrativa;
- reprocessamento.

O catálogo final de ações deve ser consolidado ao implementar.

---

# 14. Interface e experiência atual

O TCC já possui mockups e descrições das principais interfaces. Eles são referência de fluxo e informação, mesmo que a implementação visual possa evoluir.

## 14.1 Telas comuns

- Cadastro;
- Login;
- Perfil e privacidade.

## 14.2 Usuário final

- Dashboard;
- Journaling / Nova entrada;
- Recomendações;
- Compartilhar diário/síntese;
- Atividades e orientações;
- histórico/detalhes/análise conforme casos de uso.

## 14.3 Administrador

- Dashboard administrativo;
- Gerenciar obras;
- Recomendações culturais;
- Revisar passagem;
- Gerenciar temas;
- fluxo de curadoria.

## 14.4 Direção visual observada

Os mockups atuais e a identidade conceitual convergem para uma aparência:

- minimalista;
- sóbria;
- introspectiva;
- fundo claro/off-white/creme;
- verde escuro e tons suaves como acento;
- poucos elementos agressivos;
- foco na leitura e reflexão.

O material histórico também cita preto, branco, sépia/ouro envelhecido e tipografias clássicas. Isso é referência de identidade, não obrigação técnica de CSS.

Não redesenhar completamente a experiência apenas por preferência estética da IA se a tarefa não for justamente rever UX/UI.

---

# 15. Casos de teste e estratégia de qualidade

O TCC possui uma matriz extensa de testes de aceitação e integração. Ela deve ser usada como base para testes automatizados.

## 15.1 Testes de aceitação prioritários

Cobrir pelo menos:

- cadastro válido;
- e-mail duplicado;
- validação de cadastro;
- login válido/inválido;
- perfil;
- exclusão de conta;
- criação de entrada válida/inválida;
- histórico vazio/com dados;
- detalhes da entrada;
- edição/reanálise;
- exclusão;
- análise concluída/pendente/falha;
- confirmação/remoção/ajuste de temas;
- recomendações existentes/ausentes;
- referências existentes/ausentes;
- criação de compartilhamento;
- período sem dados;
- token válido/expirado/revogado;
- sugestão de atividade;
- exportação geral de conta;
- acesso admin autorizado/não autorizado;
- CRUD/revisão de catálogo;
- falhas operacionais;
- reprocessamento.

## 15.2 Testes de integração prioritários

Fronteiras descritas no TCC:

- Frontend/BFF/Auth;
- Auth/PostgreSQL;
- Journal/PostgreSQL;
- Journal/Outbox;
- Dispatcher/AI Processing;
- AI/Journal;
- AI/LLM;
- AI/PostgreSQL;
- AI/Processed Events;
- Recommendation/Journal;
- Recommendation/Catalog;
- Catalog/Neo4j;
- Recommendation/PostgreSQL;
- Sharing/Journal;
- Sharing/S3;
- Sharing/PostgreSQL;
- página compartilhada/Sharing;
- Sharing/Internal Events;
- Notification/SES;
- Notification/PostgreSQL;
- Admin/Catalog/Neo4j;
- Catalog/Recommendation;
- Outbox/Processed Events;
- tratamento de retry/falha.

## 15.3 Pirâmide prática

Ao implementar uma feature:

1. testes unitários de domínio para invariantes;
2. testes de application use case com ports fake/mocks apenas onde adequado;
3. testes de repository contra banco real/test container quando possível;
4. testes de integração entre módulos para contratos internos importantes;
5. testes HTTP/aceitação para fluxos críticos.

A ferramenta exata de testes deve seguir a stack existente. Não escolher framework novo sem necessidade.

---

# 16. Concorrentes e diferenciação

O estudo de concorrentes incluiu:

- Theryo;
- MindSync;
- Rosebud;
- Reflection;
- Mindsera;
- Life Note.

Padrões observados no estudo:

- alguns concorrentes são fortes em journal + terapia;
- alguns em padrões/insights;
- alguns em filosofia/mentores históricos;
- não foi identificado no material analisado um equivalente que reúna exatamente a combinação proposta pelo Reflecta.

O desenvolvimento deve preservar especialmente:

- curadoria filosófica/literária/cultural;
- ligação explicável entre reflexão e referência;
- controle do conhecimento;
- ponte opcional e consentida com profissional;
- journaling como experiência central, não como simples chat com LLM.

---

# 17. Inconsistências e decisões pendentes conhecidas

Esta seção é deliberadamente importante. Uma IA deve lê-la antes de criar migrations ou contratos permanentes.

## 17.1 Numeração dos casos de uso

Os números dos UCs não estão totalmente sincronizados entre o PDF do TCC e os arquivos `.puml`.

Exemplo: casos administrativos e de IA aparecem com numeração diferente conforme o artefato.

Regra temporária:

> Use **nome do caso de uso + ator** como identidade semântica. Não faça lógica, nome de classe ou endpoint depender da numeração antes de normalizar o catálogo de UCs.

## 17.2 Ator Administrador x modelo de autorização

A representação do MVP foi decidida: `UserRole` (`USER`/`ADMIN`) no agregado e na tabela `users`.

O papel é carregado do Auth a cada request e propagado no `AuthenticatedPrincipal`, sem confiar em role enviada pelo cliente ou gravada no JWT. O guard HTTP `require_role` possui cobertura unitária no serviço que diferencia `USER` e `ADMIN` e protege a criação administrativa de temas; permanecem pendentes testes HTTP de acesso permitido/negado, sua aplicação nas demais rotas administrativas e o fluxo seguro de bootstrap/promoção/rebaixamento de administradores.

## 17.3 ConsentRepository sem entidade correspondente

O componente Sharing contém `ConsentService` e `ConsentRepository`, porém DER/glossário atuais não mostram tabela/entidade `CONSENT`.

Possibilidades a analisar:

- consentimento está embutido em `SHARED_EXPORTS.permissions`;
- falta uma entidade explícita;
- diagrama de componentes está mais adiantado que modelo de dados;
- componente deve ser simplificado.

Não escolher silenciosamente.

## 17.4 Identidade do profissional

A interface de compartilhamento fala em e-mail do profissional e a tela de atividade apresenta profissional responsável, porém:

- `SHARED_EXPORTS` não contém profissional_email/id;
- `PROFESSIONAL_ACTIVITIES` não contém autor/profissional;
- não existe entidade Professional no modelo atual.

Isso afeta rastreabilidade e UX. Deve ser resolvido conscientemente antes do fluxo final de compartilhamento.

## 17.5 RecommendationItem x Work no Neo4j

Há potencial sobreposição:

- `Work` no Neo4j já representa livro, filme, artigo ou conteúdo cultural;
- `RECOMMENDATION_ITEMS` no PostgreSQL também representa item recomendável e pode referenciar Work em metadata.

Antes de expandir o catálogo, esclarecer qual é a fonte canônica para cada tipo de conteúdo.

Não duplicar automaticamente toda obra nos dois bancos sem política explícita.

## 17.6 Histórico de Analysis

O DER apresenta JournalEntry `1 -> N Analysis`, permitindo histórico de reanálises, mas não existe ainda campo explícito como `version`, `is_current` ou `superseded_at` no modelo apresentado.

Se múltiplas análises forem persistidas, decidir como recuperar a análise corrente de forma determinística.

## 17.7 Processed Events por consumidor

Ver seção 11.4. A chave atual pode exigir revisão se múltiplos consumidores processarem o mesmo evento.

## 17.8 MFA

`mfa_enabled` está modelado, porém não há um conjunto completo de casos de uso/fluxos de MFA no TCC atual.

Tratar como capacidade modelada, não necessariamente como prioridade do MVP.

## 17.9 `DRAFT` em JournalEntry

O enum conceitual possui DRAFT, mas o fluxo principal salva entrada diretamente em `PENDING_ANALYSIS`.

Não construir autosave/draft sem confirmar que o estado será utilizado.

## 17.10 E-mail de confirmação

Testes/fluxos mencionam e-mail de confirmação/boas-vindas, mas o estado de verificação de e-mail não está explicitamente modelado em USERS.

Verificar implementação/decisão antes de criar fluxo obrigatório de email verification.

## 17.11 Exportação geral de conta

Existe UC de exportação de conta/dados e armazenamento em S3, porém não há entidade específica de job/export geral no modelo atual.

Decidir se o processamento é síncrono, assíncrono ou reutiliza uma abstração existente antes de criar tabela nova.

## 17.12 Criptografia de `content_text`

Modelo antigo menciona texto cifrado; modelo atual não especifica. Ver seção 13.1.

---

# 18. Tecnologias confirmadas x tecnologias ainda não confirmadas

## 18.1 Confirmadas nos artefatos atuais

- arquitetura de backend: monólito modular;
- Clean Architecture + DDD como orientação de implementação atual;
- PostgreSQL;
- vetores no PostgreSQL/pgvector a validar na infraestrutura;
- Neo4j;
- Amazon S3;
- Amazon SES;
- LLM/provedor de IA externo;
- embeddings/vetores semânticos;
- Frontend Web;
- API/BFF;
- Outbox + workers + Processed Events;
- Amazon SQS + AWS Lambda + Amazon SES como alvo decidido para notificações Auth;
- RabbitMQ + SMTP como implementação de transição até o cutover validado;
- PlantUML e Mermaid como formatos de documentação arquitetural.

## 18.2 NÃO confirmadas pelos arquivos disponíveis neste contexto

Os seguintes itens não devem ser inventados por este documento:

- linguagem definitiva do backend;
- framework web do backend;
- ORM;
- ferramenta de migrations;
- framework do frontend;
- biblioteca de componentes;
- gerenciamento de estado do frontend;
- provedor LLM específico;
- modelo específico de embeddings;
- dimensão dos vetores;
- estratégia de autenticação de token/JWT concreta;
- Docker/Compose;
- CI/CD;
- cloud de deployment além dos serviços AWS citados;
- observabilidade;
- secrets manager;
- framework de testes;
- formato de API OpenAPI/GraphQL/REST definitivo;
- ferramenta de background jobs;
- cache;
- rate limiting.

Quando o repositório for aberto no Work/agente de código, esses itens devem ser obtidos do código real e registrados em `IMPLEMENTATION_STATUS.md`.

---

# 19. Estado de implementação conhecido neste contexto

## 19.1 O que está disponível

Neste pacote de contexto foram analisados artefatos de projeto/documentação, incluindo:

- proposta conceitual;
- DER inicial;
- estudo de concorrentes;
- documentação do TCC;
- casos de uso em PlantUML;
- arquitetura em Mermaid;
- diagramas de componentes;
- DER atual PostgreSQL + Neo4j;
- glossário atual;
- diagrama de classes.

## 19.2 O que NÃO está disponível aqui

O código-fonte do repositório não foi fornecido junto aos anexos usados para montar este contexto.

Portanto, este documento **não pode afirmar quais módulos/endpoints/migrations já estão implementados**.

O primeiro trabalho do agente que tiver acesso ao repositório deve ser executar o procedimento de bootstrap descrito em `IMPLEMENTATION_STATUS.md` e atualizar o status com evidência de arquivos reais.

---

# 20. Política de fontes e precedência

Os artefatos não foram produzidos todos no mesmo momento e existem divergências históricas. Para evitar regressões, use a seguinte regra de precedência operacional:

1. **decisão explícita mais recente do time/usuário registrada em ADR ou instrução atual**;
2. **código, migration e testes existentes**, quando claramente representam implementação vigente e não bug/dívida;
3. `PROJECT_CONTEXT.md` + ADRs vigentes;
4. `glossario_dados_reflecta.md` e diagramas atuais de arquitetura/dados/componentes;
5. documentação atual do TCC;
6. casos de uso `.puml` - semanticamente importantes, mas com numeração divergente;
7. proposta inicial/DER inicial/ideias Individuum;
8. ideias futuras e benchmarking de concorrentes.

Se duas fontes do mesmo nível divergirem, interromper decisão irreversível e apontar a divergência.

### Importante

Essa precedência não permite ignorar o TCC. Se o código foi alterado por conveniência e rompe requisito acadêmico vigente, isso precisa ser discutido e documentado.

---

# 21. Artefatos de referência do repositório

Manter, preferencialmente, os seguintes arquivos sob `docs/` ou pasta equivalente:

### Produto e requisitos

- `Contexto geral da proposta de projeto.pdf` - origem conceitual; contém ideias históricas Individuum;
- `Apps com propostas parecidas mas nao cobrem a demanda.pdf` - benchmarking;
- `TCC-Template-DocumentacaoDeProjeto-Versao-1.pdf` - requisitos, fluxos, modelos, interfaces e testes.

### Modelagem

- `casos de uso usuario-final.puml`;
- `casos de uso profissional de saude.puml`;
- `casos de uso administrador.puml`;
- `casos de uso ia.puml`;
- `diagrama-de-classes-reflecta.puml`;
- `diagrama-der-monolito-postgres-neo4j.puml`;
- `glossario_dados_reflecta.md`.

### Arquitetura e componentes

- `reflecta-arquitetura-monolito-modular.mmd`;
- `diagrama de componentes diario.mmd`;
- `diagrama de componentes recomendacoes module.mmd`;
- `diagrama de componentes notificacao.mmd`;
- `diagrama de components profissional de saude.mmd`;
- `diagrama de components catalogo econhecimento.mmd`;
- `diagrama componente eventos internos.mmd`.

### Histórico

- `Primeira ideia de entidades e relacionamentos do projeto.pdf` - útil para compreender evolução, mas não é modelo atual.

---

# 22. Como manter a documentação sincronizada

Mudanças que exigem avaliar atualização de documentação:

## Mudou entidade/campo/relação

Atualizar, quando aplicável:

- migration;
- modelo de domínio;
- `glossario_dados_reflecta.md`;
- DER;
- diagrama de classes;
- testes.

## Mudou fluxo de caso de uso

Atualizar:

- caso de uso/US se necessário;
- diagrama de sequência;
- contrato de operação;
- testes de aceitação;
- API.

## Mudou módulo ou integração

Atualizar:

- diagrama de arquitetura;
- diagrama de componentes;
- ADR;
- testes de integração.

## Mudou evento

Atualizar:

- catálogo de eventos/ADR;
- producer;
- consumers;
- payload/schema;
- testes de idempotência/retry;
- diagramas relevantes.

---

# 23. Definition of Done arquitetural

Uma feature não está tecnicamente pronta apenas porque o endpoint funciona.

Antes de considerar uma tarefa concluída, verificar:

- [ ] requisito/caso de uso atendido;
- [ ] autorização/propriedade tratada;
- [ ] regra de domínio está no lugar correto;
- [ ] controller não contém regra central;
- [ ] domínio não depende de infra/framework;
- [ ] módulo não acessa banco privado de outro módulo;
- [ ] transação está correta;
- [ ] Outbox usada quando há continuação assíncrona necessária;
- [ ] handler é idempotente quando pode haver retry;
- [ ] erros e estados de falha estão definidos;
- [ ] logs não vazam conteúdo privado;
- [ ] testes unitários/integrados relevantes existem;
- [ ] migrations são reversíveis/seguras conforme política do projeto;
- [ ] documentação afetada foi atualizada;
- [ ] `IMPLEMENTATION_STATUS.md` foi atualizado quando a feature altera o estado real do projeto;
- [ ] nenhuma tecnologia nova foi introduzida sem necessidade/decisão.

---

# 24. Regras para agentes de IA

Qualquer IA trabalhando neste projeto deve seguir estas regras:

1. **Leia `PROJECT_CONTEXT.md` inteiro antes de alterações arquiteturais.**
2. Leia `AGENTS.md` antes de editar código.
3. Consulte `IMPLEMENTATION_STATUS.md` e confirme no código o status da área.
4. Para tarefas específicas, leia também o `.puml`, `.mmd`, glossário e seção do TCC correspondente.
5. Não trate Individuum como nome atual.
6. Não reintroduza áudio/imagem/rede social/premium no MVP.
7. Não transforme o monólito modular em microsserviços.
8. Preserve Clean Architecture + DDD.
9. Não permita dependência do Domain em framework/ORM/AWS/LLM.
10. Não faça acesso direto ao schema/repository interno de outro módulo.
11. Não crie temas canônicos diretamente a partir de saída livre do LLM.
12. Não replique conteúdo privado do journal no Neo4j.
13. Não inclua conteúdo privado em logs/auditoria/eventos sem necessidade explícita.
14. Não altere schema público/DB/evento silenciosamente.
15. Não "corrija" inconsistências de documentação sem registrar decisão.
16. Ao encontrar divergência entre código e documentação, relate-a.
17. Antes de grandes refactors, explicar impacto e listar arquivos afetados.
18. Ao finalizar, informar: o que mudou, testes executados, decisões assumidas e documentação atualizada.

---

# 25. Primeira sessão de desenvolvimento com acesso ao repositório

Quando o projeto for aberto em um ambiente de IA com acesso aos arquivos, o primeiro prompt recomendado é:

```text
Antes de implementar qualquer feature, leia AGENTS.md, PROJECT_CONTEXT.md e IMPLEMENTATION_STATUS.md.
Depois inspecione o repositório inteiro em nível de estrutura, dependências, migrations, configuração, testes e módulos existentes.

Não altere código ainda.

Compare o código real com o contexto documentado e atualize/produza um relatório do IMPLEMENTATION_STATUS.md contendo:
- stack real encontrada;
- estrutura de módulos;
- o que já está implementado por módulo;
- migrations existentes;
- endpoints existentes;
- testes existentes;
- integrações externas já configuradas;
- divergências entre código e documentação;
- dívidas/bloqueios;
- próximo menor incremento recomendável.

Não assuma que itens do TCC já foram implementados. Use evidências do repositório.
```

Somente depois desse inventário deve começar a implementação de novas features.

---

# 26. Estratégia sugerida de implementação incremental

A ordem precisa ser validada contra o código real, mas o domínio sugere uma sequência segura:

## Fase A - Fundação

- estrutura modular/Clean Architecture;
- configuração;
- PostgreSQL;
- migrations;
- Auth mínimo;
- infraestrutura de testes;
- Outbox base.

## Fase B - Journal sem IA

- criação;
- histórico;
- detalhe;
- edição;
- exclusão;
- propriedade;
- estados.

## Fase C - Pipeline assíncrono de IA

- evento JournalEntryCreated;
- dispatcher/worker;
- port de LLM;
- análise estruturada;
- falha/retry;
- Analysis;
- sentenças/temas;
- embeddings quando necessários.

## Fase D - Catálogo

- Neo4j;
- Theme;
- Author;
- Work;
- Passage;
- admin/curadoria;
- S3 para obras/capas.

## Fase E - Associação e recomendação

- passagem contextual;
- Recommendation Engine;
- RecommendationItem/Recommendation após resolver responsabilidade com Work;
- visualização/salvar.

## Fase F - Sharing

- resolver identidade/consentimento do profissional;
- SharedExport;
- token;
- S3;
- página pública protegida;
- revoke/expire;
- atividades profissionais.

## Fase G - Notification e operações

- SES;
- NotificationLog;
- dashboard de falhas;
- retry administrativo;
- auditoria.

## Fase H - fechamento de TCC

- alinhar diagramas ao código;
- executar testes de aceitação/integração;
- atualizar documentação;
- registrar limitações;
- preparar evidências/demonstração.

Não interpretar essa sequência como sprint fixa; ela serve como mapa de dependências.

---

# 27. Perguntas que devem ser respondidas após inspeção do código

O agente com acesso ao repositório deve responder objetivamente:

1. Qual linguagem/framework do backend?
2. Qual framework/frontend?
3. Existe um monorepo ou repos separados?
4. Como os módulos estão fisicamente organizados?
5. Existe ORM? Qual?
6. Qual ferramenta de migration?
7. PostgreSQL já está configurado?
8. pgvector já está habilitado?
9. Neo4j já está configurado?
10. S3/SES possuem adapters ou somente ideia/documentação?
11. Qual autenticação já existe?
12. Admin role já foi resolvida no código?
13. Quais UCs já funcionam end-to-end?
14. Outbox já existe?
15. Workers já existem?
16. Há idempotência real?
17. Existe integração com LLM?
18. Qual schema da saída do LLM?
19. Há testes automatizados?
20. Quais ambientes existem?
21. Há Docker/Compose?
22. Há CI?
23. Como secrets são carregados?
24. Há logging/observabilidade e ele mascara conteúdo privado?
25. Quais divergências com este documento representam decisão nova e quais são bugs/débitos?

Registrar respostas em `IMPLEMENTATION_STATUS.md`.

---

# 28. Fontes utilizadas para consolidar este contexto

Este documento foi construído a partir dos seguintes artefatos fornecidos para o projeto:

- `Contexto geral da proposta de projeto.pdf`;
- `Primeira ideia de entidades e relacionamentos do projeto.pdf`;
- `Apps com propostas parecidas mas nao cobrem a demanda.pdf`;
- `TCC-Template-DocumentacaoDeProjeto-Versao-1.pdf`;
- `reflecta-arquitetura-monolito-modular.mmd`;
- `casos de uso administrador.puml`;
- `casos de uso profissional de saude.puml`;
- `casos de uso usuario-final.puml`;
- `casos de uso ia.puml`;
- `diagrama de componentes diario.mmd`;
- `diagrama de componentes recomendacoes module.mmd`;
- `diagrama de componentes notificacao.mmd`;
- `diagrama de components profissional de saude.mmd`;
- `diagrama de components catalogo econhecimento.mmd`;
- `diagrama componente eventos internos.mmd`;
- `diagrama-der-monolito-postgres-neo4j.puml`;
- `glossario_dados_reflecta.md`;
- `diagrama-de-classes-reflecta.puml`;
- decisão atual informada para desenvolvimento: **Clean Architecture + DDD**.

---

# 29. Regra final

O Reflecta já possui um conjunto significativo de decisões de produto e arquitetura. O objetivo da etapa de desenvolvimento não é pedir para a IA "criar um app de journaling" do zero.

O objetivo é:

> **implementar incrementalmente o sistema Reflecta que já foi modelado, validando cada decisão contra o código real, preservando as fronteiras do domínio e mantendo código, testes e documentação sincronizados.**

Se uma tarefa exigir romper uma dessas premissas, a mudança deve ser tratada como **decisão arquitetural/produto explícita**, e não como detalhe de implementação.
