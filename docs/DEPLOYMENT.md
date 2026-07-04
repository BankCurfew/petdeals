# Deployment — PETDEALS

## Build

```bash
cd ~/repos/github.com/BankCurfew/petdeals
bun install
bun run build
```

Build output: `dist/` (~1MB, SSG HTML)

## Deploy

```bash
# Token: use CLOUDFLARE_DNS_TOKEN from ~/.oracle/security/cloudflare-dns.env
# (NOT cloudflare.env — that token is scoped to FA Tools only)
CLOUDFLARE_API_TOKEN=$(grep CLOUDFLARE_DNS_TOKEN ~/.oracle/security/cloudflare-dns.env | cut -d= -f2) \
CLOUDFLARE_ACCOUNT_ID=3b1af24a7513b520e418d7e707f6491e \
npx wrangler pages deploy dist --project-name=petzdeals
```

## Verify

```bash
curl -sI https://petzdeals.com | head -5
# Should return HTTP/2 200
```

Check:
- [ ] Site loads at petzdeals.com
- [ ] GTM fires (check GTM debug)
- [ ] Product cards render
- [ ] Affiliate links work (click → Shopee)
- [ ] Mobile responsive (390px)

## Infrastructure

| Service | Value |
|---|---|
| CF Zone | 50181bfbd24d46d29eba7e09f74dcaf5 |
| CF Pages | petzdeals (petzdeals.pages.dev) |
| CF Account | 3b1af24a7513b520e418d7e707f6491e |
| Custom domains | petzdeals.com + www.petzdeals.com |

## Rollback

```bash
# List deployments
npx wrangler pages deployments list --project-name=petzdeals

# Rollback to specific deployment
npx wrangler pages deployments rollback --project-name=petzdeals <deployment-id>
```

## Daily Deploy (automated)

Via CF Worker cron or `/petdeals-publish` skill:
1. Products published from Supabase (status: scheduled → published)
2. `bun run build` (regenerates all pages)
3. `wrangler pages deploy` (pushes to CF Pages)
4. Google Indexing API submits new URLs (max 200/day)

## Troubleshooting

| Issue | Fix |
|---|---|
| Build fails | Check `astro.config.mjs`, verify data/products.json is valid JSON |
| Deploy fails — "Invalid access token" | Use `CLOUDFLARE_DNS_TOKEN` from `~/.oracle/security/cloudflare-dns.env`, NOT `cloudflare.env` (FA Tools scope only). Verify: `npx wrangler whoami` |
| Deploy fails — "invalid header value" | Token has trailing whitespace. Use `grep ... \| cut -d= -f2` not `cat` |
| Old content shown | Purge CF cache: `curl -X POST "https://api.cloudflare.com/client/v4/zones/50181bfbd24d46d29eba7e09f74dcaf5/purge_cache" -H "Authorization: Bearer TOKEN" -d '{"purge_everything":true}'` |
| Images broken | Check R2 bucket URLs in Supabase |
| DNS not resolving | Check CF DNS records for CNAME → petzdeals.pages.dev |

## CI/CD (Future)

GitHub Actions: on push to `main` → build → deploy.
CF Pages also supports Git integration (connect repo → auto-deploy on push).
