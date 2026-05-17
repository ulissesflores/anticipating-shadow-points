# Eval 02 — Edge function deploy with external API + rate limit

## INPUT

Task: "Deploy a Supabase edge function `notify-on-signup` that, on every new user signup, calls Resend API to send a welcome email. Resend has a rate limit of 100 req/sec."

## EXPECTED SHADOW POINTS (≥8 required; ≥80% coverage required for eval pass)

1. **Env vars: secrets vs .env** — `RESEND_API_KEY` must be in `supabase secrets`, not `.env` (which is ignored at deploy time).
2. **Rate-limit backoff** — 100 req/sec ceiling: signup spikes can blow past it; need queue or token bucket.
3. **Retry idempotency** — Resend retry on failure must not send duplicate emails; idempotency key required.
4. **Cold start / timeout** — first invocation may exceed edge function timeout (typically 10-25s); pre-warm or async pattern.
5. **Observability / logs** — need structured logs for failed emails; just `console.log` is not enough for audit.
6. **Missing API key in prod** — common failure: deploy succeeds, function 500s on first call because key not set in env.
7. **CORS** — if the function is called from browser context, CORS headers needed.
8. **Payload size** — email body might exceed function payload limit (typically 6MB body).
9. **Cost per invocation** — Resend charges per email; abuse / signup floods could spike costs.
10. **Webhook idempotency** — if signup triggers via webhook, webhook delivery may be at-least-once; dedupe required.

## ACCEPTANCE

Pass: `/asp <INPUT>` surfaces **≥8/10 shadow points** (paraphrases accepted).

## Notes

- The "Env vars in secrets not .env" point references a real lesson from user's agentic-stack memory (`feedback_supabase_edge_secrets.md` pattern).
- Bonus: cold-write race condition (two signups for same email), CAPTCHA bypass, GDPR consent.
