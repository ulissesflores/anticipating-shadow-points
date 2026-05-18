Plan: deploy a Supabase edge function `notify-on-signup` calling Resend.

1. Write the function: handler that takes the signup payload, calls
   Resend with the welcome email template.
2. Add `RESEND_API_KEY` to the function's environment.
3. Deploy via `supabase functions deploy notify-on-signup`.
4. Verify with a test signup.

The 100 req/sec Resend rate limit is unlikely to be hit by signups
in most cases. If we do hit it, we can add a queue or retry.

We should also add some basic logging and error handling — wrap the
Resend call in a try/catch and log failures.
