# OSWeb web proxy

Lets the OSWeb Safari app show sites that refuse to be embedded (`X-Frame-Options` / CSP `frame-ancestors`).
A static site cannot do this by itself, so this small server fetches the page for you.

**Security model** - it is not an open proxy:
- Every request must carry an HMAC signature (`sig`) over `url|exp` made with your `PROXY_SECRET`; signatures expire (<= 1 hour, OSWeb uses 5 minutes) and only work for that one URL, so a page cannot reuse them.
- Private, loopback and link-local addresses are refused (SSRF protection), re-checked on every redirect.
- GET only, http(s) only, 10 MB / 15 s limits, no cookies are forwarded or stored.
- Pages are rendered inside a sandboxed iframe without `allow-same-origin`, so they cannot read OSWeb.
- Best effort: sites that depend on cookies, logins, or cross-origin API calls will not fully work.

## Deploy on Vercel
1. `cd proxy && vercel` (project root = `proxy/`), then add an env var `PROXY_SECRET` (a long random string) and redeploy.
2. In OSWeb: Settings > Websites > paste `https://<project>.vercel.app/api/p` and the same secret.

## Run locally
`PROXY_SECRET=changeme node proxy/server.js`, then use `http://localhost:8787/` as the proxy URL (add `ALLOW_PRIVATE=1` only for local testing against local sites).
