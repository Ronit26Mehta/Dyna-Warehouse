"""Dynamic Pricing Simulation screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from ..data_loader import generate_market_state
from ..models import Product
from ..pricing_engine import DynamicPricingEngine
from ..storage import save_simulation
from ..widgets import RewardBreakdown, SectionHeader, SparklineBar


class PricingScreen(Screen):
    """Run and visualize dynamic pricing simulations."""

    BINDINGS = [
        ("d", "app.go_dashboard", "Dashboard"),
        ("c", "app.go_catalog", "Catalog"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="pricing-container"):
            yield SectionHeader("Dynamic Pricing Engine - SAC Simulation")
            with Horizontal(id="pricing-toolbar"):
                yield Input(placeholder="Enter Product ID...", id="product-id-input", type="integer")
                yield Input(placeholder="Steps (30)", id="steps-input", type="integer")
                yield Button("Run Simulation", id="btn-run", variant="primary")

            with Horizontal(id="pricing-body"):
                with Vertical(id="simulation-panel"):
                    yield SectionHeader("Simulation Progress")
                    yield Static("Enter a Product ID and click Run.", id="sim-status")
                    yield SparklineBar([], label="Price:", id="price-sparkline")
                    yield SparklineBar([], label="Reward:", id="reward-sparkline")
                    yield SectionHeader("Step History")
                    yield DataTable(id="sim-table", cursor_type="row")

                with Vertical(id="reward-panel"):
                    yield RewardBreakdown(id="reward-breakdown")
                    yield SectionHeader("Simulation Summary")
                    yield Static("", id="sim-summary")
                    yield SectionHeader("Competitor Comparison")
                    yield Static("", id="competitor-info")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#sim-table", DataTable).add_columns(
            "Step", "Old Price", "New Price", "Change", "Reward", "Dir"
        )
        pid = getattr(self.app, "selected_product_id", None)
        if pid is not None:
            self.query_one("#product-id-input", Input).value = str(pid)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-run":
            self._run()

    def _run(self) -> None:
        status = self.query_one("#sim-status", Static)
        id_val = self.query_one("#product-id-input", Input).value.strip()
        if not id_val:
            status.update("[bold red]Enter a Product ID first.[/]")
            return

        try:
            pid = int(id_val)
        except ValueError:
            status.update("[bold red]Invalid Product ID.[/]")
            return

        product = None
        for p in self.app.products:
            if p.sample_id == pid:
                product = p
                break
        if product is None:
            status.update(f"[bold red]Product #{pid} not found.[/]")
            return
        if product.price <= 0:
            status.update(f"[bold red]Product #{pid} has no price data.[/]")
            return

        steps_val = self.query_one("#steps-input", Input).value.strip()
        try:
            steps = int(steps_val) if steps_val else 30
        except ValueError:
            steps = 30
        steps = max(5, min(200, steps))

        status.update(f"[bold yellow]Running {steps} steps for {product.display_name}...[/]")

        engine = DynamicPricingEngine(self.app.settings)
        market = generate_market_state(product)
        result = engine.run_simulation(product, market, steps)

        save_simulation(result)
        self.app.simulation_history.append(result)

        status.update(
            f"[bold green]Done[/] | "
            f"${result.initial_price:.2f} -> ${result.final_price:.2f} | "
            f"Reward: {result.total_reward:.4f}"
        )

        prices = [result.initial_price] + [a.new_price for a in result.actions]
        rewards = [a.reward for a in result.actions]
        self.query_one("#price-sparkline", SparklineBar).update_values(prices)
        self.query_one("#reward-sparkline", SparklineBar).update_values(rewards)

        table = self.query_one("#sim-table", DataTable)
        table.clear()
        for a in result.actions:
            table.add_row(
                str(a.step), f"${a.old_price:.2f}", f"${a.new_price:.2f}",
                f"{a.price_change_pct:+.1f}%", f"{a.reward:.4f}", a.direction,
            )

        if result.actions:
            last = result.actions[-1]
            self.query_one("#reward-breakdown", RewardBreakdown).update_values(
                last.reward, last.profit_component,
                last.competitive_component, last.stability_component,
                last.inventory_component,
            )

        self.query_one("#sim-summary", Static).update(
            f"  [bold]Product:[/]      {product.display_name}\n"
            f"  [bold]Initial:[/]      ${result.initial_price:,.2f}\n"
            f"  [bold]Final:[/]        ${result.final_price:,.2f}\n"
            f"  [bold]Change:[/]       {result.price_change_pct:+.1f}%\n"
            f"  [bold]Range:[/]        ${result.min_price:.2f} - ${result.max_price:.2f}\n"
            f"  [bold]Total Reward:[/] {result.total_reward:.4f}\n"
            f"  [bold]Avg Reward:[/]   {result.avg_reward:.4f}"
        )

        self.query_one("#competitor-info", Static).update(
            f"  [bold]Competitor:[/]   ${market.competitor_price:.2f}\n"
            f"  [bold]Our Initial:[/]  ${result.initial_price:.2f}\n"
            f"  [bold]Our Final:[/]    ${result.final_price:.2f}\n"
            f"  [bold]Elasticity:[/]   {market.demand_elasticity:.2f}\n"
            f"  [bold]Seasonal:[/]     {market.seasonal_factor:.2f}x"
        )
