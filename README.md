# WAREHOUSE — Autonomous Dynamic Pricing TUI

<p align="center">
  <strong>A terminal-based warehouse management and dynamic pricing simulation system</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/textual-0.89%2B-green?style=flat-square" alt="Textual">
  <img src="https://img.shields.io/badge/version-1.0.0-orange?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-purple?style=flat-square" alt="License">
</p>

---

## Overview

**Warehouse** is a high-performance Terminal User Interface (TUI) built with [Textual](https://textual.textualize.io/) for managing product catalogs and running autonomous dynamic pricing simulations. It handles datasets of **75,000+ products** efficiently through intelligent data sampling, precomputed statistics, and pickle-based caching.

The application implements a **Soft Actor-Critic (SAC)** inspired pricing engine that simulates optimal pricing strategies by balancing profit maximization, competitive positioning, price stability, and inventory management.

### Key Highlights

- **Instant Startup** — First run parses CSV and caches as pickle; subsequent launches load in ~0.2 seconds
- **Reservoir Sampling** — Uniformly samples 10,000 products from arbitrarily large CSV files, keeping all categories represented
- **Zero-Recomputation** — All aggregate statistics (category counts, averages, min/max, median, std dev) precomputed once and cached
- **6 Interactive Screens** — Dashboard, Catalog, Product Detail, Pricing Simulation, Analytics, Settings
- **Keyboard-Driven** — Full keyboard navigation with intuitive shortcuts

---

## Screenshots

```
┌──────────────────────────────────────────────────────────────────────┐
│  WAREHOUSE - Dynamic Pricing System                                  │
│  ════════════════════════════════════════                             │
│                                                                      │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │
│  │ 10,000  │  │   10    │  │ $23.98  │  │    3    │                │
│  │Products │  │  Cats   │  │Avg Price│  │  Sims   │                │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘                │
│                                                                      │
│  Category Breakdown              System Status                       │
│  ─────────────────              ─────────────                        │
│  Other          2,585  25.9%    * Data Loaded                        │
│  Coffee & Tea   1,615  16.2%    * Engine Online                      │
│  Beverages      1,257  12.6%    * Storage Synced                     │
│  Snacks & Chips   885   8.8%                                         │
│  ...                                                                 │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/your-username/warehouse.git
cd warehouse

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# Install in editable mode
pip install -e .
```

### From PyPI

```bash
pip install warehouse
```

### Requirements

- **Python 3.10+**
- **textual >= 0.89.0** — TUI framework
- **rich >= 13.0.0** — Rich text rendering

---

## Quick Start

### 1. Prepare Your Data

Place your CSV file in a `data/` directory at the project root:

```
warehouse/
├── data/
│   └── train.csv          # Your product catalog CSV
├── warehouse/
│   └── ...
└── pyproject.toml
```

The CSV should have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `sample_id` | Yes | Unique product identifier |
| `price` | Yes | Product price (numeric) |
| `catalog_content` | Yes | Item name, bullet points, description |
| `unit` | No | Unit of measurement |
| `value` | No | Package value/quantity |
| `image_link` | No | Product image URL |

### 2. Launch

```bash
# Auto-detect data/ directory
warehouse

# Or specify a custom data path
warehouse --data /path/to/your/data
```

### 3. Navigate

The TUI launches on the **Dashboard** screen. Use these shortcuts to navigate:

| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Dashboard |
| `Ctrl+B` | Product Catalog |
| `Ctrl+P` | Pricing Simulation |
| `Ctrl+A` | Analytics |
| `Ctrl+S` | Settings |
| `Ctrl+Q` | Quit |
| `Esc` | Go Back |

---

## Screens

### Dashboard

The main overview screen displaying:
- **KPI Cards** — Total products, category count, average price, simulation count
- **Category Breakdown** — Table with product counts, average prices, and share bars
- **System Status** — Data loading status, price range, zero-price count

### Catalog Browser

Browse and search the product catalog with:
- **Category Tree** — Filter by product category
- **Search** — Real-time text search across product names
- **Paginated Table** — 200 products per page with `N`/`B` navigation
- **Product Detail** — Click any row to view full product details

### Pricing Simulation

Run dynamic pricing simulations powered by the SAC engine:
- **Product ID Input** — Enter any product ID to simulate
- **Configurable Steps** — 5 to 200 simulation steps
- **Live Sparklines** — Price and reward trajectory visualization
- **Reward Breakdown** — Profit, competitive, stability, and inventory components
- **Step History Table** — Detailed per-step price changes and rewards

### Analytics

Aggregate performance metrics and simulation history:
- **Catalog Statistics** — Total products, price distribution (mean, median, std, CV)
- **Category Stats Table** — Per-category count, average, min, max prices
- **Simulation History** — Last 50 simulations with results

### Settings

Configure the pricing engine parameters:
- **Learning Rate** — SAC agent learning rate
- **Discount Factor (γ)** — Future reward discount
- **Reward Weights** — Profit, competitive, stability, inventory component weights
- **Price Bounds** — Min/max price change percentage per step

---

## Architecture

```
warehouse/
├── warehouse/
│   ├── __init__.py              # Package metadata
│   ├── app.py                   # Main Textual App — entry point, navigation, data loading
│   ├── app.tcss                 # Textual CSS — all screen and widget styles
│   ├── data_loader.py           # CSV parsing, reservoir sampling, pickle caching
│   ├── models.py                # Dataclasses: Product, MarketState, PricingAction, SimulationResult
│   ├── pricing_engine.py        # SAC-inspired dynamic pricing engine
│   ├── storage.py               # JSON persistence for settings and simulation history
│   ├── widgets.py               # Custom widgets: KPICard, SparklineBar, RewardBreakdown
│   └── screens/
│       ├── __init__.py
│       ├── dashboard.py         # KPI overview and category breakdown
│       ├── catalog.py           # Product catalog with search, filter, pagination
│       ├── product_detail.py    # Single product detail view
│       ├── pricing.py           # Dynamic pricing simulation runner
│       ├── analytics.py         # Aggregate metrics and simulation history
│       └── settings.py          # Pricing engine configuration
├── data/
│   └── train.csv                # Product catalog data (user-provided)
├── pyproject.toml               # Package configuration
├── README.md
├── LICENSE
├── CONTRIBUTING.md
└── SECURITY.md
```

### Data Flow

```
CSV File (70MB, 75K rows)
        │
        ▼
  ┌─────────────────┐
  │  Reservoir       │   First run only
  │  Sampling        │   (10K products)
  │  + Stats Calc    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │  Pickle Cache    │   ~/.warehouse/cache_*.pkl (~1.8MB)
  │  (PrecomputedData│
  └────────┬────────┘
           │
           ▼  Subsequent runs: ~0.2s load
  ┌─────────────────┐
  │  WarehouseApp    │   All stats available instantly
  │  .data           │   No recomputation needed
  │  .products       │
  │  .category_counts│
  └─────────────────┘
```

### Pricing Engine

The dynamic pricing engine uses a **Soft Actor-Critic (SAC)** inspired approach:

1. **State Space** — Current price, competitor price, inventory level, engagement, seasonal factor, demand elasticity
2. **Action Space** — Continuous price adjustment (bounded by configurable min/max %)
3. **Reward Function** — Weighted combination of:
   - **α Profit** — Revenue gain from price changes
   - **β Competitive** — Penalty for deviating from competitor pricing
   - **γ Stability** — Penalty for large price swings
   - **δ Inventory** — Penalty for stock-outs or overstock

---

## Performance Optimizations

| Technique | Impact |
|-----------|--------|
| **Pickle Caching** | First run: ~60s parse → Subsequent: 0.2s load |
| **Reservoir Sampling** | 75K → 10K products with uniform category representation |
| **Precomputed Stats** | Zero per-screen computation; all aggregates cached |
| **Paginated Tables** | 200 rows/page prevents DataTable rendering bottleneck |
| **String-Based Parsing** | `str.find()` instead of regex — ~10x faster catalog parsing |
| **Truncated Fields** | Bullet points (200 chars) and descriptions (300 chars) capped |
| **Overflow Clipping** | CSS `overflow-x: hidden` prevents widget bleedthrough |

---

## Configuration

### Data Directory

The app searches for CSV data in this order:
1. `--data` command-line argument
2. `./data/` directory (relative to CWD)
3. `../data/` directory (relative to package)
4. Current working directory

### Cache Location

Pickle caches are stored at:
- **Windows:** `C:\Users\<user>\.warehouse\cache_*.pkl`
- **Linux/macOS:** `~/.warehouse/cache_*.pkl`

Cache is automatically invalidated when the CSV file changes (size or modification time).

### Settings Persistence

Engine settings and simulation history are stored as JSON:
- **Windows:** `C:\Users\<user>\.warehouse\settings.json`, `simulation_history.json`
- **Linux/macOS:** `~/.warehouse/settings.json`, `simulation_history.json`

---

## Development

### Running Tests

```bash
# Run with Python directly (useful for debugging)
python -m warehouse.app --data ./data

# Or use the entry point
warehouse --data ./data
```

### Clearing Cache

To force re-parsing the CSV (e.g., after data changes):

```python
# From within the app, use Settings screen
# Or manually delete cache files:
# Windows: del %USERPROFILE%\.warehouse\cache_*.pkl
# Linux:   rm ~/.warehouse/cache_*.pkl
```

### Adding New Screens

1. Create a new screen in `warehouse/screens/`
2. Import and install it in `warehouse/app.py` (`install_screen`)
3. Add a keyboard binding in `BINDINGS`
4. Add a navigation action method
5. Style it in `warehouse/app.tcss`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Slow first launch** | Normal — CSV is being parsed and cached. Subsequent launches are instant. |
| **"CSV not found"** | Ensure `data/train.csv` exists or use `--data /path/to/dir` |
| **Garbled display** | Use a modern terminal (Windows Terminal, iTerm2, Alacritty) with Unicode support |
| **Product not found in pricing** | The 10K sample may not include that ID. Try another product from the catalog. |
| **Stale data after CSV update** | Delete cache files in `~/.warehouse/` to force re-parse |

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

---

## Acknowledgments

- [Textual](https://textual.textualize.io/) — Modern TUI framework for Python
- [Rich](https://rich.readthedocs.io/) — Rich text and beautiful formatting for the terminal
- Inspired by real-world dynamic pricing systems and reinforcement learning literature
