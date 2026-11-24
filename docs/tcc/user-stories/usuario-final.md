## User Stories - Usuário Final

O Usuário Final representa a pessoa que utiliza o Reflecta para registrar reflexões textuais, acompanhar análises geradas pela IA, receber recomendações culturais, visualizar referências e compartilhar informações autorizadas com terceiros de sua escolha.

### US01 — Criar entrada de diário

**Como** usuário final,  
**quero** criar uma entrada de diário,  
**para** registrar minhas reflexões textuais no journaling.

### US02 — Visualizar análise da IA

**Como** usuário final,  
**quero** visualizar a análise da IA,  
**para** compreender melhor os padrões e interpretações gerados a partir das minhas reflexões.

### US03 — Gerenciar temas sugeridos pela IA

**Como** usuário final,  
**quero** gerenciar os temas sugeridos pela IA,  
**para** aceitar, organizar ou ajustar os temas identificados nas minhas reflexões.

### US04 — Receber recomendações culturais

**Como** usuário final,  
**quero** receber recomendações culturais,  
**para** acessar conteúdos relacionados ao contexto emocional e temático das minhas reflexões.

### US05 — Visualizar referências literárias e filosóficas

**Como** usuário final,  
**quero** visualizar referências literárias e filosóficas,  
**para** compreender os conteúdos associados às recomendações ou aos temas identificados.

### US06 — Compartilhar síntese com terceiro

**Como** usuário final,\
**quero** compartilhar uma síntese com um terceiro de minha escolha,\
**para** permitir que essa pessoa consulte as informações que autorizei.

### US07 — Exportar dados da conta

**Como** usuário final, quero exportar os dados da minha conta para obter uma cópia dos meus registros.

A funcionalidade está prevista no projeto como UC07 e ainda não foi implementada.

**Critérios de aceitação:**

- somente o titular autenticado pode gerar a própria exportação;
- o titular escolhe entre um JSON autocontido e um pacote ZIP com arquivos JSON separados;
- perfil, reflexões, análises, temas, passagens relacionadas, compartilhamentos e orientações profissionais são incluídos;
- a foto de perfil é incluída quando estiver disponível;
- senhas, tokens, hashes, sessões, embeddings e registros operacionais nunca são incluídos;
- a exportação é gerada sob demanda, não é persistida e não executa uma nova análise por IA;
- a resposta impede cache e é entregue como download com nome e data identificáveis.

### US08 — Criar conta

**Como** usuário final,  
**quero** criar uma conta,  
**para** acessar as funcionalidades do Reflecta.

### US09 — Entrar no sistema

**Como** usuário final,  
**quero** entrar no sistema,  
**para** acessar minha área pessoal e utilizar os recursos da plataforma.

### US10 — Gerenciar perfil

**Como** usuário final,  
**quero** gerenciar meu perfil,  
**para** editar meus dados básicos de identificação.

### US11 — Excluir conta

**Como** usuário final,  
**quero** excluir minha conta,  
**para** interromper meu acesso por exclusão lógica, preservando os dados que permitem recuperar a conta pelo UC34.

### US12 — Editar entrada de diário

**Como** usuário final,  
**quero** editar uma entrada de diário,  
**para** corrigir ou atualizar uma reflexão textual já cadastrada.

### US13 — Excluir entrada de diário

**Como** usuário final,  
**quero** excluir uma entrada de diário,  
**para** remover uma reflexão que não desejo mais manter no journaling.

### US14 — Visualizar histórico de reflexões

**Como** usuário final,  
**quero** visualizar meu histórico de reflexões,  
**para** consultar entradas anteriores registradas no sistema.

### US29 — Gerar recomendações de obras

**Como** usuário final,\
**quero** que o sistema gere recomendações de obras a partir dos temas das minhas reflexões,\
**para** consultar referências do catálogo relacionadas aos meus registros.

**Caso de uso:** UC29. O identificador detalha o processamento de apoio à consulta do UC04.

**Fluxo:** o backend consulta os temas recorrentes das entradas vigentes, considera a análise concluída mais recente de cada entrada e a seleção de temas do titular, busca passagens ativas no catálogo e ordena as obras pela recorrência temática e pela confiança das associações. O resultado é montado durante a consulta e retornado com paginação.

**Plano de verificação:** geração, composição da resposta e consulta após alteração do catálogo. O card #23 registra o escopo administrativo original; a definição atual está descrita nesta história e no documento revisado.

### US34 — Recuperar conta excluída

**Como** usuário final,
**quero** recuperar minha conta excluída logicamente por um link enviado ao e-mail cadastrado,
**para** retomar o acesso e os dados preservados após confirmar explicitamente a reativação.

**Caso de uso:** UC34. **Issue:** #53. Relaciona-se à exclusão lógica (UC11) e ao login posterior (UC09). Não redefine a senha nem cria sessão automaticamente.

**Critérios de aceitação:** resposta genérica para a solicitação; nenhuma reativação ao apenas abrir o link; confirmação válida reativa a conta; códigos ausentes, inválidos, expirados, revogados ou utilizados não a reativam; reenvio invalida links anteriores.

**Plano de testes:** resposta genérica, confirmação válida, código inválido, reenvio e persistência transacional.

---
