# Modelo de dados implementado

A Figura 57 do documento revisado utiliza os painéis `57a`, `57b`, `57b2`, `57c` e `57d`. Os arquivos DOT são as fontes editáveis; SVG e PNG são suas exportações. O diagrama `uc34-recuperacao` complementa o fluxo de recuperação de conta na Figura 32A.

O modelo foi atualizado pela conferência das migrations e dos modelos em `Codigo/BACK`, no código de referência `ef728bb`: 22 tabelas de aplicação e 24 chaves estrangeiras físicas. A tabela técnica `alembic_version` registra a versão das migrations do ambiente e é tratada separadamente das tabelas de aplicação. Esta atualização utiliza as definições do código; a conferência anterior do banco, de 9 de novembro de 2026, permanece registrada na cópia de segurança.

PK indica chave primária, FK indica chave estrangeira, UQ indica unicidade global de campo e `[NULL]` indica campo opcional. As cardinalidades derivam das FKs, da nulabilidade e das restrições de unicidade. Os painéis mostram chaves e campos selecionados; os demais atributos estão no glossário do Word. Entidades repetidas entre painéis são a mesma tabela.

A unicidade por usuário nas solicitações de verificação, exclusão e recuperação é parcial, condicionada ao estado do token. Não implica uma única solicitação histórica por usuário. As referências ao catálogo Neo4j são lógicas, sem FK entre bancos. O painel do grafo representa as relações usadas pelos repositórios do catálogo; `RELATES_TO` persiste `confidence` e `source`.

O painel B inclui `entry_date` e o índice único parcial de `journal_entries` em `(user_id, entry_date)` para `deleted_at IS NULL`. O painel B2 inclui `sharing_schema.professional_activities`, com as FKs `share_id` e `user_id` e seus vínculos com compartilhamentos e titulares.

Recomendações relacionais e logs genéricos permanecem previstos no modelo lógico. As atividades estão definidas na migration `f13a4c600006` e representadas no painel B2.

Para regenerar uma exportação, usar Graphviz sobre o DOT, por exemplo `dot -Tsvg 57a-autenticacao.dot -o 57a-autenticacao.svg`.
