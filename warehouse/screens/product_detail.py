"""Product Detail screen — full info and market state for a single product."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from ..data_loader import generate_market_state
from ..widgets import MarketStatePanel, SectionHeader


class ProductDetailScreen(Screen):
    """Display full details for a selected product."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("r", "run_sim", "Run Simulation"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="detail-container"):
            yield SectionHeader("Product Detail")
            yield Static("", id="product-header")
            with Horizontal(id="detail-body"):
                with Vertical(id="info-panel"):
                    yield SectionHeader("Product Information")
                    yield Static("", id="product-info")
                    yield SectionHeader("Description")
                    yield Static("", id="product-desc")
                with Vertical(id="market-panel"):
                    yield MarketStatePanel(id="market-state")
                    yield SectionHeader("Actions")
                    yield Button("Run Pricing Simulation", id="btn-simulate", variant="primary")
                    yield Button("Back to Catalog", id="btn-back", variant="default")
        yield Footer()

    def on_mount(self) -> None:
        pid = getattr(self.app, "selected_product_id", None)
        product = None
        for p in self.app.products:
            if p.sample_id == pid:
                product = p
                break

        if product is None:
            self.query_one("#product-header", Static).update("[bold red]Product not found[/]")
            return

        self.query_one("#product-header", Static).update(
            f"[bold]{product.name}[/]\n[dim]ID: {product.sample_id} | Category: {product.category}[/]"
        )
        info = [
            f"  [bold]Price:[/]       {product.price_display}",
            f"  [bold]Category:[/]    {product.category}",
            f"  [bold]Unit:[/]        {product.unit or 'N/A'}",
            f"  [bold]Value:[/]       {product.value or 'N/A'}",
        ]
        if product.bullet_points:
            info.append(f"\n  [bold]Features:[/]\n  {product.bullet_points[:500]}")
        self.query_one("#product-info", Static).update("\n".join(info))

        desc = product.description[:800] if product.description else "No description available."
        self.query_one("#product-desc", Static).update(f"  {desc}")

        market = generate_market_state(product)
        self.query_one("#market-state", MarketStatePanel).update_data({
            "current_price": market.current_price,
            "competitor_price": market.competitor_price,
            "inventory_level": market.inventory_level,
            "user_engagement": market.user_engagement,
            "seasonal_factor": market.seasonal_factor,
            "demand_elasticity": market.demand_elasticity,
        })

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-simulate":
            self.action_run_sim()
        elif event.button.id == "btn-back":
            self.app.pop_screen()

    def action_run_sim(self) -> None:
        self.app.push_screen("pricing")
