# Automation Task

Automation is off and dry-run by default. Require a current receipt containing
owner, allowed actions/channels, customer scope, limits, confirmation boundary,
start/expiry and revocation state. Persist a verified cursor and idempotency key.
For every new or existing customer, require a read-back-proven one-time background
result before outbound, stage or public-pool work. If absent, run it once and
record useful matched facts or exactly `背调无信息`; block that customer on
failure. Process one customer fully before the next. Stop on conflict, duplicate,
unexpected reply, login/channel error, safety prompt or read-back failure. Never
resume from an old login, schedule, prompt or previous permission.
