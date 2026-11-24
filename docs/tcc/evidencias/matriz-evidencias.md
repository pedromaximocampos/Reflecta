# Matriz de evidências dos testes do Reflecta

O capítulo 6 do [TCC Reflecta FINAL](../Documentacao/TCC-Reflecta-FINAL.pdf) apresenta os 36 casos com registro de execução manual ou automatizada. O registro de uma etapa constitui evidência parcial. Os testes de aceitação e de integração têm sequências próprias, conforme o capítulo 6.

## Execuções manuais

| Caso | Resultado observado | Evidência |
|---|---|---|
| TA01, TI01 — cadastro | Formulário e mensagem de conta criada com orientação de verificar o e-mail | [Cadastro](telas/cadastro.png), [Conta criada](telas/login-email-nao-confirmado.png) |
| TA02, TI02 — login | Tela de login e dashboard autenticado. A tentativa com e-mail ainda não confirmado exibe a mensagem de bloqueio, como verificação complementar | [Login](telas/login.png), [Dashboard](telas/dashboard.png), [Bloqueio](telas/login-email-nao-confirmado.png) |
| UC08 — confirmação de e-mail, evidência complementar a TA01 | Mensagem final de e-mail confirmado | [Confirmação](telas/confirmacao-email.png) |
| TA03 — consulta de perfil | Exibição dos dados de perfil | [Perfil](telas/Perfil.png) |
| TA04, TA05, TA07 — diário e análise pendente | Formulário de reflexão preenchido e histórico com uma reflexão aguardando análise | [Formulário](telas/journaling.png), [Histórico](telas/dashboard.png) |
| TA06, TA09 — análise concluída e temas | Uma entrada consta como analisada e o dashboard lista temas recorrentes | [Dashboard](telas/dashboard.png) |
| TA10 — recomendações | Lista com cartões de recomendação e, no dashboard, área de obras com mensagem de orientação | [Recomendações](telas/recomendacoes.png), [Outra captura da lista](telas/Screenshot_1.png), [Dashboard](telas/dashboard.png) |
| TA11, TA14 — compartilhamento | Formulário e histórico de compartilhamentos | [Compartilhamento](telas/Compartilhamento.png) |
| TA18 e TI05 — acesso administrativo | Painel administrativo exibido | [Painel](telas/adm_dashboard.png) |
| TA19, TI04 — gestão de temas | Lista, formulário preenchido e detalhe do tema com o mesmo nome e descrição | [Lista](telas/adm_temas.png), [Inserção](telas/adm_tema_inserir.png), [Detalhe](telas/adm_tema_detalhes.png) |
| TA20, TI04, TI10 — gestão de referências | Formulários de obra, obra cadastrada e catálogo com registros visíveis | [Formulário](telas/adm_obra_cadastro.png), [Tela alternativa de cadastro](telas/adm_novo.png), [Obra cadastrada](telas/adm_obra_enviar_pdf.png), [Catálogo](telas/adm_obras.png) |
| TA11 e TA14 — geração e acesso | Link com reflexões autorizadas criado em 22/11 e com vencimento em 25/11, no mesmo horário. O link com reflexões exibe o texto autorizado. O link de síntese exibe a análise e informa que as reflexões não foram incluídas. | [Link criado](telas/TA29-link-criado.png), [Análise com reflexões](telas/TA32-analise-compartilhada.png), [Somente síntese](telas/TA29-somente-sintese.png) |
| TA08, TA21, TA22, TA24 — falha e reprocessamento | A mesma reflexão foi preservada após a falha, voltou à fila, atingiu a cota de três solicitações e apareceu como analisada após a tentativa administrativa. O painel mostrou o diagnóstico e os parâmetros da nova tentativa. | [Falha inicial](telas/TA21-falha-inicial.png), [Nova tentativa na fila](telas/TA47-nova-analise-na-fila.png), [Cota esgotada](telas/TA63-cota-esgotada.png), [Diagnóstico](telas/TA46-diagnostico-admin.png), [Parâmetros administrativos](telas/TA47-parametros-admin.png), [Análise concluída](telas/TA47-analise-concluida.png) |
| TA25 — ingestão de PDF | O PDF de Meditações passou de 5 para 55 de 108 trechos concluídos e chegou a 100%, com 299 passagens associadas à obra. A consulta exibiu sugestões da IA de Meditações, com indicação das páginas 6–8 e estado Pendente de revisão. | [Cadastro](telas/TA64-cadastro-meditacoes.jpeg), [PDF selecionado](telas/TA64-pdf-meditacoes.jpeg), [Início](telas/TA64-meditacoes-processamento.jpeg), [51%](telas/TA64-meditacoes-51.jpeg), [100%](telas/TA64-meditacoes-100.jpeg), [Sugestões pendentes](telas/TA64-meditacoes-pendentes.jpeg) |
| TA17 — exportação | ZIP e JSON baixados e abertos. As evidências enviadas mostram o ZIP com reflexões e o JSON avulso com uma reflexão do titular. A conferência de isolamento e de credenciais ficou sem comprovação. | [Downloads](telas/TA37-downloads-concluidos.png), [JSON da primeira execução](telas/TA37-json-aberto.png), [ZIP da primeira execução](telas/TA37-zip-extraido.png) |

