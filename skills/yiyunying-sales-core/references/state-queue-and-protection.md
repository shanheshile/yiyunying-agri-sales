# State, Queue And Protection

## Stage state machine

- `F`: new inquiry not yet validly handled.
- After a valid outbound reaches an F customer and no real reply exists, use `D` for delivered/waiting.
- A real product or purchase reply moves F/D to `C`. Do not downgrade an existing supported B/A stage merely because a new reply arrived.
- A formal product or trade-term amount enters `B`. Use `B1` after quotation with little/no further interaction, `B2` for sustained configuration, quantity, address, shipping, customs, payment or deal-term interaction, and `B3` after a verified PI is sent.
- Use `A` only after the order is real and a verified prepayment has arrived. A remains responsible for outstanding balance, production, shipment and after-sales; it does not mean the balance is fully paid.
- Stage changes require independent read-back. A save click or transient banner is not proof.

## Priority

Process real inbound purchase questions before proactive follow-up. Then prioritize:

1. B3 payment, PI or final confirmation.
2. New F inquiries and any stage with a real new need or unanswered question.
3. B2 configuration, destination, shipping, customs or quotation confirmation.
4. B1 price acceptance, minimum missing fact or next action.
5. Active C with current advancement evidence.
6. Protected public-pool review for eligible C/D records.

A customers are not routine marketing targets, but new order, shipment, balance
or after-sales questions must be handled promptly.

## Timing and limits

- Honor the deployment's channel limits. A temporary user instruction can narrow or explicitly increase a one-run cap, but does not become a permanent default automatically.
- Default WhatsApp limit is 40 unique customers per day. Count unique customers and message count separately.
- Review a true F at least every three natural days until it is correctly handled or staged. Do not send again inside the protection window without new information.
- Do not contact a customer who specified a future date, return from travel, funding milestone or other clear time node before that node.
- Group chats, internal groups and conversations that cannot bind to one customer remain silent.
- Do not fill a quota with low-value or protected customers.

## Refusal and public pool

Move a customer to the department public pool and archive the corresponding
conversation only after a clear statement of no need, no interest, cancellation,
already purchased and no longer needs, stop contacting, or explicit business/
product refusal. Record the exact words, channel, date and reasoning first.

Do not treat silence, temporary hesitation, price concern, budget waiting,
another expense, travel, future purchase timing or a request to contact later as
refusal. Three unsuccessful touches may trigger a protected review only when the
deployment's public-pool policy explicitly permits it; it never overrides a
future-contact instruction or active purchase evidence.

