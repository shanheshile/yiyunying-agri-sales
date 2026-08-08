# CRM And Audit Ledger

## CRM business record

After each real action, protected-silence decision, confirmed channel failure or
public-pool decision, record only concise customer business facts:

- channel and actual sent/not-sent result;
- latest need or feedback;
- confirmed product, quotation, PI, freight or order status;
- current missing fact, concern or risk;
- next action and responsible time;
- stage basis when a stage changed.

Never put internal UI/technical narration into customer dynamics. Remove or
rewrite phrases equivalent to `客户标识`, `阶段复核`, `系统提示`, `保存失败`,
`为避免猜选`, page conflict, write failure or technical blockage. Put those in
the runtime execution log and user exception report instead.

## Independent verification

Sending, delivery, CRM dynamic creation, stage change, public-pool move and
archive are separate actions. Read each one back from the same stable customer ID
and record its own result. Do not infer one result from another.

## Idempotency

Create an action key from stable customer ID, action type, channel, normalized
content hash, product/quote reference and protected time bucket. Check the ledger
before acting. Resume from the last verified cursor and never restart a batch by
row position.

## Counts

Report audited customers, actual unique WhatsApp customers, WhatsApp messages,
sent/delivered/read, unique email recipients, sent/read/replied email, real
customer replies, system/automatic replies, CRM writes, verified stage changes,
public-pool moves, explicit-refusal moves, protected skips, channel failures,
confirmation-required quotes/freight/PI and unresolved exceptions separately.

Never equate a shrinking queue badge with completed follow-up. Refresh and read
the authoritative total when the count is suspect.

