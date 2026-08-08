# Quote Control

## Minimum inputs

Confirm customer/country, exact product ID/model/configuration, quantity,
attachments, current cost source, product image, packing, destination, trade
term, quotation currency, exchange-rate source/time, freight scope and every
additional cost included in that term.

When freight is not ready, an EXW machine-only price may be prepared if the
product and cost are fully verified. State that freight, destination charges,
duty/tax and delivery are excluded. Do not describe it as a landed price.

## Price source and profit semantics

- Use the current configured quote builder or approved price source for the exact product ID. A zero, blank, missing or stale cost is `价格待确认`.
- UI defaults are not evidence. Recheck product, image, customer, quantity, currency, incoterm, destination, profit field, lead time, payment, warranty and packing before generation.
- Declare whether a rate is markup on cost, gross margin on sale or backend-calculated. `cost * 1.15` and `cost / 0.85` are different and must never be substituted silently.
- If a deployment says the backend default is 10% and the current rate is usually 15%, retain the default field only as configured and set the current field to 15% after verifying the backend semantics. A generated page is still a draft.
- Round customer amounts upward only after all same-currency costs are included. Preserve the unrounded calculation internally.

## Currency

Prefer the customer's explicit or established quotation currency. Otherwise use
the deployment rule; a common default is EUR for euro-area customers, GBP for the
UK and USD for international trade elsewhere. Country, address and customer
history outweigh phone code or language.

Exchange rates require a source and timestamp. Convert every cost into one
customer-facing currency, apply the configured risk allowance once, and never
mix unconverted CNY/USD/EUR/GBP values in one total.

## Existing quotes

Do not automatically reduce a customer's established quotation because a newer
freight option or internal cost is lower. Compare scope and validity, then obtain
approval for any revised customer price.

## Quote artifact

The customer version must show exact product/configuration, quantity, verified
image, currency, unit/total price, incoterm and named destination, inclusions,
exclusions, validity, payment terms, production/delivery wording and seller
identity. Any mismatch makes the artifact incomplete and blocks sending.

