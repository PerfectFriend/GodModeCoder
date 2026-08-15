---
name: treasury-ledger
description: "SQLite ledger for Thaler: 70% Ag, 30% premium, NFT dividends"
trigger: Need immutable supply tracking, silver deposit minting, pro-rata dividend distribution.
---
# Treasury Ledger (Thaler / TL Token Economy)

## Overview
Immutable SQLite-backed ledger for the Thaler (TL) currency:
- **70% silver-backed**: 70 TL per troy ounce of physical silver in vault
- **30% utility premium**: minted to treasury for dividends, ops, development
- **NFT Banknotes**: 8 denominations (14, 88, 111, 228, 420, 666, 1024, 1488 TL) receive pro-rata dividends

## Core Components

### Ledger (`internal/treasury/ledger.go`)
- **Schema**: `tl_entries` (append-only), `tl_state` (key/value supply aggregates)
- **Entry types**: mint, burn, transfer, dividend, stake, unstake, nft_lock, nft_unlock
- **Supply tracking**: total_minted, total_burned, circulating, in_nfts, staked, treasury, backing_silver (oz * 1e8)
- **SilverDeposit(traderID, oz, batchID, assayCert)**: mints 70 TL/oz + 30% to treasury
- **DividendDistribute(denomination, totalTL, holders)**: pro-rata by (count × denomination) weight

### API Endpoints (`internal/api/treasury.go`)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/treasury/supply` | user | Current supply state |
| GET | `/api/treasury/entries` | user | Audit trail (limit, offset, type filter) |
| POST | `/api/treasury/silver-deposit` | admin | Trader delivers silver → mints TL |
| POST | `/api/treasury/dividend` | admin | Distribute dividends to NFT holders |

### Frontend (dashboard.html → Wallet tab)
- NT gas balance + staking
- Thaler: available / in NFTs / staked / total
- Silver Vault: physical oz, TL minted, backing ratio, next batch estimate
- NFT Portfolio: 8 denominations with count + dividend tracking
- Mint NFT UI: denomination selector + quantity → cost preview
- AI Exchanger: top-20 aggregate, 2.28% fee, quote + execute
- Top-10 multi-currency accounts

## Verification Commands
```bash
# Check supply
curl -b cookies.txt http://localhost:8080/api/treasury/supply

# Silver deposit (admin)
curl -b cookies.txt -X POST http://localhost:8080/api/treasury/silver-deposit \
  -H "Content-Type: application/json" \
  -d '{"trader_id":"trader1","oz":"1000","batch_id":"batch-2026-001","assay_cert":"SHA256:..."}'

# Dividend distribution (admin/cron)
curl -b cookies.txt -X POST http://localhost:8080/api/treasury/dividend \
  -H "Content-Type: application/json" \
  -d '{"denomination":1488,"total_tl":"50000000000000","holders":{"addr1":"5","addr2":"3"}}'
```

## Session 2026-08-05 Implementation Details

### Exact API Endpoints Created
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/treasury/supply` | user | Current supply state (total_minted, total_burned, circulating, in_nfts, staked, treasury, backing_silver, last_batch_id, last_batch_time) |
| GET | `/api/treasury/entries` | user | Audit trail with filters: `?type=&limit=&offset=` |
| POST | `/api/treasury/silver-deposit` | admin | `{trader_id, oz, batch_id, assay_cert}` → mints 70 TL/oz + 30% to treasury |
| POST | `/api/treasury/dividend` | admin | `{denomination, total_tl, holders:{addr:count}}` → pro-rata payout |

### Mint Logic (70% silver / 30% premium)
```go
// SilverDeposit(traderID, oz, batchID, assayCert)
amount = oz * 70_00000000  // 70 TL per oz * 1e8 decimals
// 70% → circulating, 30% → treasury
treasuryPremium = amount * 30 / 100
circulating += amount
treasury += treasuryPremium
backingSilver += oz * 1e8
```

### Dividend Pro-Rata Formula
```go
// DividendDistribute(denomination, totalTL, holders)
totalWeight = Σ(count × denomination)
for addr, count in holders:
    weight = count × denomination
    share = totalTL × weight / totalWeight
    // record dividend entry per holder + treasury burn entry
```

### NFT Denominations (8 fixed)
`[14, 88, 111, 228, 420, 666, 1024, 1488]` TL — weight = count × denomination

### Verified Live (2026-08-05)
- 100 oz deposit → 7B TL minted + 2.1B to treasury
- 1488 TL dividend → 3 holders pro-rata
- Audit trail: `/api/treasury/entries?type=dividend&limit=5` returns immutable entries

## Pitfalls & Fixes
- **big.Int handling**: Use `big.NewInt(0)` not `var x big.Int` for accumulator variables
- **Decimal precision**: All amounts stored as string with 8 decimals (1 TL = 100,000,000 base units)
- **Pro-rata dividend math**: weight = count × denomination; share = totalDividend × weight / totalWeight
- **Admin-only endpoints**: Check `X-Role: admin` header
- **SQLite path**: `dataDir/tl_ledger.db` — survives restarts, append-only audit trail

## Integration Points
- Wallet page reads `/api/wallet/state` (includes TL balances, NFT counts, vault backing)
- Dividend cron: daily scan vault → compute 30% premium available → distribute to NFT holders
- Silver oracle: live spot price polling (5min) → triggers auto-mint when new silver purchased

## Future Extensions
- On-chain anchor (periodic merkle root to BTC/ETH)
- Multi-asset treasury (BTC, ETH, XMR reserves)
- DAO governance for dividend policy
- Auditor role (read-only access to entries)