# Connectors

> Skills use `~~category` placeholders instead of specific tool names. **Every skill runs at Tier 1 with zero external dependencies** — paste data manually, or pull it yourself from the free/public sources below. MCP servers (further down) are an optional Tier 2/3 convenience, never required.

All endpoints below were verified against primary vendor/source docs (2026-05; re-verified 2026-07 with each product's **official documentation linked inline** — click the source name in any row). If a call 404s, re-check the linked doc — vendors move endpoints.

## Bundled helpers — run the data fetch locally (zero-dependency)

For the bundle-able categories the repo ships small **Python-3-stdlib** helpers under [`scripts/connectors/`](scripts/connectors/README.md) — no `pip`, no key (except where noted). They turn the recipes below into one command, so a skill can pull real data itself instead of asking you to paste it. Run from the repo root:

| Capability | Helper | Needs |
|---|---|---|
| Crawl a site (→ page records) | `crawl.py <url>` | — |
| On-page audit (title/meta/headings/canonical/JSON-LD) | `onpage.py <url>` | — |
| robots.txt eval + AI-bot check | `robots.py <url> --check-ai-bots` | — |
| sitemap / sitemap-index / llms.txt | `sitemap.py <url>` | — |
| Internal-link graph (orphans / depth / internal PageRank) | `crawl.py … \| linkgraph.py -` | — |
| Page speed + Core Web Vitals | `psi.py <url>` | free key for automation |
| Structured-data extract + validate (+ FAQ/HowTo deprecation) | `schema_lint.py <url>` | — |
| Entity → Wikidata QID + claims | `kg.py reconcile "<name>"` | — |
| Archive history / change tracking | `wayback.py <url>` | — |
| Domain-authority signal | `openpagerank.py <domain> --key …` | free key |
| Keyword ideas (⚠️ unofficial endpoint) | `suggest.py "<seed>" --expand` | — |
| Live web SERP (keyless) | `firecrawl.py search "<query>" --limit 10` | — (optional key) |
| Rendered-page scrape for JS-heavy pages / site URL map | `firecrawl.py scrape <url>` · `firecrawl.py map <domain>` | — (optional key) |
| AI answer engine + citation probe / news search / URL extract (keyless) | `tavily.py search "<query>" --answer` · `tavily.py extract <url>` | — (optional key) |
| Email-auth DNS records — SPF/DMARC/BIMI/MX + DKIM-selector probes (DoH) | `doh.py auth <domain>` · `doh.py query <name> --type TXT` | — |
| Entity/topic attention series (Wikipedia pageviews) | `pageviews.py "<Article>" --months 12` | — |
| Global news mentions + volume trend (GDELT) | `gdelt.py '"<brand>"' --days 30` (⚠️ ≥5s between calls) | — |
| Brand / mention RSS | `rss_monitor.py <feed-url>` | — |
| Email ESP automation — domain-auth status / seed-test send / suppression sync / broadcasts (Resend) | `resend.py domains` · `resend.py seed …` (mutating commands dry-run by default, `--live` to execute) | free key |
| Before/after deltas (measurement loop) | `… \| ledger.py record <target> --source <name>` → `ledger.py diff <target> --source <name>` | — |

See [scripts/connectors/README.md](scripts/connectors/README.md) for the full list, the safety contract, and what intentionally stays external (proprietary / own-data → MCP/API).

**Measurement loop.** Most helpers above are point-in-time. Pipe any of them into `ledger.py record` to keep a local, git-diffable time series per target, then `ledger.py diff` / `ledger.py trend` to compute real movement — so a skill reports a measured delta instead of an estimated one. This is the spine the monitor-phase skills (rank-tracker, performance-monitor) and technical-seo-checker read for baselines. **Before trusting any movement, read [references/measurement-protocol.md](references/measurement-protocol.md)** — it defines which signals are minute-level proxies vs week-scale outcomes, and why outcome deltas need a control group to attribute.

## Free & public data sources (no paid tool, no MCP)

The fastest way to keep a skill zero-dependency is to feed it data from a free, first-party, or keyless public endpoint, then paste the response when the skill asks for the matching `~~category` data.

### Your own site — first-party, free

| Need (`~~category`) | Source | Endpoint / how | Auth | Free limit |
|---|---|---|---|---|
| Keywords + rankings (`~~SEO tool`, `~~search console`) | [Google Search Console Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) | `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query` (URL-encode siteUrl, or use `sc-domain:example.com`) | OAuth 2.0, scope `https://www.googleapis.com/auth/webmasters.readonly` | 1,200 queries/min per site |
| Index status per URL (`~~search console`) | [GSC URL Inspection API](https://developers.google.com/webmaster-tools/v1/urlInspection.index/inspect) — note the **newer** host, separate from webmasters/v3 | `POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect` (`inspectionUrl`, `siteUrl`) — verdict, coverage state, last crawl, canonical, mobile/rich-result checks | OAuth 2.0, same scope | 2,000 inspections/day per property |
| Keywords + rankings on Bing | [Bing Webmaster Tools API](https://learn.microsoft.com/en-us/bingwebmaster/getting-access) | REST API; key from BWT → Settings → API Access | `apikey` query param **or** [OAuth Bearer](https://learn.microsoft.com/en-us/bingwebmaster/oauth2) (token `https://www.bing.com/webmasters/oauth/token`) | free account |
| Traffic & behavior (`~~analytics`) | [Google Analytics Data API (GA4)](https://developers.google.com/analytics/devguides/reporting/data/v1) | `POST https://analyticsdata.googleapis.com/v1beta/{property=properties/*}:runReport` (`v1beta` is the current documented surface) | OAuth 2.0, scope `https://www.googleapis.com/auth/analytics.readonly` | 200,000 tokens/property/day |
| Backlinks to your site (`~~link database`) | [GSC Links report](https://support.google.com/webmasters/answer/9049606) | Search Console UI → Links → Export top linking sites | GSC login | free |

### Public / keyless — any site

| Need (`~~category`) | Source | Endpoint / how | Auth | Limit |
|---|---|---|---|---|
| Keyword ideas / autocomplete (`~~SEO tool`) | Google Suggest — **⚠️ unofficial, undocumented** | `https://suggestqueries.google.com/complete/search?client=chrome&q=QUERY&hl=en&gl=US` | none | undocumented; backoff on 429/503, may change without notice |
| Live web SERP + rendered scrape (`~~SEO tool`, `~~web crawler`) | [Firecrawl](https://docs.firecrawl.dev) — [keyless since the 2026 launch](https://www.firecrawl.dev/blog/firecrawl-keyless-launch) | `POST https://api.firecrawl.dev/v2/search` / `/v2/scrape` — bundled as `firecrawl.py` (local robots.txt pre-flight built in) | none (optional `FIRECRAWL_API_KEY` raises limits) | ~1,000 free credits/mo |
| AI answer engine + scored search + extract (`~~AI monitor` proxy, `~~SEO tool`, `~~trend database`) | [Tavily](https://docs.tavily.com/api-reference/endpoint/search) — [keyless mode](https://docs.tavily.com/documentation/keyless) | `POST https://api.tavily.com/search` / `/extract` (header `X-Tavily-Access-Mode: keyless`) — bundled as `tavily.py` (robots pre-flight on extract) | none (optional `TAVILY_API_KEY`, 1,000 credits/mo free) | keyless rate-limited; `/crawl`/`/map`/`/research` key-only |
| Email-auth DNS records (`~~email platform` auth signals) | [Google](https://developers.google.com/speed/public-dns/docs/doh/json) / [Cloudflare](https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/) DNS-over-HTTPS | `GET https://dns.google/resolve?name=…&type=TXT` (Cloudflare fallback) — bundled as `doh.py auth` | none | generous; public resolvers |
| Entity/topic attention series (`~~trend database`, `~~knowledge graph` adjacent) | [Wikimedia Pageviews API](https://wikimedia.org/api/rest_v1/#/Pageviews%20data) | `GET https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/…` — bundled as `pageviews.py` | none — descriptive User-Agent required | ~100 req/s ceiling; data lags ~1 day |
| Global news mentions (`~~brand monitor`) | [GDELT DOC 2.0](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) | `GET https://api.gdeltproject.org/api/v2/doc/doc?query=…&format=json` — bundled as `gdelt.py` | none | **≥5s between requests**; throttles shared IPs (plain-text notice or 429) |
| Subdomain discovery via certificate transparency (`~~web crawler` aux) | [crt.sh](https://crt.sh) (Sectigo; community-documented) | `GET https://crt.sh/?q=%25.example.com&output=json` — dedupe `name_value` | none | slow, occasionally times out; be gentle |
| HTML validity (`~~web crawler` aux) | [W3C Nu validator](https://github.com/validator/validator/wiki/Service-%C2%BB-HTTP-interface) | `GET https://validator.w3.org/nu/?doc=URL&out=json` | none | be gentle |
| Post/video metadata (`~~social platform analytics` partial) | [oEmbed](https://oembed.com) — YouTube · [TikTok](https://developers.tiktok.com/doc/embed-videos) · X | `https://www.youtube.com/oembed?url=…` · `https://www.tiktok.com/oembed?url=…` · `https://publish.twitter.com/oembed?url=…` | none | metadata only (title/author/thumbnail) — no follower/engagement metrics; Instagram oEmbed requires a token |
| Tech/forum heat (`~~trend database`) | [Hacker News Algolia](https://hn.algolia.com/api) | `GET https://hn.algolia.com/api/v1/search?query=…` | none | generous |
| Domain authority signal (`~~link database`) | [Open PageRank](https://www.domcop.com/openpagerank/documentation) | `GET https://openpagerank.com/api/v1.0/getPageRank?domains[]=example.com` | free key in header `API-OPR: KEY` | 10,000 calls/hr, ≤100 domains/call (domain-rank scores, not raw link lists) |
| Inbound links / web graph (`~~link database`, `~~web crawler`) | [Common Crawl CDX index](https://commoncrawl.org/get-started) | `https://index.commoncrawl.org/CC-MAIN-YYYY-WW-index?url=URL&output=json` — crawl list at `https://index.commoncrawl.org/collinfo.json` | none | shared server, keep < 10 req/s (expect `503 SlowDown`) |
| Historical pages / change tracking (`~~competitive intel`) | [Wayback Machine CDX API](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md) | `http://web.archive.org/cdx/search/cdx?url=URL&output=json` (matchType `exact`/`prefix`/`host`/`domain`) | none | be gentle |
| Entity / knowledge-graph facts (`~~knowledge graph`) | [Wikidata SPARQL](https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual) | `https://query.wikidata.org/sparql?query=...&format=json` (GET or POST) | none — **descriptive User-Agent required** | ~60s query CPU per 60s per IP (429 on excess) |
| Entity lookup via Google (`~~knowledge graph`) | [Google Knowledge Graph Search API](https://developers.google.com/knowledge-graph) — **⚠️ soft-migrating to [Cloud Enterprise KG](https://docs.cloud.google.com/enterprise-knowledge-graph/docs/search-api)** | `GET https://kgsearch.googleapis.com/v1/entities:search?query=...&key=KEY` | API key | 100,000 calls/day (no sunset date announced; prefer Wikidata for durable keyless access) |

### Page speed / Core Web Vitals — free (`~~page speed tool`)

| Data | Source | Endpoint | Auth | Limit |
|---|---|---|---|---|
| Lab Lighthouse score | [PageSpeed Insights API v5](https://developers.google.com/speed/docs/insights/v5/get-started) | `GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=URL&strategy=mobile` | key optional (recommended for automation) | — |
| Real-user field CWV (latest 28-day window) | [Chrome UX Report (CrUX) API](https://developer.chrome.com/docs/crux/api) | `POST https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=KEY` | Google Cloud API key (query param) | 150 queries/min (free; no paid increase) |
| Field CWV **time series** — up to 40 weekly points (~6 months) | [CrUX History API](https://developer.chrome.com/docs/crux/history-api) | `POST https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord?key=KEY` (`collectionPeriodCount` ≤ 40; updates Mondays) — a ready-made baseline series for the `ledger.py` measurement loop | same key | same quota |
| Local lab run | [Lighthouse CLI](https://github.com/GoogleChrome/lighthouse) | `npx lighthouse URL --output json --output-path=./lh.json` | none | — |

### Open-source / self-host / DIY

| Need (`~~category`) | Tool | How |
|---|---|---|
| Crawl, robots.txt, sitemaps, SERP, logs (`~~web crawler`) | [**advertools**](https://advertools.readthedocs.io) (Python, OSS) | `pip install advertools` — site crawl, `sitemap_to_df`, `robotstxt_test`, SERP analysis, log-file parsing |
| Desktop crawl (`~~web crawler`) | [Screaming Frog SEO Spider](https://www.screamingfrog.co.uk/seo-spider/) | free tier ≤ 500 URLs |
| Privacy analytics you own (`~~analytics`) | [**Plausible**](https://plausible.io/docs/stats-api) / [**Matomo**](https://developer.matomo.org/api-reference/reporting-api) (OSS, self-host) | Plausible Stats API v2: `POST https://plausible.io/api/v2/query` (`Authorization: Bearer KEY`, 600 req/hr); self-host uses the same path on your host |
| Schema / structured-data check (`~~schema validator`) | [validator.schema.org](https://validator.schema.org) · [Google Rich Results Test](https://search.google.com/test/rich-results) | **UI only — paste markup; no public API** |
| Brand / mention monitoring (`~~brand monitor`) | [Google Alerts](https://www.google.com/alerts) (RSS) · [F5Bot](https://f5bot.com) | free email/RSS alerts on brand or keyword mentions |
| Social/platform → RSS bridge (`~~social listening`) | [**RSSHub**](https://github.com/DIYgod/RSSHub) (OSS, self-host) | turns hundreds of platforms (incl. CN platforms) into RSS feeds `rss_monitor.py` can watch |
| Metasearch you own (`~~SEO tool` aux) | [**SearXNG**](https://docs.searxng.org) (OSS, self-host) | self-hosted metasearch with a JSON API — the self-host alternative to Firecrawl/Tavily search |
| AI-answer citation check (`~~AI monitor`) | Manual prompt-testing (ChatGPT / Perplexity / Google AI Overviews) · OSS GEO trackers · Tavily answer probe | **no free API for the big engines** — run target prompts and record which sources each engine cites over time; `tavily.py search --answer` gives a keyless Measured read for Tavily's own answer layer (a proxy for the others, label it Estimated) |

**Zero-tool DIY pattern:** for most technical and content checks you need nothing but `fetch` — pull `robots.txt`, `sitemap.xml`, `llms.txt`, and the page HTML directly, and paste them in.

## Tool Categories (placeholder → tools)

`Discipline` = which discipline(s) use the category (search / influencer / paid / both / all). `Agent default` = what an agent should reach for first at Tier 1 (use the free/own-data path unless the team already pays for a listed tool).

| Category | Placeholder | Discipline | Example paid tools | Free alternative (above) | Agent default |
|----------|-------------|------------|--------------------|--------------------------|---------------|
| SEO Platform | `~~SEO tool` | search | Ahrefs, Semrush, Moz, SISTRIX, SE Ranking | GSC + Google Suggest + Firecrawl live SERP | GSC + Suggest + `firecrawl.py search` (keyless) |
| Analytics | `~~analytics` | all | GA, Adobe Analytics, Plausible, Matomo | GA4 Data API / self-host Plausible | GA4 own-data |
| Search Console | `~~search console` | search | Google Search Console, Bing Webmaster | GSC + Bing WMT APIs | GSC (own) |
| AI Visibility | `~~AI monitor` | search | Otterly, Profound, Scrunch AI | manual prompt-testing + Tavily answer-citation probe (one engine, proxy) | manual prompt set + `tavily.py search --answer` |
| Web Crawler | `~~web crawler` | search | Screaming Frog, Sitebulb, Lumar | advertools / Screaming Frog free / DIY fetch / Firecrawl keyless (JS-rendered) | DIY fetch (`crawl.py`); JS pages → `firecrawl.py scrape` |
| Link Database | `~~link database` | search | Ahrefs, Majestic, Moz | Open PageRank + Common Crawl + GSC Links | Open PageRank + GSC |
| Competitive Intel | `~~competitive intel` | search | SimilarWeb, SpyFu, Semrush | Wayback CDX + Common Crawl + Firecrawl scrape/map | Wayback CDX + `firecrawl.py map` |
| Page Speed | `~~page speed tool` | search | GTmetrix, WebPageTest | PSI / CrUX / Lighthouse | PSI (keyless) |
| CDN | `~~CDN` | search | Cloudflare, Fastly, Akamai, CloudFront | response-header inspection (`curl -sI URL` → `cf-ray` / `x-served-by` / `x-cache` / `server`) + `dig CNAME host` for edge mapping + CrUX/PSI TTFB as the performance signal | header + DNS inspection (keyless) |
| Schema Validator | `~~schema validator` | search | — | validator.schema.org / Rich Results Test | Rich Results Test |
| Knowledge Graph | `~~knowledge graph` | both | Google KG API, CrunchBase | Wikidata SPARQL | Wikidata SPARQL |
| Local Listings | `~~local listings` | search | Google Business Profile, Yext, BrightLocal, Whitespark | GBP dashboard (own data, manual export) + manual NAP/citation check + [Nominatim/OSM geocoding](https://nominatim.org/release-docs/latest/api/Overview/) (keyless, 1 req/s + descriptive UA) | GBP own data (keyless) |
| Brand Monitor | `~~brand monitor` | both | Brand24, Mention, Brandwatch | Google Alerts / F5Bot / GDELT DOC API | Google Alerts RSS + `gdelt.py` (keyless) |
| CRM / Marketing | `~~CRM` | all | HubSpot, Salesforce, Marketo | — | manual CSV |
| Content / CMS | `~~content platform` / `~~CMS` | all | WordPress, Webflow, Contentful, Sanity, Notion | — | existing CMS |
| Communication | `~~team chat` | all | Slack, Teams, Discord | — | manual paste |
| Reporting | `~~reporting` | all | Looker Studio, Tableau, Power BI | — | Markdown report |

### Influencer / IMPACT categories

The influencer-marketing skills use these additional placeholders (plus `~~CRM`, `~~content platform`/`~~CMS`, `~~team chat`, and `~~reporting` shared with the table above). Every one works at Tier 1 — paste the data manually; the right-hand column is the keyless / own-data path. Categories marked Discipline=**both** are also used by the **paid** (Paid Ads) discipline — notably `~~ad platform`, `~~web analytics`, `~~ecommerce`, which paid scores from **own-account manual export** (keyed ad-platform APIs are opt-in Tier-2/3 MCP, never required).

| Category | Placeholder | Discipline | Example paid tools | Free / own-data path | Agent default |
|----------|-------------|------------|--------------------|----------------------|---------------|
| Influencer Database | `~~influencer database` | influencer | Modash, HypeAuditor, Upfluence, GRIN | manual creator CSV (handles + public metrics) | manual CSV (no public API) |
| Social Platform Analytics | `~~social platform analytics` | influencer | IG/TikTok/YouTube creator APIs, Dash Hudson | native creator dashboards (manual export of own/partner data) + keyless oEmbed post metadata (YouTube/TikTok/X — title/author/thumbnail only) | manual export (no public metrics API) |
| Social Listening | `~~social listening` | both | Brandwatch, Sprout Social, Talkwalker | Google Alerts / F5Bot / platform search | Google Alerts |
| Audience Intelligence | `~~audience intelligence` | influencer | HypeAuditor, Audiense, SparkToro | platform audience demographics (own/manual) | platform native (own) |
| Audience Overlap | `~~audience overlap` | influencer | Audiense, SparkToro | manual follower-sample comparison | manual sample |
| Trend Database | `~~trend database` | both | Exploding Topics, TrendTok | Google Trends / platform trending pages / Tavily news search / Wikipedia pageviews / HN Algolia | Google Trends RSS (`rss_monitor.py`) + `tavily.py search --topic news` + `pageviews.py` |
| Ad Platform | `~~ad platform` | both (influencer + paid) | Meta Ads, TikTok Ads, Google Ads | native ad manager (own data, manual export) | manual export (own); keyed API = opt-in MCP |
| Web Analytics | `~~web analytics` | both | GA4, Adobe Analytics, Plausible | GA4 Data API (own data) | GA4 own-data |
| E-commerce / Sales | `~~ecommerce` (bare alias covering both `~~ecommerce / sales platform` and `~~ecommerce / analytics`) | both | Shopify, WooCommerce, Stripe | platform order export (own data) | order CSV (own) |
| A/B Testing | `~~A/B testing platform` | both | Optimizely, VWO | server-side split / manual variant test | manual variant |
| Landing / Page Builder | `~~CMS / landing page builder` | both | Webflow, Unbounce, Instapage | static HTML / existing CMS | existing CMS |
| DAM / Asset Library | `~~DAM / asset library` | influencer | Bynder, Brandfolder | shared Drive / Dropbox folder | shared folder |
| Email / DM | `~~email/DM tool` | influencer | Klaviyo, Mailchimp, native DMs | native DM + manual email | manual DM |
| Compliance Reference | `~~compliance reference` | both | platform policy portals | [FTC 16 CFR §255](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255) / [Part 465](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) (public) | FTC public rule |
| Competitor Tracking | `~~competitor tracking` | influencer | Social Blade, BuzzSumo | manual competitor profile review | manual review |
| Customer Survey | `~~customer survey data` | influencer | Typeform, SurveyMonkey, Qualtrics | Google Forms | Google Forms |
| E-signature | `~~e-signature` | influencer | DocuSign, Dropbox Sign, PandaDoc | PDF + manual signature | manual PDF sign |

### Email / SEND categories

The email-marketing skills add one placeholder, `~~email platform` (the ESP), and reuse `~~web analytics` (GA4) + `~~ecommerce` for revenue truth. Every deliverability signal is **keyless** — it comes from public DNS, the free DMARC aggregate (RUA) report you already receive, or a seed-list test — so no keyed ESP API is ever required (keyed ESP APIs are opt-in Tier-2/3 MCP). The SEND framework scores from the user's **own-account manual export**, exactly like ad/ROAS.

**Bundled ESP automation — Resend ([resend.com](https://resend.com), free tier ~3,000 emails/mo).** When Resend is (or becomes) the ESP, the bundled [`scripts/connectors/resend.py`](scripts/connectors/resend.py) turns the `~~email platform` category into one command with a free-tier key (`RESEND_API_KEY`): `domains` (per-domain SPF/DKIM record status — Measured S1 evidence), `seed` (per-recipient seed-list test send for inbox-placement), `send`/`batch`/`broadcast-create`/`broadcast-send` (transactional + segment campaigns, `--scheduled-at`/`--at` for send-time), `contacts`/`suppress` (suppression sync mirroring the consent-registry), `segments`. **Safety:** it is the one bundled helper that can mutate external state, so every mutating subcommand is dry-run by default and executes only with `--live`; `send`/`seed`/`batch` carry an `Idempotency-Key` (auto-UUID, or `--idempotency-key` for a stable cross-run key) so retries can never double-send, and non-idempotent endpoints never auto-retry. **Consent boundary:** Resend's acceptable use is opted-in mail only — no purchased/scraped lists and no cold outbound (`cold-outbound-sequencer` stays manual-export); syncing a suppression to Resend never replaces the [consent-registry](protocol/consent-registry/SKILL.md) record, which stays the SSOT. Resend also ships an official remote MCP (`https://mcp.resend.com`, in `docs/mcp-catalog.json`) as the Tier-2/3 alternative to the CLI.

**Resend's wider AI-support surface** ([resend.com/docs/ai-onboarding](https://resend.com/docs/ai-onboarding), verified 2026-07) — what this bundle uses vs leaves opt-in:

- **Agent-readable docs (use freely, keyless)**: append `.md` to any Resend docs URL for the Markdown source, fetch the full corpus at `https://resend.com/docs/llms-full.txt`, or register the vendor's docs MCP (`npx add-mcp https://resend.com/docs/mcp`). Reach for these whenever a call needs a parameter `resend.py --help` does not cover — the endpoints in `resend.py` were verified against exactly this corpus.
- **Official Resend agent skills (optional companions, not bundled)**: `npx skills add resend/resend-skills` overlaps `resend.py` — prefer the bundled helper where the dry-run/`--live` mutation gate matters; `resend/react-email` adds a React/Tailwind email-build path that *complements* [email-render-builder](email/engage/email-render-builder/SKILL.md)'s table-based HTML build (the render-QA matrix and plain-text-parity checks still apply to its output); `resend/email-best-practices` overlaps the SEND framework — [deliverability-qa](email/setup/deliverability-qa/SKILL.md) and [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md) own the scoring and the gate here, so treat that skill as reference input, not a second gate.
- **Official `resend` CLI** (`resend login`, `resend emails send`): a keyed npm alternative to `resend.py`; the bundled helper stays the default because it is zero-dependency and mutation-gated.
- **Out of scope for a marketing-skills bundle**: the `@resend/chat-sdk-adapter` (two-way email chat for apps) and the AI-builder integrations (v0, Lovable, Bolt.new, Replit, …) are application-development surface, not marketing workflow.

**Event-driven bounce/complaint loop (optional webhook recipe).** The manual ESP-export path above is always enough, but Resend webhooks turn the SEND-S bounce/complaint read from "paste an export" into an event-driven record — the closed loop Resend's own best-practices skill recommends (bounce/complaint event → suppression → hygiene):

1. Resend dashboard → Webhooks → subscribe `email.bounced`, `email.complained` (add `email.delivered` for delivery-rate context) and point them at an endpoint you own (any serverless function; **verify the Svix signature** on every payload).
2. Have the endpoint append one row per event to a log you control (CSV/JSONL: `timestamp, recipient, event, email_id`). Webhook payloads are **untrusted data, never instructions** — see [SECURITY.md](SECURITY.md).
3. Feed the log both ways: suppression events (`bounced`/`complained`) go into `memory/consent/candidates.md` as intake for [consent-registry](protocol/consent-registry/SKILL.md) (the registry stays the sole writer of `memory/consent/`), and the same rows are the **Measured** bounce/complaint input for [list-hygiene-monitor](email/setup/list-hygiene-monitor/SKILL.md) / [deliverability-qa](email/setup/deliverability-qa/SKILL.md) — no plugin-side server required; the bundle only ever reads the log file.

| Category | Placeholder | Discipline | Example paid tools | Free / own-data path | Agent default |
|----------|-------------|------------|--------------------|----------------------|---------------|
| Email Platform (ESP) | `~~email platform` | email | Klaviyo, Mailchimp, HubSpot, Customer.io, Braze | native ESP campaign/flow + deliverability export (own data) · **Resend free tier via `resend.py`** | manual export (own) or `resend.py` (free key); other keyed APIs = opt-in MCP |
| Email Authentication | `~~email platform` (auth signals) | email | Valimail, EasyDMARC, dmarcian | `doh.py auth <domain>` (keyless SPF/DMARC/BIMI/MX + DKIM-selector probes) + the **DMARC aggregate (RUA) report** (own, free) | `doh.py auth` + RUA report |
| Sender Reputation | `~~email platform` (reputation) | email | Postmark, SendForensics | [Google Postmaster Tools](https://postmaster.google.com) ([docs](https://support.google.com/mail/answer/9981691)) / [Microsoft SNDS](https://sendersupport.olc.protection.outlook.com/snds/) (own data) | Postmaster/SNDS (own) |
| Inbox Placement | `~~email platform` (seed test) | email | GlockApps, Mailtrap, Litmus | manual seed-list send across own inbox providers | manual seed test |

## How placeholders work

A skill might say: *"Pull keyword rankings from `~~SEO tool` and cross-reference with `~~search console` impressions."* If you use Ahrefs + Google Search Console, read it as Ahrefs + GSC. If you use no paid tool, read it as "the Search Console Search Analytics API (above)" — or just paste the data.

## Optional MCP servers (Tier 2/3 automation)

[`docs/mcp-catalog.json`](docs/mcp-catalog.json) is a **copy-paste reference** of official remote HTTP MCP endpoints (plus one self-hosted entry, OpenSEO) — it is **opt-in, not auto-registered**. The catalog is deliberately kept outside the plugin-root `.mcp.json` path that Claude Code auto-discovers (and `plugin.json` carries no `mcpServers` key), so installing the plugin does NOT add 15 servers to your `/mcp` list or trigger any auth prompts. To enable any of these, copy the entries you want into your own host/user MCP config; auth happens interactively on first use. MCP automates retrieval but is never required — the free sources above cover the same data.

**SEO data** (endpoints verified 2026-05; vendor MCP docs linked + re-checked 2026-07):

| Vendor (→ official MCP docs) | Endpoint (`docs/mcp-catalog.json`) | Transport | Auth | Cost model | Sample tools |
|--------|------------------------|-----------|------|------------|--------------|
| [Ahrefs](https://docs.ahrefs.com/en/mcp/docs/introduction) | `https://api.ahrefs.com/mcp/mcp` | streamable HTTP | API key (MCP scope; Lite+ plan) | subscription | keyword & backlink data, site audit |
| [Semrush](https://developer.semrush.com/api/introduction/semrush-mcp/) | `https://mcp.semrush.com/v1/mcp` | streamable HTTP | OAuth, or `Authorization: Apikey KEY` | subscription | `organic_research`, `keyword_research`, `backlink_research` |
| [SE Ranking](https://seranking.com/api/integrations/mcp/) | `https://api.seranking.com/mcp` | streamable HTTP | OAuth or API key (`X-Api-Key`) | subscription | keyword/backlink/domain, AI-search visibility (160+ tools) |
| [SISTRIX](https://www.sistrix.com/api/connection-to-chatbot-ai/) | `https://api.sistrix.com/mcp` | HTTP | **OAuth login — since the 2026 rollout no API key is needed** ([changelog](https://www.sistrix.com/changelog/sistrix-mcp-servers/)) | subscription | `domain`, `keyword`, `links`, `ai` modules |
| [SimilarWeb](https://developers.similarweb.com/docs/similarweb-mcp) | `https://mcp.similarweb.com` | HTTP | OAuth / key | subscription | traffic estimates, competitive intel |
| [OpenSEO](https://github.com/every-app/open-seo) (self-hosted) | `https://<your-host>/mcp` (edit your copied entry) | streamable HTTP | none (local Docker) / OAuth (Cloudflare) | **free app + pay-as-you-go data** | `research_keywords`, `get_ranked_keywords`, `get_serp_results`, `find_serp_competitors`, `get_domain_overview`, `get_backlinks_overview`, `get_search_console_performance`, local-SERP/Maps tools |

**Cost model — read before enabling.** The five vendors above are **subscription** (flat monthly fee for plan-gated API access). OpenSEO is the one **pay-as-you-go** option: the app is free and self-hosted, and it bills only the underlying [DataForSEO](https://dataforseo.com) API calls you actually make — so it fits the free/keyless-first ethos better than a subscription suite while still returning real SERP/keyword/backlink data.

**OpenSEO — self-hosted full SEO suite ([github.com/every-app/open-seo](https://github.com/every-app/open-seo), open source).** Run it via Docker (single-user, no auth — local only) or Cloudflare Workers (OAuth, team-ready, free plan compatible), connect your own DataForSEO key, and the app exposes an MCP server at `/<host>/mcp`. Set the host in the `openseo` entry you copied from `docs/mcp-catalog.json` into your MCP config (placeholder ships as `your-openseo-host.example`). It natively reads Google Search Console (`get_search_console_performance`), which makes the [keyword-research](seo-geo/research/keyword-research/SKILL.md) striking-distance loop and rank tracking first-party. Indicative DataForSEO spend (vendor pay-as-you-go pricing, verify current rates — $1 free starter credit, $50 min top-up as of early 2026):

| Task (×100 requests) | Approx. cost |
|---|---|
| Keyword research, 150 results/seed | ~$3.50 |
| Keyword research, 500 results/seed | ~$7.00 |
| Domain overview (200 ranked keywords) | ~$4.01 |
| Backlinks domain search | ~$6.34 |
| Track 100 keywords weekly at depth 50 | ~$1.20 / month |

**Free Google data via MCP** (not shipped in `docs/mcp-catalog.json` — these run locally and need your own Google credentials):

- **Google Analytics** — official ([github.com/googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)): `pipx run analytics-mcp`, stdio, ADC scope `analytics.readonly`; tools `run_report`, `run_realtime_report`, `get_account_summaries`.
- **Google Search Console** — community ([github.com/AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc), MIT): `uvx mcp-search-console`, stdio, OAuth or service account; tools `get_search_analytics`, `inspect_url_enhanced`, `list_properties`.

**Infra / CMS / CRM / comms** (listed in `docs/mcp-catalog.json` as opt-in references, official remote endpoints, OAuth on first use): Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack. See each vendor's MCP docs for its current tool list.

**Email (`~~email platform`)**: **Resend** — official remote MCP at `https://mcp.resend.com` (in `docs/mcp-catalog.json`; OAuth in web clients, or Bearer API key). Tools cover send/batch/schedule, contacts + broadcasts, domain verification, and webhooks — the Tier-2/3 twin of the bundled [`scripts/connectors/resend.py`](scripts/connectors/resend.py) CLI, which covers the same surface with a free-tier key and dry-run-by-default sends.

**Crawl / SERP (`~~web crawler`, `~~SEO tool`)**: **Firecrawl** — official remote MCP at `https://mcp.firecrawl.dev/v2/mcp` (in `docs/mcp-catalog.json`) — works **keyless**: no key or auth at all on the ~1,000-credit/mo free tier (a key raises limits). Tools cover search/scrape/map/crawl — the Tier-2/3 twin of the bundled [`scripts/connectors/firecrawl.py`](scripts/connectors/firecrawl.py), which adds a local robots.txt pre-flight the hosted MCP does not perform for you.

**AI search / answer citations (`~~AI monitor` proxy, `~~SEO tool`)**: **Tavily** — official remote MCP at `https://mcp.tavily.com/mcp/` (in `docs/mcp-catalog.json`), also **keyless** (`tavily-search` + `tavily-extract` tools, no auth required; a key lifts the rate limit). The Tier-2/3 twin of the bundled [`scripts/connectors/tavily.py`](scripts/connectors/tavily.py), which adds the local robots pre-flight on extract.

**Third URL-to-markdown fallback**: **Jina Reader** — prepend `https://r.jina.ai/` to any URL (keyless, ~20 RPM; a free key raises to 500+ RPM), official remote MCP at [github.com/jina-ai/MCP](https://github.com/jina-ai/MCP). Overlaps Firecrawl/Tavily, so it is deliberately **not** bundled or wired into skills — use it to spread load when the other two keyless tiers are rate-limited.

To enable a server, copy its entry from `docs/mcp-catalog.json` into your host/user MCP config. The catalog is a curated reference, not an active registration — it deliberately does not live at the plugin root as `.mcp.json` (which Claude Code would auto-register); keep it in sync only when contributing a new default endpoint.

## Progressive enhancement tiers

| Tier | Integration | Experience |
|------|-------------|------------|
| **Tier 1** | None | Paste data, or pull it from the free sources above. Skills provide the full analysis framework. |
| **Tier 2** | A free first-party API or one MCP | Automatic retrieval of your own GSC/GA4/CWV data. |
| **Tier 3** | Full MCP set | Fully automated multi-source workflows. |

Every skill works at Tier 1. Connecting tools only automates data retrieval.

## Environment variables

Soft dependencies — everything works without them. These are the only env vars the **bundled
stdlib connectors** actually read (both optional; the connectors fall back to keyless/lower-quota mode):

| Variable | Read by | Purpose |
|----------|---------|---------|
| `OPENPAGERANK_API_KEY` | `scripts/connectors/openpagerank.py` | Open PageRank domain-rank lookups (free key) |
| `PAGESPEED_API_KEY` | `scripts/connectors/psi.py` | Higher PageSpeed Insights quota (works keyless at low volume) |
| `RESEND_API_KEY` | `scripts/connectors/resend.py` | Resend ESP automation (free-tier key; mutating subcommands additionally require `--live`) |
| `FIRECRAWL_API_KEY` | `scripts/connectors/firecrawl.py` | Optional — `scrape`/`search` work keyless (~1,000 credits/mo); a key raises limits and covers `map`/`crawl` |
| `TAVILY_API_KEY` | `scripts/connectors/tavily.py` | Optional — `search`/`extract` work keyless (rate-limited); a free key (1,000 credits/mo) lifts the limit |

The opt-in MCP servers do not use env vars here: most (Semrush, SE Ranking, SISTRIX, SimilarWeb, Cloudflare, Vercel, Webflow, Sanity, Contentful) use **OAuth** at first use; Ahrefs uses an in-client MCP key. The free Google APIs use OAuth (GSC/GA4) or a key (PSI/CrUX/Knowledge Graph) you supply at call time.

## Freshness & caveats

- **Google Knowledge Graph Search API** is in soft-migration to Cloud Enterprise Knowledge Graph (no sunset date). Prefer **Wikidata SPARQL** for durable, keyless entity data.
- **Google Suggest/autocomplete** is unofficial and undocumented — it may change or rate-limit without notice; add exponential backoff.
- **Common Crawl**'s shared index server has been rate-limited since Nov 2023 — expect `503 SlowDown`; run your own index for heavy use (data is free on AWS S3 `commoncrawl`).
- **Google Rich Results Test** and **validator.schema.org** expose no public API — paste markup into the UI.
- **AI-citation visibility** has no free API from any engine — the realistic free method is manual prompt-testing recorded over time (plus the Tavily answer probe as a single-engine proxy).
- **SISTRIX MCP** dropped its API-key requirement in 2026 — auth is now an OAuth login for any SISTRIX account; older setup guides mentioning `X-API-Key` are stale.
- **CrUX History API** returns weekly windows updated Mondays (~04:00 UTC, data through the prior Saturday) — align `ledger.py` comparisons to the same weekday to avoid phantom deltas.
