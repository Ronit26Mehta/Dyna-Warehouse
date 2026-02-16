"""Data loader — fast CSV parsing with pickle cache.

Strategy:
  1. Parse CSV with simple string lookups (no regex)
  2. Limit to MAX_PRODUCTS with uniform sampling across the file
  3. Precompute ALL statistics in a single pass
  4. Cache everything as a pickle — subsequent loads are instant
"""

from __future__ import annotations

import csv
import hashlib
import pickle
import random
from dataclasses import dataclass, field
from pathlib import Path

from .models import MarketState, Product

MAX_PRODUCTS = 10_000     # Hard cap for UI performance
CACHE_DIR = Path.home() / ".warehouse"

# ── Category keywords ──
_CAT_RULES = [
    ("Coffee & Tea", ("coffee", "tea", "espresso", "latte", "brew", "chai", "matcha")),
    ("Beverages", ("water", "juice", "soda", "drink", "beverage", "cola", "lemonade")),
    ("Snacks & Chips", ("chip", "snack", "pretzel", "popcorn", "cracker", "cookie", "nuts")),
    ("Candy & Sweets", ("candy", "chocolate", "gum", "mint", "sweet", "gummy", "caramel")),
    ("Spices & Seasoning", ("spice", "seasoning", "pepper", "salt", "cinnamon", "cumin", "paprika")),
    ("Health & Wellness", ("vitamin", "supplement", "protein", "organic", "health", "probiotic")),
    ("Dairy & Refrigerated", ("milk", "cheese", "yogurt", "butter", "cream", "dairy", "egg")),
    ("Canned & Packaged", ("canned", "soup", "sauce", "paste", "jar", "broth", "stock")),
    ("Baking & Cooking", ("flour", "sugar", "baking", "yeast", "vanilla", "cocoa", "mix")),
]


def _classify(name_lower: str) -> str:
    for cat, kws in _CAT_RULES:
        for kw in kws:
            if kw in name_lower:
                return cat
    return "Other"


def _fast_parse_catalog(raw: str) -> tuple[str, str, str]:
    """Extract name, bullets, desc using fast string finds — no regex."""
    name = bullets = desc = ""
    if not raw:
        return name, bullets, desc

    low = raw.lower()

    # Find item_name
    ni = low.find("item_name")
    bi = low.find("bullet_point")
    di = low.find("product_description")

    if ni >= 0:
        start = raw.find(":", ni) + 1
        end = bi if bi > start else (di if di > start else len(raw))
        name = raw[start:end].strip()[:120]

    if bi >= 0:
        start = raw.find(":", bi) + 1
        end = di if di > start else len(raw)
        bullets = raw[start:end].strip()[:200]

    if di >= 0:
        start = raw.find(":", di) + 1
        desc = raw[start:].strip()[:300]

    if not name:
        name = raw[:80].strip().replace("\n", " ")

    return name, bullets, desc


@dataclass
class PrecomputedData:
    """All data — precomputed, cached, zero recomputation needed."""
    products: list[Product] = field(default_factory=list)
    category_counts: dict[str, int] = field(default_factory=dict)
    category_avg_prices: dict[str, float] = field(default_factory=dict)
    category_min_prices: dict[str, float] = field(default_factory=dict)
    category_max_prices: dict[str, float] = field(default_factory=dict)
    total_products: int = 0
    total_in_csv: int = 0
    priced_products: int = 0
    avg_price: float = 0.0
    median_price: float = 0.0
    min_price: float = 0.0
    max_price: float = 0.0
    std_price: float = 0.0
    zero_price_count: int = 0


def _cache_key(csv_path: Path) -> Path:
    stat = csv_path.stat()
    key = f"{csv_path.name}_{stat.st_size}_{int(stat.st_mtime)}_{MAX_PRODUCTS}"
    h = hashlib.md5(key.encode()).hexdigest()[:12]
    return CACHE_DIR / f"cache_{h}.pkl"


