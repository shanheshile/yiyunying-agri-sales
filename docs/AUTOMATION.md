# Automation

The generic automation is distributed as a paused template. It must be tested
manually with `dryRun=true` before scheduling.

Activation requires a receipt containing the authorizing user, effective run or
date range, CRM owner, accounts, channels, customer scope, queues/stages, per-
channel limits, protection window, excluded actions and stop condition. The
receipt is runtime state and must not be committed.

Automation may handle routine, low-risk follow-up only after evidence and
outbound gates pass. The first gate applies equally to new and existing
customers: an absent one-time background result must be completed, identity-
matched, saved as useful facts or exactly `背调无信息`, and read back before
outbound, stage or public-pool work. Formal quotations, PI, payment details, certificates,
dangerous-goods documents, taxes, customs scope and freight commitments stay in
the confirmation queue.

Stop immediately on identity ambiguity, stale sources, duplicate risk,
unexpected customer reply, authentication failure, platform safety prompt,
send/read-back mismatch or CRM read-back failure. Resume from the last verified
ledger cursor after authorization and health are rechecked.
