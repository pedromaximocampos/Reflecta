# Frontend Reflecta

## Execução integrada com auth

- Frontend: `npm ci` e `npm run dev` em `frontend` (origem padrão `http://localhost:5173`).
- Configure `VITE_API_URL=http://localhost:8000` no `.env.local` do frontend.
- No backend e worker de e-mail, configure `FRONT_END_DOMAIN=http://localhost:5173`, sem caminho adicional. Essa origem também é usada pelo CORS para aceitar chamadas com credenciais. Se mudar o host ou a porta do frontend, ajuste a configuração e reinicie os serviços.
- Quando usar o worker AWS Lambda, configure também `FRONTEND_BASE_URL` com a mesma origem do frontend.
- Prepare as dependências do backend com `uv sync` na raiz do repositório (incluindo `python-slugify`). Confira `DEBUG` e `SQL_ECHO` como booleanos e as configurações `NEO4J_*`, `AWS_SNS_REGION` e `AWS_SNS_ARN` no ambiente.
- API, bancos, migrations e worker de notificações precisam estar em execução para completar os fluxos. A resposta `202` confirma a solicitação, não a entrega do e-mail.
- Faça um novo login para carregar papel e data de nascimento nas sessões criadas antes desta integração.
- Testes locais: `npm test`, `npm run build` e `npm run lint`.

| Tela/ação | Endpoint |
| --- | --- |
| Perfil: salvar alterações | `PATCH /auth/user-info` |
| Perfil: solicitar exclusão | `POST /auth/request-delete` |
| Link de exclusão: confirmar | `DELETE /auth/delete?code=...` |
| Recuperar conta: solicitar link | `POST /auth/request-recovery` |
| Link de recuperação: confirmar | `POST /auth/recovery?code=...` |

As confirmações por código não enviam cookies nem Bearer token e só são executadas após clique do usuário.

## Recuperação de conta excluída

## Redefinição de senha

- O link recebido por e-mail deve abrir o frontend em `/auth/reset-password?code=...` (a origem vem de `FRONT_END_DOMAIN` no backend), e não a URL da API diretamente.
- A tela envia `POST /auth/reset-password` com `{ reset_token, new_password, repeated_password }` e não exige login.
- O código é lido da URL, removido após sucesso e nunca é colocado nos campos visíveis da tela. Senhas não são armazenadas localmente.
- A senha precisa ter pelo menos 12 caracteres e as duas entradas precisam coincidir. Códigos inválidos, expirados ou já usados ficam como erro retornado pelo backend.

- Login e cadastro oferecem o link **Recuperar conta excluída**.
- `/auth/request-recovery` é uma página pública que envia `{ "email": "..." }` para `POST /auth/request-recovery`. A mensagem de sucesso é genérica e não revela a existência da conta.
- O e-mail deve apontar para `/auth/recovery?code=...`. A página exige clique em **Confirmar recuperação da conta** antes de chamar `POST /auth/recovery?code=...`.
- As duas chamadas dispensam autenticação e não enviam cookies nem Bearer token. A confirmação não cria sessão: após sucesso, o usuário pode voltar ao login e usar suas credenciais existentes.
- Há tratamento de código ausente/inválido/expirado/reutilizado, falhas da API e cliques repetidos. Reenvio é feito pelo formulário de solicitação; vale o link mais recente.
- Configure a URL do frontend no serviço de notificações e o fallback para `index.html` na hospedagem para permitir acesso direto ao link do e-mail.
- Contratos conferidos no backend desta branch. O envio real de e-mail e o fluxo ponta a ponta dependem do backend e serviço de notificações em execução.

## Integração do perfil

- A tela de perfil fica em `/auth/perfil`, independente do dashboard. O prefixo `/auth` fica reservado para os próximos fluxos de gerenciamento da conta.
- Configure `VITE_API_URL` com a URL do backend (padrão: `http://localhost:8000`).
- O formulário usa `PATCH /auth/user-info` com Bearer token e envia somente campos alterados: `name`, `surname`, `date_of_birth` e `avatar_url`.
- E-mail é somente leitura. O contrato atual não permite limpar campos enviando valores nulos.
- O perfil inicia com os dados retornados pelo login e mantidos em `sessionStorage`; não existe uma chamada de consulta de perfil nesta integração.
- `useAuth()` em `src/services/authSession.js` fornece `user`, `role`, `isAdmin` e `isAuthenticated`. Espera `user.role` como `ADMIN` ou `USER` no login. Papel ausente/desconhecido resulta em `role: null` e `isAdmin: false`.
- Login e refresh retornam `user.role` (`ADMIN` ou `USER`) e `user.date_of_birth` (`YYYY-MM-DD`). O perfil e os fluxos de exclusão/recuperação usam os endpoints do backend desta raiz.
- O papel no navegador serve para apresentação. Um futuro guard de administrador deve ser acompanhado de autorização no servidor; dados em `sessionStorage` não são prova de permissão.
- Após o login, `ADMIN` vai para `/deshboard`; `USER` ou papel ausente/desconhecido vai para `/inicio`, o dashboard do usuário. Papel não informado mantém `isAdmin: false`.
- Compartilhamentos, estatísticas e preferências continuam demonstrativos.

