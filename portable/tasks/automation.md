# Automation Task

Automation is off and dry-run by default. Require a current receipt containing
owner, allowed actions/channels, customer scope, limits, confirmation boundary,
start/expiry and revocation state. Persist a verified cursor and idempotency key.
Process one customer fully before the next. Stop on conflict, duplicate,
unexpected reply, login/channel error, safety prompt or read-back failure. Never
resume from an old login, schedule, prompt or previous permission.
