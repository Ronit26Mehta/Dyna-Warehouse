"""Analytics screen — aggregate metrics, history, category stats."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ..storage import load_simulation_history
from ..widgets import SectionHeader


class AnalyticsScreen(Screen):
    """View aggregate analytics and simulation history."""

    BINDINGS = [
        ("d", "app.go_dashboard", "Dashboard"),
        ("c", "app.go_catalog", "Catalog"),
        ("p", "app.go_pricing", "Pricing"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="analytics-container"):
            yield SectionHeader("Analytics & Performance Metrics")
            with Horizontal(id="analytics-top"):
                with Vertical(id="metrics-panel"):
                    yield SectionHeader("Aggregate Metrics")
                    yield Static("", id="agg-metrics")
                with Vertical(id="category-stats-panel"):
                    yield SectionHeader("Category Statistics")
                    yield DataTable(id="cat-stats-table")

            with Vertical(id="analytics-bottom"):
                yield SectionHeader("Simulation History")
                yield DataTable(id="history-table", cursor_type="row")
                yield Static("", id="history-count")
        yield Footer()

    def on_mount(self) -> None:
        d = self.app.data  # All stats precomputed, zero computation here
        cv = (d.std_price / d.avg_price * 100) if d.avg_price > 0 else 0

        sim_history = self.app.simulation_history
        n = len(sim_history)
        avg_r = sum(getattr(s, "avg_reward", 0) for s in sim_history) / n if n else 0
        avg_c = sum(getattr(s, "price_change_pct", 0) for s in sim_history) / n if n else 0

        self.query_one("#agg-metrics", Static).update(
            f"  --- Catalog ---\n"
            f"  Total Products:   {d.total_products:>10,}\n"
            f"  With Price:       {d.priced_products:>10,}\n"
            f"  Categories:       {len(d.category_counts):>10}\n\n"
            f"  --- Price Stats ---\n"
            f"  Average:          ${d.avg_price:>10,.2f}\n"
            f"  Median:           ${d.median_price:>10,.2f}\n"
            f"  Std Dev:          ${d.std_price:>10,.2f}\n"
            f"  Range:            ${d.max_price - d.min_price:>10,.2f}\n"
            f"  CV:                {cv:>9.1f}%\n\n"
            f"  --- Simulations ---\n"
            f"  Total:            {n:>10}\n"
            f"  Avg Reward:        {avg_r:>10.4f}\n"
            f"  Avg Price Delta:   {avg_c:>9.1f}%"
        )

        # Category stats — all precomputed
        ct = self.query_one("#cat-stats-table", DataTable)
        ct.add_columns("Category", "Count", "Avg $", "Min $", "Max $")
        for cat, count in d.category_counts.items():
            avg = d.category_avg_prices.get(cat, 0)
            mn = d.category_min_prices.get(cat, 0)
            mx = d.category_max_prices.get(cat, 0)
            ct.add_row(cat, f"{count:,}", f"${avg:,.2f}", f"${mn:,.2f}", f"${mx:,.2f}")

        # History table (last 50)
        ht = self.query_one("#history-table", DataTable)
        ht.add_columns("Product", "Steps", "Initial", "Final", "Change", "Reward")
        recent = sim_history[-50:][::-1]
        for s in recent:
            name = getattr(s, "product_name", "?")[:40]
            steps = str(getattr(s, "steps", 0))
            initial = getattr(s, "initial_price", 0)
            final = getattr(s, "final_price", 0)
            pct = getattr(s, "price_change_pct", 0)
            reward = getattr(s, "avg_reward", 0)
            ht.add_row(
                name, steps,
                f"${initial:,.2f}", f"${final:,.2f}",
                f"{pct:+.1f}%", f"{reward:.4f}",
            )
        self.query_one("#history-count", Static).update(f"  {len(recent)} of {n} simulations")
