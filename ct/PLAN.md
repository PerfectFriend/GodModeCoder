# HOT
# CyberTarot — Execution Plan (10 Items)

## Item 1: Initialize TDD test suite
- **Goal**: Create vitest config and write first failing test for shuffleDeck
- **RED**: Watch test fail because no test infrastructure yet
- **GREEN**: Minimal code to pass test
- **REFACTOR**: Clean up after passing

## Item 2: Fix shuffleDeck to use full 78-card deck
- **Goal**: Ensure shuffleDeck draws from all 78 cards, not just 22 majors (per EVOLUTION_PLAN.md section 1.4 Unit tests)
- Current issue: DECK imported from tarot-deck.json may have issues
- **RED**: Write test that fails — should see >22 unique cards in 100 draws
- **GREEN**: Fix shuffleDeck implementation

## Item 3: Fix rollRarity rarity distribution
- **Goal**: Ensure rollRarity distributes ~70/25/5 (rare:epic:legendary) per EVOLUTION_PLAN.md
- Current: Common has weight 0 but still possible
- **RED**: Test fails — common appears in rollRarity results
- **GREEN**: Fix weight distribution logic

## Item 4: Fix ManaWell tickWell dry/fill cycle
- **Goal**: Ensure ManaWell tickWell correctly handles fill/dry/refill cycle per spec (6h fill, 6h dry)
- Current: Complex state transitions in magicWell.ts
- **RED**: Write test that fails — observe incorrect tickWell behavior
- **GREEN**: Fix tickWell logic

## Item 5: Add localStorage persistence tests
- **Goal**: Test that useTarot hook persists and restores state from localStorage
- **RED**: Test fails — persistence not verified
- **GREEN**: Fix save/load state in useTarot.ts

## Item 6: Fix card orientation property
- **Goal**: Ensure every drawn card has orientation property (upright/reversed)
- **RED**: Test fails — missing orientation
- **GREEN**: Fix shuffleDeck mapping

## Item 7: Add interpretation service tests
- **Goal**: Test mockInterpret returns valid JSON structure
- **RED**: Test fails — mock not working
- **GREEN**: Fix mock or integrate Ollama

## Item 8: Fix mint cost deduction
- **Goal**: Ensure mint deducts correct balance based on rarity cost
- **RED**: Test fails — balance not updated correctly
- **GREEN**: Fix mint callback in useTarot.ts

## Item 9: Add collection management tests
- **Goal**: Test sellCard removes card and adds 60% cost to balance
- **RED**: Test fails — collection/sell not working
- **GREEN**: Fix sellCard callback

## Item 10: Full test suite passes with no regressions
- **Goal**: Run all vitest tests, ensure 100% pass
- **RED**: Some tests failing
- **GREEN**: `vitest run --config vitest.config.ts` — all green