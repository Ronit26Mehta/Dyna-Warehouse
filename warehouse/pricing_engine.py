"""Dynamic Pricing Engine — SAC-inspired reward function and simulation."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

from .models import AppSettings, MarketState, PricingAction, Product, SimulationResult


class DynamicPricingEngine:
    """Implements the autonomous pricing logic from the SAC framework.

    Reward function:
        R(s, a) = α·R_profit - β·P_competitive - γ·P_stability - δ·P_inventory

    Where:
        R_profit       = (new_price - cost) × demand(new_price)
        P_competitive  = max(0, new_price - competitor_price)²
        P_stability    = (new_price - old_price)²
        P_inventory    = penalty for over/under-stocking
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or AppSettings()
        self._rng = random.Random(42)

    def _estimate_cost(self, price: float) -> float:
        """Estimate product cost as ~60% of list price."""
        return price * 0.60

    def _demand_function(self, price: float, base_price: float,
                         elasticity: float, seasonal: float,
                         engagement: float) -> float:
        """Compute demand based on price elasticity model.

        demand = base_demand × (price / base_price) ^ elasticity × seasonal × engagement
        """
        if base_price <= 0 or price <= 0:
            return 0.0
        base_demand = 100.0
        price_ratio = price / base_price
        demand = base_demand * (price_ratio ** elasticity) * seasonal * engagement
        return max(0.0, demand)

    def compute_reward(self, old_price: float, new_price: float,
                       market: MarketState) -> tuple[float, float, float, float, float]:
        """Compute the multi-component reward.

        Returns:
            (total_reward, profit_component, competitive_penalty,
             stability_penalty, inventory_penalty)
        """
        s = self.settings
        cost = self._estimate_cost(market.current_price)

        # ── Profit component ──
        demand = self._demand_function(
            new_price, market.current_price,
            market.demand_elasticity, market.seasonal_factor,
            market.user_engagement,
        )
        profit = (new_price - cost) * demand
        r_profit = profit / max(1.0, market.current_price * 100)  # Normalize

        # ── Competitive penalty ──
        comp_diff = max(0.0, new_price - market.competitor_price)
        p_competitive = (comp_diff / max(1.0, market.competitor_price)) ** 2

        # ── Stability penalty ──
        price_change = abs(new_price - old_price) / max(1.0, old_price)
        p_stability = price_change ** 2

        # ── Inventory penalty ──
        inv = market.inventory_level
        if inv < 20:
            p_inventory = ((20 - inv) / 20) ** 2  # Low stock penalty
        elif inv > 400:
            p_inventory = ((inv - 400) / 400) ** 2  # Overstock penalty
        else:
            p_inventory = 0.0

        total = (s.alpha * r_profit
                 - s.beta * p_competitive
                 - s.gamma * p_stability
                 - s.delta * p_inventory)

        return total, r_profit, p_competitive, p_stability, p_inventory

    def suggest_price(self, product: Product, market: MarketState) -> float:
        """Suggest an optimal price using gradient-free search.

        Tests several candidate prices and returns the one with the highest reward.
        """
        base = market.current_price
        rng = self.settings.price_adjustment_range
        candidates = [
            base,
            base * (1 - rng * 0.25),
            base * (1 - rng * 0.50),
            base * (1 - rng * 0.75),
            base * (1 + rng * 0.25),
            base * (1 + rng * 0.50),
            base * (1 + rng * 0.75),
            market.competitor_price,
            market.competitor_price * 0.98,
            market.competitor_price * 1.02,
        ]

        best_price = base
        best_reward = float("-inf")
        for cp in candidates:
            cp = round(max(0.01, cp), 2)
            reward, *_ = self.compute_reward(base, cp, market)
            if reward > best_reward:
                best_reward = reward
                best_price = cp

        return round(best_price, 2)

    def simulate_step(self, product: Product, market: MarketState,
                      old_price: float) -> tuple[PricingAction, MarketState]:
        """Run one step of the pricing simulation.

        Returns the action taken and the updated market state.
        """
        new_price = self.suggest_price(product, market)
        total, r_profit, p_comp, p_stab, p_inv = self.compute_reward(
            old_price, new_price, market
        )

        action = PricingAction(
            product_id=product.sample_id,
            product_name=product.name[:60],
            old_price=round(old_price, 2),
            new_price=round(new_price, 2),
            reward=round(total, 4),
            profit_component=round(r_profit, 4),
            competitive_component=round(p_comp, 4),
            stability_component=round(p_stab, 4),
            inventory_component=round(p_inv, 4),
        )

        # Evolve market state
        inv_change = self._rng.randint(-30, 30)
        new_inv = max(0, market.inventory_level + inv_change)
        engagement_drift = self._rng.uniform(-0.05, 0.05)
        new_engagement = max(0.05, min(1.0, market.user_engagement + engagement_drift))
        seasonal_drift = self._rng.uniform(-0.1, 0.1)
        new_seasonal = max(0.3, min(2.5, market.seasonal_factor + seasonal_drift))
        comp_drift = self._rng.uniform(-0.03, 0.03)
        new_comp = round(max(0.01, market.competitor_price * (1 + comp_drift)), 2)

        new_market = MarketState(
            product_id=product.sample_id,
            current_price=new_price,
            competitor_price=new_comp,
            inventory_level=new_inv,
            user_engagement=round(new_engagement, 2),
            seasonal_factor=round(new_seasonal, 2),
            demand_elasticity=market.demand_elasticity,
        )

        return action, new_market

    def run_simulation(self, product: Product, market: MarketState,
                       steps: Optional[int] = None) -> SimulationResult:
        """Run a complete pricing simulation.

        Args:
            product: The product to simulate
            market: Initial market state
            steps: Number of simulation steps (default from settings)

        Returns:
            SimulationResult with full action history
        """
        steps = steps or self.settings.default_steps
        actions: list[PricingAction] = []
        current_price = market.current_price
        initial_price = current_price
        current_market = market
        prices = [current_price]

        for step in range(steps):
            action, current_market = self.simulate_step(
                product, current_market, current_price
            )
            action.step = step + 1
            actions.append(action)
            current_price = action.new_price
            prices.append(current_price)

        total_reward = sum(a.reward for a in actions)
        avg_reward = total_reward / len(actions) if actions else 0.0

        return SimulationResult(
            product_id=product.sample_id,
            product_name=product.name[:60],
            actions=actions,
            total_reward=round(total_reward, 4),
            avg_reward=round(avg_reward, 4),
            final_price=round(current_price, 2),
            initial_price=round(initial_price, 2),
            max_price=round(max(prices), 2),
            min_price=round(min(prices), 2),
            steps=steps,
        )
