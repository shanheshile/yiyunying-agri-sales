# Freight Control

## Inquiry readiness

Prepare one request per customer, product configuration, quantity, destination
and incoterm. Required fields:

```text
国家：
地址：DDP/DAP/DDU写详细地址或邮编城市；CIF/CFR/CNF写目的港
产品：准确型号和配置
数量：
尺寸：每件包装长×宽×高 mm
重量：每件包装毛重 kg
方数：每件及合计 CBM
包装件数：
类型：贸易术语
限制：电池/液体/危险品/裸装/货值等已知情况
```

Do not copy example values into a real request. Compute a deduplication key and
read the forwarder's previous conversation/capability before sending. Do not
repeatedly send the same request to one forwarder. Acknowledge a real reply once
when the channel convention requires it.

## Term routing

For Europe with a complete deliverable address/postcode, try DDP first through
capable channels. One forwarder's inability to provide DDP is not proof that DDP
is impossible. Continue with another qualified DDP source and retain any offered
CIF option as a fallback, not as customer acceptance.

For CIF/CFR/CNF, confirm destination port and current CBM. For DAP/DDU/DDP,
confirm deliverable address/postcode, gross weight, unloading ability and tax/
customs scope. Use the customer's requested term unless a verified capability
problem requires a clearly explained alternative.

## Forwarder matrix

Store each reply independently with customer/request key, destination, term,
route, carrier, sailing/cutoff, transit time, validity, currency, charging unit,
minimums, origin fees, main carriage, destination fees, delivery, customs/tax,
as-actual charges, exclusions, restrictions and exact unavailable reason.

Never build a synthetic option from one forwarder's low ocean freight, another's
low origin fees and a third's destination charges. Compare only complete options
with the same product, quantity, packing, destination, term and scope. If scopes
differ, list the difference before comparing totals.

Negative freight, rebate or `return X per CBM` is an internal cost clue until its
calculation and collection conditions are verified. It does not authorize an
automatic customer discount and must not appear in the customer quote.

## Recommendation

Reject expired, incapable or incomplete options. For remaining options, compare
verified all-in internal cost, route/time, restrictions, risk and fee certainty.
Report calculation and recommended option for approval; do not send the formal
freight amount automatically.