def load_and_cache(csv_path: str | Path) -> PrecomputedData:
    """Load from pickle cache or parse CSV + cache.

    Uses reservoir sampling to get a uniform sample of up to MAX_PRODUCTS
    from arbitrarily large CSV files without loading everything.
    """
    csv_path = Path(csv_path)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = _cache_key(csv_path)

    if cache.exists():
        try:
            with open(cache, "rb") as f:
                data = pickle.load(f)
            if isinstance(data, PrecomputedData) and data.total_products > 0:
                return data
        except Exception:
            pass

    # ── Reservoir sampling: read entire CSV but only keep MAX_PRODUCTS ──
    reservoir: list[Product] = []
    total_rows = 0

    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            total_rows += 1
            catalog = row.get("catalog_content", "")
            name, bullets, desc = _fast_parse_catalog(catalog)

            try:
                price = float(row.get("price", 0))
            except (ValueError, TypeError):
                price = 0.0

            product = Product(
                sample_id=int(row.get("sample_id", i)),
                name=name or f"Product {i}",
                price=price,
                category=_classify(name.lower()),
                unit=row.get("unit", ""),
                value=row.get("value", ""),
                image_link=row.get("image_link", ""),
                bullet_points=bullets,
                description=desc,
            )

            if len(reservoir) < MAX_PRODUCTS:
                reservoir.append(product)
            else:
                # Reservoir sampling: replace with decreasing probability
                j = random.randint(0, i)
                if j < MAX_PRODUCTS:
                    reservoir[j] = product

    # ── Compute all stats in a single pass ──
    data = PrecomputedData(products=reservoir)
    data.total_products = len(reservoir)
    data.total_in_csv = total_rows

    cat_counts: dict[str, int] = {}
    cat_sums: dict[str, float] = {}
    cat_cnts: dict[str, int] = {}
    cat_mins: dict[str, float] = {}
    cat_maxs: dict[str, float] = {}
    prices: list[float] = []

    for p in reservoir:
        cat_counts[p.category] = cat_counts.get(p.category, 0) + 1
        if p.price > 0:
            prices.append(p.price)
            c = p.category
            cat_sums[c] = cat_sums.get(c, 0) + p.price
            cat_cnts[c] = cat_cnts.get(c, 0) + 1
            if c not in cat_mins or p.price < cat_mins[c]:
                cat_mins[c] = p.price
            if c not in cat_maxs or p.price > cat_maxs[c]:
                cat_maxs[c] = p.price

    data.category_counts = dict(sorted(cat_counts.items(), key=lambda x: x[1], reverse=True))
    data.category_avg_prices = {c: cat_sums[c] / cat_cnts[c] for c in cat_cnts}
    data.category_min_prices = cat_mins
    data.category_max_prices = cat_maxs

    data.priced_products = len(prices)
    data.zero_price_count = data.total_products - data.priced_products
    if prices:
        prices.sort()
        data.avg_price = sum(prices) / len(prices)
        data.median_price = prices[len(prices) // 2]
        data.min_price = prices[0]
        data.max_price = prices[-1]
        data.std_price = (sum((x - data.avg_price) ** 2 for x in prices) / len(prices)) ** 0.5

    try:
        with open(cache, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        pass

    return data


def generate_market_state(product: Product, seed: int | None = None) -> MarketState:
    """Generate a simulated market state for a product."""
    rng = random.Random(seed if seed is not None else product.sample_id)
    base = product.price if product.price > 0 else 10.0
    return MarketState(
        product_id=product.sample_id,
        current_price=base,
        competitor_price=round(base * (1 + rng.uniform(-0.20, 0.20)), 2),
        inventory_level=rng.randint(5, 500),
        user_engagement=round(rng.uniform(0.1, 1.0), 2),
        seasonal_factor=round(rng.uniform(0.5, 2.0), 2),
        demand_elasticity=round(rng.uniform(-3.0, -0.5), 2),
    )


def find_csv_files(data_dir: str | Path) -> list[Path]:
    data_dir = Path(data_dir)
    if not data_dir.exists():
        return []
    return sorted(data_dir.glob("*.csv"))
