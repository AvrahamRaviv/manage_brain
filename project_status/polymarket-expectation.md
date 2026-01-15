# Polymarket Expectation

Repo: https://github.com/AvrahamRaviv/polymarket-expectation

## Current Status
- Status: wip
- Last update: 2026-01-15 14:14
- Default branch: main
- Archived: False

## Latest Changes (auto-generated)
<!-- PROJECT_LATEST_START -->
- Update README with comprehensive documentation

- Quick start all-in-one command
- Workflow diagram (train → find → evaluate)
- Nested CV with holdout documentation
- Find opportunities command
- Evaluate opportunities command
- Example results output
- Conservative and full grid search examples
- Updated project structure

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (3aa9aae, 2026-01-15 14:14)
<!-- PROJECT_LATEST_END -->

## History (auto-generated)
<!-- PROJECT_HISTORY_START -->
- 2026-01-15
  - Update README with comprehensive documentation
  
  - Quick start all-in-one command
  - Workflow diagram (train → find → evaluate)
  - Nested CV with holdout documentation
  - Find opportunities command
  - Evaluate opportunities command
  - Example results output
  - Conservative and full grid search examples
  - Updated project structure
  
  Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (3aa9aae, 2026-01-15)
- 2026-01-15
  - Update README with comprehensive documentation
- Quick start all-in-one command
- Workflow diagram (train → find → evaluate)
- Nested CV with holdout documentation
- Find opportunities command
- Evaluate opportunities command
- Example results output
- Conservative and full grid search examples
- Updated project structure
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (3aa9aae, 2026-01-15)
  - Add opportunity storage and evaluation features
1. Timestamped opportunity storage:
   - --export auto saves to opportunities/YYYY-MM-DD_HHMMSS.json
   - Creates opportunities/ folder automatically
   - Default for find-opportunities is now 'auto'
2. New evaluate-opportunities command:
   - Evaluates stored opportunities against actual outcomes
   - Fetches current market status from Polymarket API
   - Calculates P&L for resolved markets (WIN/LOSS)
   - Shows unrealized P&L for open positions
   - Summary with top/worst performers
Usage:
  python main.py find-opportunities --params-file cv.json
  # Wait some days...
  python main.py evaluate-opportunities opportunities/2026-01-15_150006.json
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (8031a1a, 2026-01-15)
  - Fix max_markets not respected when loading from cache
Cache now respects --max-markets limit instead of returning all cached markets.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (ce3a6b6, 2026-01-15)
  - Add automatic opportunity scanning after nested CV
New --scan-opportunities flag for nested CV:
- After CV completes, automatically scans all live markets
- Uses recommended params from CV results
- Exports matching opportunities to specified file
- Shows summary of found opportunities
Usage:
  python main.py grid-search --nested-cv --scan-opportunities opportunities.json
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (0ef1cae, 2026-01-15)
  - Add time-stratified holdout for unbiased CV evaluation
Reserve 15% of markets as pure holdout before nested CV:
- 5% from early period, 5% from middle, 5% from late
- Holdout markets never touched during any CV fold
- Evaluate best params on holdout after CV completes
- Compare CV estimate vs holdout for validation
Changes:
- backtest/validation.py: Add holdout_fraction config, split method
- backtest/cross_validator.py: Reserve holdout before CV, evaluate after
- main.py: Add --holdout-pct flag (default 15%), export holdout results
- backtest/runner.py: Reduce progress output frequency
Usage:
  python main.py grid-search --nested-cv --holdout-pct 0.15 ...
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (a8e429f, 2026-01-15)
  - Add holdout test and live opportunity scanner commands
Two new commands for strategy validation and live trading:
1. holdout-test: Validate optimized params on unseen markets
   - Time-based split: older markets for reference, recent for test
   - Uses vectorized backtest for fast evaluation
   - Loads params from CV results JSON file
   - Reports unbiased P&L and win rate on holdout set
2. find-opportunities: Scan live markets for trading signals
   - Fetches all active Polymarket markets
   - Detects stability signals using optimized params
   - Outputs market IDs with entry/exit prices
   - Exports to JSON for automated trading
   - Tested: Found 454 opportunities from 8,728 markets
New files:
- backtest/holdout.py: Time-based holdout test logic
Modified:
- main.py: Added holdout-test and find-opportunities subcommands
- backtest/__init__.py: Export holdout functions
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (3742059, 2026-01-15)
  - Fix stdout buffering for verification output
