# Product Source Resolution

## Precedence

Use this order for each field, not for the whole record:

1. Effective-dated user/factory override that names the exact stable product and configuration.
2. Current live product detail by stable product ID.
3. Final factory packing sheet, certificate or configuration sheet for the exact unit.
4. Approved catalog snapshot within its freshness window.
5. Historical quote, chat or document only as a lead for re-verification.

A freight quote cannot override product dimensions or weight. A material-library
image cannot prove price, inventory, certificate, packing, performance or lead
time. A historical customer quote cannot become a universal product price.

## Conflict handling

- Compare model, product ID, code, configuration, factory/source version, observed time and effective date.
- Preserve both values and their sources. Use the higher-precedence value only when its exact binding and effective period are proven.
- A changed weight or package size invalidates freight quotes calculated from the old value.
- If volume calculated from dimensions differs from a confirmed booking CBM, retain both fields and their scopes; do not overwrite either silently.

## Freshness

Catalog and price sources must declare an observed time. Prices, availability,
certificates and freight-sensitive packing are stale unless the deployment's
freshness policy accepts them. Re-query live data before a formal quote when the
snapshot is stale or an override exists.

## Search result

Return stable ID, exact model, category, configuration, public parameters,
packing, internal pricing status, material matches, source and validation issues.
Do not silently choose between duplicate or similarly named products.

## Plausibility gates

- Parse units before comparing dimensions or weights. A bare `3.2*1.6*2.45`
  is commonly metres, while `1840*1520*1050` is commonly millimetres; retain
  the source text and expose the interpretation.
- A reported gross/package weight lower than confirmed machine/net weight is a
  hard conflict. Do not use it for freight inquiry, landed quote or booking.
- Calculate outer-volume CBM from the stated dimensions. If it differs from the
  reported/booking CBM by more than 10%, keep both values and stop booking until
  the scope is confirmed. A current approved system CBM may still be used for a
  preliminary freight inquiry when its source and caveat are recorded.
- Product parameters, packing and logistics readiness are separate. A valid
  EXW product price does not make unverified packing fit for CIF/DDP.
