# Compartilhar síntese — UC06 / #31

Após gerar uma análise de histórico com período de sete dias e pelo menos cinco
entradas, o usuário pode compartilhar o resultado. Em “Minhas reflexões”, tanto
no resultado atual quanto nos detalhes de uma análise anterior disponível,
“Compartilhar análise” abre a confirmação do conteúdo exibido acima.

Por padrão, o link contém somente a síntese. O titular pode marcar **Incluir
também as reflexões utilizadas** para autorizar os textos, datas, títulos,
conclusões individuais da IA, temas mantidos e passagens relacionadas. A opção
inclui as entradas utilizadas pela análise, sem seleção avulsa de reflexões.

O titular confirma que conferiu o conteúdo e gera o link. A interface apresenta o
endereço e seu vencimento, com botão para copiar e possibilidade de seleção e
cópia manual. O sistema não envia e-mail, mensagem, convite nem notificação ao
destinatário. O titular escolhe a quem enviar o link por conta própria.

## Acesso do destinatário

O link usa `/compartilhamento#token=...`. A parte após `#` não é enviada ao
servidor de arquivos da página nem nos endereços das requisições. O frontend lê
o token e o envia no body de um POST para a API. Não exige login ou cadastro.
Quem possuir o link poderá consultar o conteúdo autorizado enquanto ele estiver
válido. Esse destinatário corresponde ao ator **Terceiro** e pode ser qualquer
pessoa com quem o usuário compartilha o link. O acesso por posse do token não
verifica sua identidade, formação ou vínculo profissional.

Está fora do escopo verificar se o destinatário é psicólogo ou terapeuta,
consultar registro profissional ou confirmar vínculo terapêutico com o titular.
A profissão de uma persona não restringe o ator Terceiro nem suas permissões.
Essa delimitação se aplica à consulta da análise contextual, às reflexões
incluídas com autorização e ao envio de atividades e reflexões guiadas.

O destinatário vê a mesma síntese salva: período, quantidade de entradas, data da
análise, resumo, padrões, mudanças e perguntas. O componente de apresentação é o
mesmo usado para o titular, sem os controles de compartilhamento nem os links
internos para as reflexões. Se o titular tiver autorizado a inclusão, a página
também apresenta as reflexões e as análises individuais disponíveis no snapshot.
Sem essa opção, não entrega os textos ou títulos do diário. Em ambos os casos,
a API pública não entrega IDs do titular, da análise ou das entradas, nomes de
perfil, e-mail nem tokens de sessão.
Naturalmente, o conteúdo da própria síntese confirmada pode mencionar fatos
presentes na análise — esse é o conteúdo que o titular escolheu compartilhar.

## Validade, tokens e revogação

Cada link tem token aleatório de 256 bits e validade de exatamente **72 horas**
a partir da criação, verificada no backend. Na igualdade com o vencimento já é
inválido. O banco persiste somente SHA-256 do token, não o token original. O token
é entregue ao titular somente na criação; após sair da página, ele pode consultar
metadados, revogar os links ou gerar outro, mas não recuperar o endereço antigo.

O titular pode revogar cada link antes do vencimento. A operação é idempotente.
A partir da revogação, a API recusa consultas futuras pelo token. A página aberta
reconsulta a autorização a cada minuto e também oculta o conteúdo no vencimento
local. Isso não retira uma cópia que o destinatário já tenha feito.

Token desconhecido, revogado, expirado, conta excluída ou origem indisponível
resultam na mesma mensagem genérica 404. A exclusão de uma reflexão usada na
síntese também impede novas consultas públicas. Resultados são snapshots: uma
nova análise não altera o conteúdo de links existentes.

O snapshot e os metadados ficam em `journal_schema.context_analysis_shares`.
Esse fluxo não gera um arquivo de exportação no S3. A validade é fixa em 72
horas, sem prazo personalizado ou campo de e-mail do destinatário.

Em “Compartilhamentos”, o titular consulta o histórico paginado, filtra links
ativos, expirados ou revogados e revoga acessos ativos. A listagem não recupera
o token original nem permite copiar novamente o link após sair da criação.

Respostas dos endpoints de compartilhamento usam `Cache-Control: no-store`,
`Referrer-Policy: no-referrer` e `X-Robots-Tag: noindex, nofollow`. O fetch público
não envia cookies nem Authorization. Não há catálogo público ou listagem pública
para descobrir análises: é necessário possuir o token enviado pelo titular.

## API

- `POST /journal/context-analyses/{analysis_id}/shares`, autenticado pelo titular,
  com body `{"confirmed":true,"include_journals":false}`: retorna 201 com ID,
  token, datas e `includes_journals`. A inclusão das reflexões exige
  `include_journals:true`; o padrão é falso.
- `GET /journal/context-shares`, autenticado pelo titular: lista os próprios
  compartilhamentos com filtro opcional `state` (`active`, `expired`, `revoked`)
  e paginação por `limit` e `offset`.
- `GET /journal/context-analyses/{analysis_id}/shares`, autenticado pelo titular:
  lista metadados e estado (`active`, `expired`, `revoked`), sem tokens/snapshots.
- `DELETE /journal/context-analyses/{analysis_id}/shares/{share_id}`, titular:
  revoga o link e retorna seus metadados.
- `POST /shared/context-analysis/resolve`, sem autenticação, body `{"token":"..."}`:
  retorna a síntese, `entries`, `includes_journals` e o vencimento. `entries`
  fica vazio quando as reflexões não foram incluídas na criação.

Um administrador não recebe acesso a gerenciar links de outro titular por seu
papel. Análises legadas sem período explícito ou com fontes indisponíveis não
podem gerar novos links (409). O servidor usa seu padrão de validação (400 para
body inválido) e retorna 503 com mensagem segura em indisponibilidade.

## Banco, implantação e testes

A migração `b31c72e00002`, posterior a `a31b7d5e0001`, cria
`journal_schema.context_analysis_shares`: proprietário, análise, hash único,
snapshot, criação, expiração e revogação. As exclusões físicas de conta/análise
removem os vínculos por cascata. A migração foi aplicada no PostgreSQL local.

A revisão dos cenários do TCC mantém TA11–TA16, TA23, TI03 e TI09 para
criação, autorização, persistência do snapshot, consulta e indisponibilidade.
Esses cenários documentais não constituem registro de execução. Os testes
automatizados verificam confirmação, propriedade, acesso sem
login, expiração exata, revogação repetida, fontes excluídas, dados permitidos,
persistência do token em hash e ausência de credenciais na consulta pública.
Os testes de `JournalSharingFacade` e `JournalShareSnapshotBuilder` também
verificam a inclusão opcional de reflexões e o contrato público desses dados.

As atividades e reflexões guiadas que o terceiro pode sugerir possuem
fluxo próprio. Sua notificação ao titular não é envio automático do link ao
destinatário.

O teste opcional `tests/integration/test_context_sharing.py` executa com
`SHARING_TEST_DATABASE_URL` em um banco migrado e usa a aplicação HTTP e o
PostgreSQL reais. Os dados fictícios são revertidos ao final. Não faz chamadas
à IA nem envia mensagens. A collection
`Codigo/BACK/postman/Reflecta-Compartilhamento.postman_collection.json` permite
validar as operações manualmente; os tokens reais não devem ser exportados.