Flush stdout before running verification subprocess to ensure
output appears in correct order.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (b26c135, 2026-01-15)
  - Fix verification integration in main.py
Call the independent verification script via subprocess instead of
importing the old functions that were replaced.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (ff30383, 2026-01-15)
  - Implement true independent trade verification
The previous verification only checked P&L math (exit - entry), which
wasn't truly independent since it used the same exported prices.
New verification:
- Loads raw price history from SQLite cache
- Verifies entry prices match daily close from raw data
- Verifies exit prices match actual timestamps or resolution
- Verifies market resolution outcomes from cached data
- Reports verification rate with detailed error breakdown
This catches real bugs in the backtesting logic, not just arithmetic.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (ba00890, 2026-01-15)
  - Fix trade outcome enum mapping for all string formats
Handle both uppercase DataFrame values (HIT_TAKE_PROFIT) and lowercase
enum values (take_profit) with a complete mapping table.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (5e4acd2, 2026-01-15)
  - Use parallel fetching for price histories (5-10x faster)
- Replace sequential API calls with fetch_multiple()
- Default concurrency: 50 parallel requests
- Pre-filter cached items before fetching
- Progress updates every 100 fetches
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (0f0dd19, 2026-01-15)
  - Fix trade export enum conversion for uppercase outcome strings
The vectorized_trades module uses uppercase outcome strings (RESOLVED_WIN)
but TradeOutcome enum expects lowercase values. Added mapping to handle both.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (b8a21b5, 2026-01-15)
  - Add --min-price-points flag to increase valid market count
- Add CLI argument (default: 5, was hardcoded at 10)
- Add filtering analytics showing breakdown during data loading
- Expected ~30% more valid markets
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (832171a, 2026-01-14)
  - Add trade export and independent verification
- Add --export-trades flag (default: trades_output.json) to export all test
  fold trades for independent verification
- Add scripts/verify_trades.py to recalculate P&L from first principles
- Auto-run verification after each nested CV run
- Add grid search over confidence weights (--stability-weight-range, etc.)
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (b70b71d, 2026-01-14)
  - Add confidence-based position sizing for nested cross-validation
Introduces ConfidenceConfig and confidence scoring for position sizing based on
stability, convergence, and time decay weights. Allows variable position sizes
based on signal strength during backtesting.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (876a843, 2026-01-14)
  - Add nested cross-validation for unbiased grid search evaluation
- Add backtest/validation.py with NestedCVConfig, MarketSplitter, result dataclasses
- Add backtest/cross_validator.py with NestedCrossValidator for nested CV algorithm
- Add filter_by_markets() method to VectorizedBacktestData for train/test splitting
- Add --nested-cv flag and related CLI options to grid-search command
- Add live scanner module for continuous market monitoring
The nested CV implementation uses:
- Outer loop (K=5 folds) for TRUE performance estimation
- Inner loop (K=3 folds) for hyperparameter selection
- Stratified splitting to balance YES/NO outcomes
- Prevents overfitting by never evaluating on training data
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (b99effd, 2026-01-14)
  - Add vectorized backtesting for faster grid search
- Add vectorized data preprocessing (build once, reuse for all combinations)
- Add vectorized signal detection using pandas operations
- Add vectorized trade simulation
- Add --fast/--slow flags to grid search command
- Add progress tracking with ETA and checkpointing
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (4da44e4, 2026-01-13)
  - Improve backtest reporting clarity
- Show actual position prices for NO trades (was showing YES price)
- Show entry→exit price format: "$0.950→$0.997"
- Better progress: show analyzed vs skipped counts
- Final summary shows data quality stats (% with price data)
- Use 3 decimal places for prices to show extreme values
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (224368d, 2026-01-13)
  - Fix timezone mismatch in datetime comparisons
Normalize datetimes to naive (strip timezone) when comparing
timestamps from different sources that may have inconsistent
timezone awareness.
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (df12f0f, 2026-01-13)
  - Update README with backtesting documentation
Add comprehensive documentation for:
- Backtest command and parameters
- Grid search optimization
- Cache management
- Updated project structure
Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com> (b1cb382, 2026-01-13)
<!-- PROJECT_HISTORY_END -->
