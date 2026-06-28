# Deployment — PETDEALS

## Build

```bash
cd ~/repos/github.com/BankCurfew/petdeals
bun install
bun run build
```

Build output: `dist/client/` (~1MB, SSG HTML)

## Deploy

```bash
CLOUDFLARE_API_TOKEN=[CF_API_TOKEN — see ~/.oracle/secrets/shopee-affiliate.env] \
CLOUDFLARE_ACCOUNT_ID=3b1af24a7513b520e418d7e707f6491e \
npx wrangler pages deploy dist/client --project-name=petzdeals
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
