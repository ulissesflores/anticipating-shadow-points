ASP plan for `notify-on-signup` edge function with Resend (100 req/sec).

Pre-mortem (30 days out):

1. Deploy succeeded; first call returned 500 because RESEND_API_KEY
   was in .env (ignored at deploy time), not in supabase secrets.
2. Signup spike during marketing launch blew past 100 req/sec rate
   limit; emails dropped silently.
3. Retry on transient failure caused duplicate emails (no idempotency
   key).
4. First invocation timed out (cold start) at 25s; subsequent fine
   but user got no welcome email for that signup.
5. CORS missing; browser-initiated signups failed silently.
6. Webhook delivery at-least-once; same signup processed twice.
7. Resend cost spiked when bot signups created abuse pattern.
8. Email body included user-uploaded avatar URL which exceeded
   payload limit (~6MB).
9. Observability gap: only `console.log`; no structured logs to debug
   the missed emails.
10. GDPR consent flag not verified before sending; legal flagged.

MAST pass:
- FC1: explicit constraints — Resend rate limit, signup volume,
  payload structure (FM-1.1, FM-1.3).
- FC2: coordination — secrets vs .env (FM-2.4 information withholding
  if the deploy team is unaware of supabase secrets semantics);
  idempotency contract between webhook and Resend (FM-2.6
  reasoning-action mismatch).
- FC3: verification — cold start timeout requires a synthetic
  acceptance test, not just "it deployed".

Categorized shadow points:
- Data: payload size, observability and structured logging.
- Integration: env vars in secrets not .env; CORS; webhook idempotency;
  Resend API contract.
- Concurrency: rate-limit backoff strategy with token bucket; cold
  start and timeout handling.
- Cost: per-invocation cost; abuse / signup flood mitigation
  (CAPTCHA, sliding window).
- Op-ex: missing API key in prod (canary deploy first); dead-letter
  queue for failed sends; alerting on send failure.

Mitigations:
- Use `supabase secrets set RESEND_API_KEY ...` not .env.
- Implement token bucket at 80 req/sec ceiling with retry backoff.
- Idempotency key on every Resend call (signup id).
- Async pattern: enqueue then process; avoid cold-start blocking.
- Structured logs (JSON) + alert on >1% send failure rate.
- CORS headers if browser-initiated.
- Webhook signature validation + dedupe on signup id.
