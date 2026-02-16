"""Data models for the Warehouse application."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """A product from the warehouse catalog."""

    sample_id: int
    name: str
    price: float
    category: str
    unit: str = ""
    value: str = ""
    image_link: str = ""
    bullet_points: str = ""
    description: str = ""

    @property
    def display_name(self) -> str:
        """Return a truncated name for table display."""
        if len(self.name) > 55:
            return self.name[:52] + "..."
        return self.name

    @property
    def price_display(self) -> str:
        """Formatted price string."""
        return f"${self.price:,.2f}"


@dataclass
class MarketState:
    """Current market state for a product."""

    product_id: int
    current_price: float
    competitor_price: float
    inventory_level: int
    user_engagement: float  # 0.0 - 1.0
    seasonal_factor: float  # 0.5 - 2.0
    demand_elasticity: float  # -3.0 to -0.5
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class PricingAction:
    """A pricing decision record."""

    product_id: int
    product_name: str
    old_price: float
    new_price: float
    reward: float
    profit_component: float
    competitive_component: float
    stability_component: float
    inventory_component: float
    step: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    @property
    def price_change_pct(self) -> float:
        if self.old_price == 0:
            return 0.0
        return ((self.new_price - self.old_price) / self.old_price) * 100

    @property
    def direction(self) -> str:
        if self.new_price > self.old_price:
            return "▲"
        elif self.new_price < self.old_price:
            return "▼"
        return "━"


@dataclass
class SimulationResult:
    """Result of a full pricing simulation run."""

    product_id: int
    product_name: str
    actions: list[PricingAction] = field(default_factory=list)
    total_reward: float = 0.0
    avg_reward: float = 0.0
    final_price: float = 0.0
    initial_price: float = 0.0
    max_price: float = 0.0
    min_price: float = 0.0
    steps: int = 0

    @property
    def price_change_pct(self) -> float:
        if self.initial_price == 0:
            return 0.0
        return ((self.final_price - self.initial_price) / self.initial_price) * 100


@dataclass
class AppSettings:
    """Application settings."""

    # Pricing engine weights
    alpha: float = 0.40  # Profit weight
    beta: float = 0.25   # Competitive penalty weight
    gamma: float = 0.20  # Stability penalty weight
    delta: float = 0.15  # Inventory penalty weight

    # Simulation defaults
    default_steps: int = 30
    price_adjustment_range: float = 0.15  # Max 15% price change per step

    # Display
    max_catalog_rows: int = 500
    theme: str = "warehouse_dark"

    def to_dict(self) -> dict:
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "delta": self.delta,
            "default_steps": self.default_steps,
            "price_adjustment_range": self.price_adjustment_range,
            "max_catalog_rows": self.max_catalog_rows,
            "theme": self.theme,
        }

    @classmethod
    def from_dict(cls, data: dict) -> AppSettings:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