## Execuções automatizadas

A rodada de integração registrou cinco testes aprovados. [Log](automacao/integracao-corrigida-0Jjabv/05-backend-integration.log) · [Relatório XML](automacao/integracao-corrigida-0Jjabv/backend-integration.xml)

| Teste automatizado | Casos relacionados | Verificações registradas |
|---|---|---|
| [Compartilhamento](../Codigo/BACK/tests/integration/test_context_sharing.py) | TA11–TA16, TA23, TI03 e TI09 | Confirmação, escopos, privacidade, expiração, revogação e indisponibilidade após exclusão. |
| [Histórico contextual](../Codigo/BACK/tests/integration/test_context_history.py) | TI11 | Elegibilidade, isolamento por titular, histórico, reuso e invalidação após mudança das fontes. |
| [Falhas operacionais](../Codigo/BACK/tests/integration/test_operational_failures.py) | TA21 e TI07 | Consulta administrativa, filtros, detalhe e recusa de acesso ao diagnóstico por usuário comum. |
| [Limite de reprocessamento](../Codigo/BACK/tests/integration/test_reprocess_limit.py) | TA22, TA24, TI06 e TI08 | Cota, conflitos, auditoria, concorrência e solicitação administrativa. |

## Casos com registro de execução

| ID | Cenário | Cobertura registrada |
|---|---|---|
| TA01 | Cadastro com dados válidos | Evidência parcial |
| TA02 | Login com credenciais válidas | Evidência parcial |
| TA03 | Consulta do perfil | Resultado visual registrado |
| TA04 | Criação de entrada válida | Evidência parcial |
| TA05 | Histórico com registros | Evidência parcial |
| TA06 | Análise concluída | Evidência parcial |
| TA07 | Análise pendente | Evidência parcial |
| TA08 | Análise com falha | Resultado visual registrado |
| TA09 | Visualização de temas sugeridos | Evidência parcial |
| TA10 | Recomendações disponíveis | Evidência parcial |
| TA11 | Criação de link com conteúdo autorizado | Resultado visual registrado |
| TA12 | Análise indisponível para compartilhamento | Evidência parcial |
| TA13 | Solicitação sem confirmação ou de análise de outro titular | Evidência parcial |
| TA14 | Acesso com token válido | Resultado visual registrado |
| TA15 | Acesso com token expirado | Evidência parcial |
| TA16 | Acesso com token inválido | Evidência parcial |
| TA17 | Exportação válida da conta | Evidência parcial |
| TA18 | Administrador válido | Resultado visual registrado |
| TA19 | Gerenciamento de temas | Evidência parcial |
| TA20 | Gerenciamento de referências | Evidência parcial |
| TA21 | Visualização de falhas | Evidência visual e automatizada |
| TA22 | Reprocessamento de análise | Evidência visual e automatizada |
| TA23 | Compartilhamento após exclusão da fonte ou da conta | Evidência parcial |
| TA24 | Limite de reprocessamento pelo titular | Evidência visual e automatizada |
| TA25 | Processamento de obra e revisão das sugestões | Resultado visual registrado |
| TI01 | Cadastro encaminhado ao módulo de autenticação | Evidência parcial |
| TI02 | Login encaminhado ao módulo de autenticação | Evidência parcial |
| TI03 | Consulta pública pelo token | Evidência automatizada |
| TI04 | Atualização do grafo administrativo | Evidência parcial |
| TI05 | Consulta do painel administrativo | Evidência parcial |
| TI06 | Reprocessamento de análise | Evidência parcial |
| TI07 | Rastreabilidade de falhas entre módulos | Evidência parcial |
| TI08 | Indisponibilidade ou erro do provedor de IA | Evidência parcial |
| TI09 | Indisponibilidade do compartilhamento e falha de persistência | Evidência parcial |
| TI10 | Criação de Theme, Work, Author, Passage e relacionamentos | Evidência parcial |
| TI11 | Reuso da análise contextual e mudança das fontes | Evidência parcial |
