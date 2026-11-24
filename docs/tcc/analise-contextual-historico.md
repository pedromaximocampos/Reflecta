# Análise contextual do histórico — períodos de 7 dias

A geração é voluntária e separada da análise individual automática. O usuário
escolhe início e fim de um período de **exatamente 7 dias**, contando ambas as
datas. O intervalo precisa conter **pelo menos 5 entradas não excluídas** do titular.
A análise usa **todas** as entradas desse período, sem limitar a cinco ou sete.
Não é necessário haver uma entrada em cada dia.

A seleção considera os dias no fuso `America/Sao_Paulo`. O filtro começa à
meia-noite local da primeira data, inclusive, e termina à meia-noite do dia
seguinte à última data, exclusive. Assim, inclui o último dia inteiro e respeita
viradas de mês, ano e regras históricas de horário de verão.

## Interface

Em “Minhas reflexões”, a seção “Análise do meu histórico” permite escolher as
duas datas. Alterar uma ajusta a outra para manter os sete dias. A tela informa
a quantidade de reflexões do intervalo e mantém o botão desabilitado com menos
de cinco. Selecionar datas e consultar elegibilidade nunca gera uma análise.
O usuário precisa clicar em “Analisar meu histórico”, que informa o envio das
reflexões ao provedor de IA.

O resultado mostra o período, resumo, padrões, mudanças ao longo do tempo,
perguntas de reflexão e links para as entradas utilizadas. A interpretação não
constitui diagnóstico clínico. Sugestões de temas não são tratadas como temas
confirmados. As análises anteriores seguem disponíveis na lista paginada.

## API

- `GET /journal/context-analysis?start_date=2026-10-20&end_date=2026-10-26`:
  consulta somente elegibilidade e resultado já salvo para o período e conjunto atual.
- `POST /journal/context-analysis`: solicita geração com JSON
  `{"start_date":"2026-10-20","end_date":"2026-10-26"}`.
- `GET /journal/context-analysis/history?limit=5&offset=0`: histórico paginado,
  sem precisar fornecer período nem manter o mínimo de entradas.

Datas são obrigatórias para consulta de elegibilidade e geração. Intervalos com
mais ou menos de sete dias são recusados com 422, inclusive por chamadas diretas
à API. Com menos de cinco entradas, a geração retorna 409 antes de chamar o
provedor. Falhas do banco/provedor retornam 503 com mensagem segura. O usuário
é determinado pela autenticação, sem aceitar proprietário no payload.

As respostas incluem `period` com `start_date`, `end_date` e `timezone`. O status
inclui `entry_count`, `minimum_entries`, `eligible` e `analysis`. O histórico
inclui `analyses`, `total`, `limit` e `offset`, ordenado por data e ID decrescentes.

## Persistência e consistência

A tabela `journal_schema.context_analyses` guarda o resultado e as referências
às entradas. Uma impressão do período e dos registros identifica o conjunto por
usuário. Repetir a solicitação reutiliza o resultado existente; uma constraint
evita duplicar resultados em concorrência. Requisições concorrentes antes do
primeiro commit ainda podem chamar o provedor mais de uma vez.

Antes de salvar, os registros de origem são bloqueados e o conjunto do período
é consultado novamente. Se mudou durante a geração, retorna 409 sem salvar o
resultado. Novas reflexões fora do período não alteram a impressão da análise.
Não há atualização automática de resultados nem envio de contexto a outras
análises. A janela é cronológica; não é uma busca por embeddings.

No histórico, excluir uma origem mantém o registro da geração, mas remove da
resposta seu conteúdo e referências (`available=false`, `result=null`,
`entry_ids=[]`). A conta autenticada só consulta seus próprios registros.

## Migração e análises legadas

A migração `a31b7d5e0001`, após `f29a30c3b001`, adiciona `period_start` e
`period_end`. Uma constraint exige que ambas sejam nulas ou que o intervalo
contenha sete dias. A migração foi aplicada ao PostgreSQL local.

As análises antigas continuam salvas com período nulo e são identificadas como
legadas na interface. Suas datas não são inventadas retroativamente. Elas não
são reutilizadas como se tivessem sido geradas para um período explícito.
A regra anterior das sete últimas entradas foi substituída por esta regra.

## Validação

Testes unitários cobrem intervalos inválidos, fuso, virada de mês/ano bissexto,
mínimo de cinco, envio de todas as entradas e cache separado por período.
O teste `tests/integration/test_context_history.py` valida o fluxo HTTP e
PostgreSQL, incluindo entradas nos limites exatos, fora do período, excluídas e
de outra conta, além de histórico e reutilização. As escritas fictícias são
revertidas e o provedor é simulado.

O compartilhamento da síntese por link válido por três dias está implementado
na issue #31. Consulte `Documentacao/compartilhamento-analise.md`.
