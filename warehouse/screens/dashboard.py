"""Dashboard screen — KPIs, category breakdown, system status."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ..widgets import KPICard, SectionHeader


class DashboardScreen(Screen):
    """Main dashboard with KPI cards, category breakdown, and system status."""

    BINDINGS = [
        ("c", "app.go_catalog", "Catalog"),
        ("p", "app.go_pricing", "Pricing"),
        ("a", "app.go_analytics", "Analytics"),
        ("s", "app.go_settings", "Settings"),
        ("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="dashboard-container"):
            yield Static(
                "======================================================\n"
                "   WAREHOUSE - Dynamic Pricing System\n"
                "   Autonomous Price Optimization Framework\n"
                "======================================================",
                id="banner",
            )

            with Horizontal(id="kpi-row"):
                yield KPICard("TOTAL PRODUCTS", "0", "loading", id="kpi-products")
                yield KPICard("CATEGORIES", "0", "groups", id="kpi-categories")
                yield KPICard("AVG PRICE", "$0", "catalog", id="kpi-avg-price")
                yield KPICard("SIMULATIONS", "0", "done", id="kpi-simulations")

            with Horizontal(id="panels-row"):
                with Vertical(id="category-panel"):
                    yield SectionHeader("Category Breakdown")
                    yield DataTable(id="category-table")

                with Vertical(id="status-panel"):
                    yield SectionHeader("System Status")
                    yield Static("", id="status-content")
                    yield SectionHeader("Quick Actions")
                    yield Static(
                        "  [bold cyan]C[/]  Product Catalog\n"
                        "  [bold cyan]P[/]  Pricing Simulation\n"
                        "  [bold cyan]A[/]  Analytics\n"
                        "  [bold cyan]S[/]  Settings\n"
                        "  [bold cyan]Q[/]  Quit",
                        id="quick-actions",
                    )
        yield Footer()

    def on_mount(self) -> None:
        d = self.app.data  # PrecomputedData

        # Update KPIs
        kpi_p = self.query_one("#kpi-products", KPICard)
        kpi_p.query_one(".kpi-value", Static).update(f"{d.total_products:,}")
        kpi_p.query_one(".kpi-sub", Static).update("in catalog")

        kpi_c = self.query_one("#kpi-categories", KPICard)
        kpi_c.query_one(".kpi-value", Static).update(str(len(d.category_counts)))

        kpi_a = self.query_one("#kpi-avg-price", KPICard)
        kpi_a.query_one(".kpi-value", Static).update(f"${d.avg_price:,.2f}")

        sims = len(self.app.simulation_history)
        kpi_s = self.query_one("#kpi-simulations", KPICard)
        kpi_s.query_one(".kpi-value", Static).update(str(sims))

        # Category table — all stats already precomputed
        table = self.query_one("#category-table", DataTable)
        table.add_columns("Category", "Products", "Avg Price", "Share")
        total = d.total_products or 1
        for cat, count in d.category_counts.items():
            avg = d.category_avg_prices.get(cat, 0)
            share = count / total * 100
            blen = int(share / 2.5)
            bar = "#" * blen + "." * (20 - blen)
            table.add_row(cat, f"{count:,}", f"${avg:,.2f}", f"{bar} {share:.1f}%")

        # Status
        self.query_one("#status-content", Static).update(
            f"  [bold green]*[/] Data Loaded\n"
            f"  Products:    {d.total_products:>8,}\n"
            f"  Categories:  {len(d.category_counts):>8}\n"
            f"  Price Range: ${d.min_price:,.2f} - ${d.max_price:,.2f}\n"
            f"  Zero-Price:  {d.zero_price_count:>8,}\n"
            f"  Simulations: {sims:>8}\n"
            f"  [bold green]*[/] Engine Online\n"
            f"  [bold green]*[/] Storage Synced"
        )
