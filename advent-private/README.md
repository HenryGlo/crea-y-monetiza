# Crea y Monetiza private advent landing

This is client landing code, not PerfectFlow application code. The branded email
screen and supplied calendar/resources belong to this repository/deployment.
Activepieces owns email eligibility, single-use codes, rate limits, delivery and
CRM intake. PerfectFlow is used only through its existing automation APIs.

`server.mjs` is a small, read-only static-content gateway: it relays requests to
the authenticated Activepieces webhook and converts a verified signed session
into an HttpOnly cookie. Private HTML is sandboxed with an opaque origin; images
and videos require scoped, expiring asset tickets. No paid entitlement, CRM
transition or campaign rule lives in this server.

Deploy `app/` (these server files), `content/` (the private supplied archive), and
`config.json` to `/opt/cym-advent-20261125` on the Crea droplet. Config contains
`gatewayKey`, `signingKey`, and the internal synchronous webhook URL. Keep this
file and the private resource bundle OUT of GitHub Pages and Git. The allowlist
is private workflow configuration in Activepieces, stored as SHA-256 email hashes.
Never expose that workflow export or credentials in this repository.

`install.sh` starts an isolated Node container and validates nginx before a
reload. It preserves the prior nginx configuration and never restarts the CRM.
The public GitHub Pages site redirects students to `/calendario/alumnas/` on
the client's application host. Legacy experience links redirect there as well.
The old public events URL is proxied for already-open tabs during cutover.

Access is valid for seven days. A newly requested code invalidates the previous
code; codes expire after ten minutes and are limited to five verification attempts.
Asset tickets last one hour and are renewed by the verified browser session.
An access-list removal prevents new sessions; existing sessions expire naturally.
Rotate the signing key to invalidate all sessions immediately.

Run `node --test tests/*.test.cjs tests/*.test.mjs`. No real email is sent by unit
tests. Live delivery tests use a separate, temporary workflow and signing key,
with one owned test address; disable that workflow after verification.

The adjacent `automation/advent-access.template.json` is a sanitized import
manifest, with blank signing/gateway/API keys, no approved addresses and a
placeholder Gmail connection. Set private inputs in the correct Activepieces
project and bind the existing client Gmail connection. The source of truth for
the code step is `automation/advent-access.mjs`; update the embedded template
source when changing it. Dynamic response property schemas are required by this
Activepieces version; omitting them causes response-step failures.
