## User Stories - Administrador

O Administrador representa o ator responsável pela gestão administrativa do Reflecta, incluindo o catálogo de temas, referências filosóficas e literárias e revisão de passagens sugeridas pela IA.

### US26 — Acessar área administrativa

**Como** administrador,  
**quero** acessar a área administrativa,  
**para** utilizar funcionalidades restritas de gestão do sistema.

### US27 — Gerenciar catálogo de temas

**Como** administrador,  
**quero** gerenciar o catálogo de temas,  
**para** criar, editar, desativar ou remover temas utilizados pela IA nas análises.

### US28 — Gerenciar referências filosóficas e literárias

**Como** administrador,  
**quero** gerenciar referências filosóficas e literárias,  
**para** administrar obras, autores, passagens e referências utilizadas pelo sistema.

**Rastreabilidade:** UC28, issue principal #13. O frontend de inserção de obras (#74) é tarefa deste caso de uso. O processamento posterior da obra e a sugestão de passagens pertencem ao UC23 (#20).

### US30 — Revisar passagens sugeridas pela IA

**Como** administrador,  
**quero** revisar passagens sugeridas pela IA,  
**para** conferir o conteúdo e as associações temáticas, aprovar ou rejeitar sugestões e decidir separadamente sua ativação no catálogo.

Na revisão, o administrador deve conferir a correspondência do trecho com a obra e sua localização, a fidelidade da paráfrase, a coerência da nota interpretativa, a pertinência dos temas e o potencial de apoio à reflexão. Confiança temática e valor reflexivo são indicadores auxiliares calculados pela IA, sem comprovar a qualidade da interpretação.

As sugestões da ingestão começam em `PENDING_REVIEW`. Aprovar resulta em `APPROVED`; rejeitar resulta em `REJECTED`. A ativação posterior leva uma passagem aprovada ou inativa a `ACTIVE`; a desativação resulta em `INACTIVE`. Aprovação e ativação exigem temas existentes e ativos. Passagens cadastradas manualmente começam em `APPROVED` e também exigem ativação.

A edição permite ajustar localização, intervalo de páginas, paráfrase, prioridade e associações temáticas, preservando o trecho original e a nota interpretativa. A curadoria do catálogo não comprova a correção de cada associação ou explicação produzida posteriormente pela IA para uma reflexão do usuário.
