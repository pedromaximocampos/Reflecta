# Reprocessamento controlado — UC33 / #30

## Regra

A cota é por entrada do diário: o proprietário pode solicitar até três
reprocessamentos. A análise inicial (automática ou envio de um rascunho antigo)
não conta. As até duas chamadas internas do worker para validar a mesma resposta
de IA também não consomem solicitações adicionais.

A terceira solicitação é aceita e processada normalmente. Se também terminar em
`analysis_failed`, a entrada passa a exigir administrador para novas tentativas.
Enquanto estiver pendente, repetir a solicitação não incrementa a cota. Não há
reinício automático do contador; tentativas administrativas não devolvem cota.
Uma entrada analisada com sucesso não pode ser reanalisada por esse fluxo.

O usuário vê contagem, tentativas restantes, estado e mensagem de bloqueio, sem
receber o motivo técnico. Diagnósticos continuam exclusivos do administrador.
A análise contextual por período de sete dias é outro fluxo e não é modificada aqui.

## API do proprietário

`GET /journal/entries/{id}/analysis` inclui `reprocess`:

```json
{
  "user_limit": 3,
  "user_used": 2,
  "user_remaining": 1,
  "can_user_reprocess": true,
  "requires_admin": false,
  "revision": "2026-10-27T12:00:00+00:00"
}
```

`POST /journal/entries/{id}/analysis` aceita a revisão lida no GET:

```json
{"expected_revision": "2026-10-27T12:00:00+00:00"}
```

A revisão é obrigatória para sair de `analysis_failed`: evita que uma requisição
atrasada consuma nova tentativa se o worker já tiver falhado novamente. Sem revisão
ou com revisão antiga, retorna 409 sem consumir cota. O envio inicial de um
rascunho não exige body. Entradas pendentes retornam 202 sem nova cobrança.

O backend valida proprietário, conteúdo e limite, bloqueia a linha com
`FOR UPDATE` e grava contador, transição e auditoria na mesma transação. Conta
esgotada retorna 403 com mensagem sobre o limite. Outro proprietário ou entrada
indisponível retorna 404. Banco indisponível retorna 503 com mensagem segura.
Não são aceitos campos de papel ou contador no body.

## API e interface administrativas

`POST /admin/operational-failures/journal/{failure_id}/reprocess` exige ADMIN.
A operação aceita somente a falha mais recente de uma entrada não excluída em
`analysis_failed`. O detalhe administrativo informa `can_admin_reprocess` e a
política `reprocess` para habilitar a ação na tela.

Em Administração → Falhas operacionais → Ver detalhes, o administrador confirma
a solicitação e recebe a informação de que a análise entrou na fila. A lista é
atualizada. O contador do usuário permanece inalterado. O administrador também
pode intervir antes de a cota se esgotar.

Se já estiver pendente para essa falha, retorna 202 com `already_pending=true`,
sem gravar outra solicitação. Falhas antigas ou análises concluídas retornam 409;
registros ausentes/excluídos retornam 404. Reprocessamento de obras, trechos e
eventos não faz parte desta operação de análise do diário.

## Persistência e implantação

Migração `f29a30c3b001`, posterior a `e183a62b07c4`:

- `journal_entries.user_reprocess_count`, inteiro 0–3, padrão 0.
- `analysis_reprocess_requests`, com entrada, falha consumida, solicitante, papel,
  número da solicitação do usuário e data.
- Constraint única por falha, impedindo que uma mesma falha gere duas solicitações.

As linhas existentes iniciam a contagem em zero. O histórico anterior não registra
quem solicitou cada reprocessamento, portanto não permite reconstruir uma cota de
usuário confiável. A contagem e auditoria passam a valer a partir desta migração.
A auditoria é interna: não expõe identidades do solicitante nos endpoints comuns.

Aplicar `python -m alembic upgrade head` no ambiente configurado antes de executar
a nova versão da API/worker. A migração foi aplicada ao banco local. Esta branch
inclui o painel do card #29 como dependência, por fast-forward da branch UC32_#29.
Nenhum commit novo foi criado para a implementação do UC33 durante este trabalho.

## Validação — TA22, TA24, TI06, TI07 e TI08

Testes unitários cobrem envio inicial gratuito, três solicitações, bloqueio,
revisão antiga, idempotência, auditoria, papel administrativo e erros seguros.
Os testes de frontend cobrem a revisão enviada no body e o POST administrativo,
sem repetição automática em erros.

`tests/integration/test_reprocess_limit.py` executa com
`REPROCESS_TEST_DATABASE_URL` em PostgreSQL migrado. Valida o fluxo HTTP completo
e usa sessões paralelas reais para verificar uma única cobrança, uma única
solicitação administrativa e um único resultado concluído. O teste paralelo
segura o advisory lock do worker enquanto usa registros fictícios confirmados,
para impedir chamadas reais à IA. Esses registros são removidos ao final, apenas
pelos identificadores gerados pelo próprio teste. O teste sequencial usa rollback.