## Exclusão de conta

1. Em `/auth/perfil`, o botão vermelho **Excluir conta** abre a explicação do fluxo.
2. **Enviar e-mail de confirmação** chama `POST /auth/request-delete`, sem body, com o Bearer token da sessão. O retorno `202` indica que a solicitação foi recebida; o envio do e-mail é assíncrono.
3. O e-mail aponta para `/auth/delete?code=...`. Essa página funciona sem login e não realiza exclusão ao abrir o link.
   Links antigos para a porta da API também funcionam: `GET /auth/delete` redireciona para a confirmação no frontend, preservando o código.
4. **Confirmar exclusão da conta** chama `DELETE /auth/delete?code=...`. Após sucesso, o frontend limpa sua sessão, remove o código da URL e exibe a confirmação.

A exclusão do backend é lógica: desativa a conta e invalida as sessões, sem apagar definitivamente os dados. Reenviar a solicitação invalida o link anterior. Cancelar/fechar a interface não revoga um link já emitido; o usuário é orientado a ignorá-lo.

Configure a URL base do frontend no serviço de notificações do backend para que os links abram esta aplicação. O servidor que hospeda o frontend precisa servir `index.html` também no acesso direto a `/auth/delete`. Os endpoints foram conferidos no backend. Envio real e integração ponta a ponta ainda precisam ser validados com a API e o serviço de e-mail em execução.

Validação local: `node --test tests/auth.test.js`, `npm run build` e `npm run lint`.

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

## Telas de diário e dashboards

### Histórico de reflexões

- `/inicio/reflexoes` lista as reflexões do usuário autenticado, com paginação de 10 itens e ações para consultar, editar e excluir.
- `/inicio/reflexoes/:id` consulta uma reflexão específica.
- `/inicio/reflexoes/:id/editar` permite editar título, conteúdo e tags de contexto.
- A exclusão exige confirmação e chama `DELETE /journal/entries/{id}`. A entrada só desaparece da lista após a API confirmar o sucesso.
- As páginas usam os endpoints `GET /journal/entries`, `GET /journal/entries/{id}`, `PATCH /journal/entries/{id}` e `DELETE /journal/entries/{id}` com o Bearer token da sessão.

Telas adaptadas de `Projetoia/src/app/components` para JSX e os estilos existentes:

- `/inicio`: dashboard de usuário já existente, agora com acesso a **Nova reflexão**.
- `/inicio/diario`: tela `Journaling`, com título, conteúdo textual e contexto/tags.
- `/deshboard`: `AdminDashboard`, com resumo do catálogo, passagens pendentes, ações rápidas e falhas operacionais.

Os dashboards usam dados de exemplo. O diário permite criar entradas pelo botão **Salvar reflexão**; o botão separado **Rascunho** continua desabilitado. Áudio e imagem não foram incorporados ao diário textual. Ações de administração cujas telas ainda não foram importadas ficam desabilitadas. O layout oferece navegação em desktop e celular. O guard administrativo continua pendente; o login já retorna `role` para direcionar a navegação.

## Criar entrada de diário

- `/inicio/diario` envia `POST /journal/entries` com Bearer token da sessão, sem cookies ou identidade fornecida pelo formulário.
- O corpo contém `title` opcional (até 200 caracteres), `content_text` obrigatório (até 20.000 caracteres) e `context_tags` opcional. Temas separados por vírgula são enviados em `context_tags.domains`, com `source: "user"`; tags vazias e repetidas são removidas e cada tag aceita até 100 caracteres.
- O backend define usuário, identificador, data e status `DRAFT`. O salvamento persiste a entrada, mas não dispara análise automática.
- Durante a requisição, o formulário fica bloqueado para evitar envios simultâneos. Após sucesso, os campos são limpos e uma confirmação é exibida. Em falhas, o conteúdo permanece na tela; não há reenvio automático.
- Em `401`, a sessão é limpa e a tela orienta a copiar o texto antes de ir para o login. O texto não é armazenado fora da tela.
- A API precisa estar atualizada e a migration `d4a1c7e9b203` (schema do diário) aplicada no banco. Listagem, consulta, edição e exclusão ainda não estão integradas.

