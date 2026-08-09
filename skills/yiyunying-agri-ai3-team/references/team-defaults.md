# AI3 Team Defaults

## Stage semantics

- `F`: new inquiry not yet substantively handled.
- `D`: a substantive outbound was verified and the customer is waiting/silent.
- `C`: the customer replied with real interest or a requirement, before quotation.
- `B1`: a verified quotation was sent; next action is acceptance or missing data.
- `B2`: post-quote deep interaction on configuration, freight, customs or terms.
- `B3`: PI, payment or final order confirmation is in progress.
- `A`: order customer after verified advance/deposit payment; retain a balance-payment and fulfilment checkpoint.

Treat these as deployment defaults. A CRM adapter must map them to actual system
values and read the saved stage back before claiming success.

## Operating defaults

- Review new inbound purchase questions and F inquiries before proactive follow-up.
- Check whether one-time background research is already recorded. If not, run it once and immediately record only usable findings or `背调无信息`.
- Read inquiry allocation details, contacts, CRM dynamics, WhatsApp, email, quotes and orders before contact.
- Address customers by verified contact name, never by an internal remark label.
- Use one exact customer at a time; apply five-day duplicate-contact protection unless a new inbound message overrides it.
- Move an explicit refusal to the department public pool after recording the refusal words, channel, date and reason. Silence, hesitation, price concern or a future-contact date is not refusal.
- CRM dynamics contain customer facts, action, blocker and next step. Do not record internal UI errors, save failures or operator narration.
- No individual identity, phone, email, website, price, account or daily quota is hard-coded in this team package.
