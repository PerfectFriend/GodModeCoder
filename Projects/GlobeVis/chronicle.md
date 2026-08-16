# GlobeVis Evolution Chronicle

## Session History

### 2026-08-03 — Initial Discovery & Strategic Analysis
**Author:** Master Inquisitor  
**Session:** Current (default profile)  
**Event:** Charles Schreiber proposed GlobeVis project via Telegram

**Charles's Proposal:**
- Product: GlobeVis.net — Real-time 3D Visitors Globe
- Target: WordPress site owners + HTML/PHP sites
- Free WP plugin: ~1,000 installs (WP.org shows 60+)
- Lifetime license: $12, conversion ~1% (1 paid per 100 free)
- Needs: Logging, 2 products (WP + HTML/PHP), Stripe payments
- Offer: Marketing partner gets 50% split, Charles provides product + logs access

**Strategic Analysis Delivered:**
- Market assessment: TAM ~$1B, SAM ~$1.1B
- Pivot recommendation: Lifetime $12 → SaaS $19-149/mo
- Free plugin = lead gen, Cloud Dashboard = product
- 3 financial scenarios modeled (Pessimistic/Realistic/Aggressive)
- GTM strategy: WP.org funnel + Affiliate flywheel + Viral badge
- Phase 0-3 roadmap with gates
- Decision framework with Continue/Pivot/Kill thresholds

---

### 2026-08-07 — Marketing Plan Document Created
**Author:** Master Inquisitor / Hermes Agent  
**Session:** Current (default profile)  
**Event:** Full marketing plan written to `marketing-plan.md` (23 KB)

**Deliverable:** `C:/Users/tomas/marketing-plan.md`
- TAM/SAM/SOM analysis
- Unit economics (LTV $945, CAC target <$315)
- 3 scenario projections with monthly tables
- Scenario comparison summary
- Recommended hybrid path (Realistic with Aggressive optionality)
- Detailed GTM roadmap (Phase 0-3)
- Weekly metrics dashboard (11 metrics)
- Risk register (8 risks)
- Decision framework with monthly gates
- Immediate next steps checklist for both partners
- Financial model assumptions appendix

---

### 2026-08-07 — Project Extracted to Obsidian Vault
**Author:** Hermes Agent  
**Session:** Current (default profile)  
**Event:** GlobeVis project saved as standalone project in Obsidian Vault for GodModeCoder compatibility

**Files Created:**
1. `C:/Vault/Projects/GlobeVis/GlobeVis_Evolution_Report.md` — Full strategic report (Markdown, 27 KB)
2. `C:/Vault/Projects/GlobeVis/graph.yaml` — Graph evolution format with:
   - Project node with metrics and 4 phases
   - 4 phase nodes with KPIs, budgets, timelines
   - 4 hiring nodes (Support, Content, Growth, Enterprise AE)
   - 5 milestone nodes with criteria and owners (G1-G5)
   - 2 contributor nodes (Charles 50%, Marketing Partner 50%)
   - 8 risk nodes with probability/impact/mitigation
   - Edges: contains, requires, has_milestone, precedes, contributed_by, has_risk
   - Pulse config: weekly cadence, Monday reviews, 11 metrics tracked, 5 gate reviews, 3 scenario gates
   - Chronicle: 3 session history entries
3. `C:/Vault/Projects/GlobeVis/chronicle.md` — This file

**Verification:** All files validated — YAML syntax valid, all 24 nodes and 26 edges cross-reference correctly, all required sections present.

---

## Next Actions (When Charles Ready)

### Immediate (Phase 0 — Week 1-4)
- [ ] **Charles:** Stripe test keys, Database URL, WP.org SVN access, Vercel/Netlify access
- [ ] **Charles:** Rewardful/FirstPromoter API key, Resend/Postmark API key + domain
- [ ] **Charles:** Sentry / Plausible / Better Uptime DSN
- [ ] **Both:** Confirm tech stack (Node/Go/Python? Next.js? Prisma/Drizzle? Postgres?)
- [ ] **Day 1-2:** Stripe Billing core (Products, Prices, Checkout, Portal, Webhooks)
- [ ] **Day 3-4:** Multi-tenant DB schema (organizations, sites, events, api_keys, alerts, team_members)
- [ ] **Day 5:** Dashboard API (orgs → sites → globe + top100 + sparkline)
- [ ] **Day 6-7:** WP Plugin v2 "Connect to Cloud" + Landing page
- [ ] **Day 7:** Soft launch to 50 beta users

### Phase 1 Gates (Month 3)
**G2: PMF Validated** — Continue threshold:
- 100+ paying customers
- MRR ≥ $3,500
- Blended CAC < $80
- Monthly churn < 4%
- 20+ active affiliates
- Free→Trial ≥ 3%, Trial→Paid ≥ 18%

### Scenario Switch Gates
| Gate | When | Criteria → Action |
|------|------|-------------------|
| **Gate A** | Month 3 | $5K MRR + CAC <$80 + LTV >$800 + Churn <4% → Open Aggressive tap |
| **Gate B** | Month 6 | $15K MRR + Shopify live + 20 affiliates + Paid ads ROAS >3 → Scale to Aggressive budget |
| **Gate C** | Month 12 | $65K MRR → Series A decision ($1-2M at $10M+ valuation) |

---

## Key Metrics Baseline (August 2026)
- **Free WP Installs:** ~1,000
- **Daily Active Sites:** ~200
- **Pro Subscribers:** ~10
- **MRR:** ~$0
- **Platforms:** WordPress, HTML/PHP
- **Chains:** N/A (Web2 product)

## Targets
| Period | Realistic | Aggressive |
|--------|-----------|------------|
| **Q4 2026 (Month 3)** | $3.5K MRR, 100 paying | $5K MRR, 150 paying |
| **Month 6** | $10K MRR, 300 paying | $14K MRR, 400 paying |
| **Month 12** | $21K MRR, 600 paying | $66K MRR, 1,900 paying |
| **Year 3** | $256K ARR, $72K/yr each | $3.9M ARR, $400K+/yr each |

---

## Strategic Positioning
**Current:** WP plugin $12 lifetime, 1% conversion, no dashboard  
**Pivot:** B2B SaaS $19-149/mo — Visual Real-time Analytics Category King  
**Moat:** Viral badge ("Powered by GlobeVis"), White-label, Agency workflow, Data history, Integrations, Brand  
**Distribution:** WP.org organic (60%) + Affiliate flywheel (25-35%) + Viral loops + Paid ads (Aggressive)  
**Exit:** Strategic acquisition (Hotjar, Contentsquare, SimilarWeb, Cloudflare, Datadog) — $1.5M (Realistic) to $40-60M (Aggressive)

---

## Partnership Terms (Agreed)
- **Charles Schreiber:** 50% equity — Product, Dev, Infrastructure
- **Marketing Partner:** 50% equity — GTM, Marketing, Partnerships, Fundraising
- **Profit Split:** 50/50 after expenses
- **Decision Making:** Consensus on strategy, Charles = product decisions, Marketing = GTM decisions
- **Kill Clause:** Graceful wind down, split assets/IP 50/50, no hard feelings

---

*Chronicle maintained per Graph Evolution Protocol v3.0 — pulse weekly, gates at milestones, chronicle per session.*