## Cores dos temas

O cadastro e a edição em **Gerenciar temas** incluem um seletor de cor.
A listagem e os temas associados às frases exibem a cor cadastrada.
A API retorna `color` em `#RRGGBB`, preparando futuros destaques por tema no texto.
Temas antigos sem cor usam o padrão `#8B5CF6`.

## Confirmação de e-mail

`/auth/verify-email?code=...` confirma o código via `POST /auth/verify-email`,
sem sessão ou cookies. Links no host da API redirecionam para essa tela.
Após sucesso, o código sai da URL e a página agradece ao usuário, informa
que ele pode fechar a aba e oferece acesso ao login. Códigos expirados,
inválidos e falhas de conexão exibem erro, sem mostrar sucesso.

## Catálogo administrativo

Acesse `/deshboard` com uma conta `ADMIN`. As páginas administrativas possuem
proteção de acesso; a autorização efetiva continua no backend.

- `/deshboard/obras`: cadastro com autoria, URL pública opcional para a capa,
  pré-visualização da imagem, envio de PDF validado e histórico dos pedidos nesta
  aba. O upload do PDF usa multipart com campo `document`.
- `/deshboard/passagens`: filtros por status, obra e ingestão; atualização manual ou
  a cada 10 segundos; consulta individual, edição, criação manual, aprovação,
  rejeição com confirmação, ativação, desativação e retirada lógica.
- Obras e ingestões ficam em `sessionStorage` para preservar IDs e autoria.
  Não há chamada de listagem de obras nem consulta de status da ingestão.
- O painel usa contagens retornadas pela API, sem métricas fictícias.

O backend desta branch implementa obras, ingestões e passagens. Falhas aparecem na
interface, sem respostas simuladas. Uma fila vazia não confirma conclusão ou falha
da ingestão.

Execute `npm test`, `npm run build` e `npm run lint` em `frontend`.

## Leitura da reflexão e da análise lado a lado

Em `/inicio/reflexoes/:id`, os controles **Lado a lado**, **Só reflexão** e
**Só análise** alternam a organização dos cards. No desktop, ampliar um card
recolhe o outro em uma faixa lateral; o botão dessa faixa reabre os dois. Cada
card possui rolagem própria e cabe na altura disponível da janela.

Quando a análise está concluída, o painel apresenta `main_message` como conclusão
geral e lista as passagens contextuais persistidas em `sentences[].passages`. Cada
passagem mostra a citação do catálogo, obra, autoria, localização, tema, motivo da
seleção e paráfrase. O texto é renderizado como conteúdo, nunca como HTML.

Em telas menores os cards ficam empilhados, com conteúdo recolhível e altura de
leitura limitada. Recolher mantém o componente montado: preserva seus controles,
o resultado da análise e o acompanhamento de uma solicitação pendente. A tela
de edição continua usando o formulário existente.

## Cadastro de obra em etapas

- `/deshboard/obras`: apresenta somente o formulário de cadastro. **Cadastrar e
  continuar** chama `POST /catalog/works` e navega apenas após a confirmação da API.
- A capa é opcional e enviada como `cover_image_url`; a API valida uma URL HTTP(S),
  persiste a propriedade da obra no Neo4j e a etapa seguinte exibe a imagem. Upload
  binário de capa para o S3 ainda não faz parte deste contrato.
- `/deshboard/obras/:workId/pdf`: apresenta o resumo da obra criada e o envio do PDF.
  Essa etapa exige uma obra preservada na sessão; sem ela, orienta iniciar o cadastro.
- Após o upload aceito, a tela mostra **Processamento solicitado** e oferece acesso
  às passagens filtradas por obra e ingestão. O formulário é substituído pela
  confirmação para evitar reenvio acidental.
- Obras cadastradas nesta aba podem ser retomadas pela primeira tela. Atualizar a
  página de envio mantém a obra e a confirmação no `sessionStorage`.
- O cadastro e o upload usam os mesmos endpoints e continuam sujeitos à dependência
  do backend documentada acima. Não foram criadas chamadas de listagem de obras.

Validação desta mudança: build, testes automatizados e contratos do backend. Cadastro
e upload reais continuam dependentes da API, Neo4j, S3 e credenciais AWS em execução.

O cadastro usa duas colunas no desktop e mantém o formulário centralizado e
compacto. A opção temporária de prévia foi removida; o upload exige obra cadastrada.
O teste completo de cadastro e envio de PDF permanece pendente.
