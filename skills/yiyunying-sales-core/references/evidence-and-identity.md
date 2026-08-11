# Evidence And Identity

## Customer binding

- Prefer the stable CRM customer ID. Row order, partial labels, translated notes and adjacent records are never identities.
- When no stable ID is available, require an exact normalized email or phone and at least one matching field such as name, company, country, inquiry ID or product.
- Normalize phone formatting but preserve the raw values and every proven alias. A redirect to a conversation is not enough to rewrite the CRM phone unless both numbers are proven to be the same customer.
- If WhatsApp, email and CRM bind to different people, stop external, stage and public-pool actions until the record is resolved.

## Required evidence set

Read the full content, direction and timestamp of every relevant source:

1. CRM contact and basic information.
2. Original inquiry and the complete automatic-allocation detail.
3. Full CRM dynamics, including expanded text.
4. CRM channel records and actual WhatsApp/email threads.
5. Sent, delivered, read, failed and bounced status.
6. Quote, PI, order, payment and shipping records when the customer has reached those steps.

List previews, unread badges, subjects, snippets, stage labels and a success toast
are not complete evidence. An encrypted, waiting or unavailable message does not
prove intent; ask for the minimum readable text when appropriate.

## Latest intent

Determine the latest real customer intent, confirmed product/use, quantity,
location, budget or timing, current concern, last sales promise and single next
decision. A newer direct customer statement overrides older notes. A simple
thanks or system auto-reply is not a new purchase signal.

## Name, language and country

- Address the customer using a verified contact name from CRM or the customer's own message. Never expose internal Chinese labels, dates, countries, models or stages as a name.
- If the name is uncertain, use a neutral greeting in the customer's language.
- Determine country from the combined CRM record, delivery address, explicit statement, phone code and conversation language. Do not use phone code or language alone when evidence conflicts.

## Background research

- Apply this gate to every customer, whether new or existing, before outbound, stage change or normal CRM follow-up.
- Search CRM dynamics first. A valid prior result is either useful matched facts or the exact entry `背调无信息`; if either exists and can be read back, do not repeat the background check.
- Otherwise open the exact CRM customer, run the configured AI background research once, wait for completion, and compare name, company, email/domain, phone, country and address with the bound customer.
- Fill only verified missing fields. Never overwrite a stronger customer-provided or transaction-proven value with research output.
- Similar names, unrelated companies and generic search results are not customer facts.
- Immediately write useful matched facts or, when no usable information exists, only `背调无信息` in the correct CRM follow-up area.
- Read the saved result back. Until research and CRM read-back are complete, do not send, change stage, move public pool or count the customer as handled.
- If research is unavailable, remains running, conflicts with identity or cannot be saved/read back, stop that customer and record an operational exception outside customer dynamics.
- Use the stable idempotency key `customerId:background-research:v1`; automation memory may store only the key/status, never the customer facts.

## High-stage identity

For A/B3, shipping or after-sales work, verify the trade order detail itself.
Cross-check customer, country, seller entity, store, exact product/configuration,
quote number, contract number, order number, trade order number, PI, payment and
shipping reference. A filename or matching country alone cannot bind an order.
