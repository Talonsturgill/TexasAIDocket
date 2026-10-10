# Written Ask agent

The production Worker uses Claude Haiku 5.5. The default in `answer.js` and
`ASK_MODEL` in `wrangler.toml` agree. Adaptive thinking uses medium effort with
room for reasoning and the short answer. Requests omit sampling parameters.

Answer cache keys include the model request settings and the published pack
revision. Upgrading the model retires old answers while preserving spending
counters. Retrieval, sentence verification, Turnstile and the existing caps
continue to govern each answer.

Deployment preserves dashboard variables outside the committed pins. The small
health probe caps its own effort at high when answers use xhigh or max.

Checked sentences wait for the provider's terminal classification. A declined
turn returns a clear notice and discards partial text without caching it.
Model progress resets the browser's idle timeout without exposing draft text
or reasoning. A stalled stream still closes after 45 seconds of inactivity.
Empty replies, interrupted streams and provider stream errors remain retryable.
Only completed, accepted answers enter the cache.
The cache schema retires entries written before these completion checks.

Run the Worker checks and regenerate the dashboard bundle before release.

```sh
node workers/ask/bundle.mjs
node workers/ask/test.js
wrangler deploy --config workers/ask/wrangler.toml
```

Deploy the reviewed commit after its CI passes and it reaches `main`.
`/_config` reports the effective model. `/_probe` makes a small real API call
and reports the provider's response model and whether it returned text.
Then ask fresh questions and follow-ups through the live site's form.
