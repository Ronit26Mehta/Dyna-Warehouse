"""Warehouse TUI Application — Main entry point."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from .data_loader import PrecomputedData, find_csv_files, load_and_cache
from .models import AppSettings, Product
from .screens.analytics import AnalyticsScreen
from .screens.catalog import CatalogScreen
from .screens.dashboard import DashboardScreen
from .screens.pricing import PricingScreen
from .screens.product_detail import ProductDetailScreen
from .screens.settings import SettingsScreen
from .storage import load_settings, load_simulation_history


class WarehouseApp(App):
    """Autonomous Dynamic Pricing Warehouse — Terminal User Interface."""

    TITLE = "WAREHOUSE - Dynamic Pricing System"
    SUB_TITLE = "Autonomous Price Optimization Framework"

    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("ctrl+d", "go_dashboard", "Dashboard", show=True),
        Binding("ctrl+b", "go_catalog", "Catalog", show=True),
        Binding("ctrl+p", "go_pricing", "Pricing", show=True),
        Binding("ctrl+a", "go_analytics", "Analytics", show=True),
        Binding("ctrl+s", "go_settings", "Settings", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    def __init__(self, data_path: str | Path | None = None):
        super().__init__()
        self.data_path = data_path
        self.settings: AppSettings = load_settings()
        self.simulation_history: list = load_simulation_history()
        self.selected_product_id: int | None = None

        # Load precomputed data (from pickle cache or fresh CSV parse)
        self.data: PrecomputedData = self._load_data()

        # Convenience aliases for screens
        self.products = self.data.products
        self.category_counts = self.data.category_counts
        self.total_products = self.data.total_products
        self.priced_products = self.data.priced_products
        self.avg_price = self.data.avg_price
        self.min_price = self.data.min_price
        self.max_price = self.data.max_price
        self.zero_price_count = self.data.zero_price_count

        # Install all screens upfront
        self.install_screen(DashboardScreen(), name="dashboard")
        self.install_screen(CatalogScreen(), name="catalog")
        self.install_screen(PricingScreen(), name="pricing")
        self.install_screen(AnalyticsScreen(), name="analytics")
        self.install_screen(SettingsScreen(), name="settings")
        self.install_screen(ProductDetailScreen(), name="product_detail")

    def _load_data(self) -> PrecomputedData:
        data_dir = self._find_data_dir()
        if data_dir is None:
            return PrecomputedData()

        csv_files = find_csv_files(data_dir)
        if not csv_files:
            return PrecomputedData()

        target = csv_files[0]
        for f in csv_files:
            if "train" in f.name.lower():
                target = f
                break

        try:
            return load_and_cache(target)
        except Exception:
            return PrecomputedData()

    def _find_data_dir(self) -> Path | None:
        if self.data_path:
            p = Path(self.data_path)
            if p.is_dir():
                return p
            if p.is_file():
                return p.parent

        candidates = [
            Path.cwd() / "data",
            Path(__file__).parent.parent / "data",
            Path.cwd(),
        ]
        for c in candidates:
            if c.exists() and list(c.glob("*.csv")):
                return c
        return None

    def on_mount(self) -> None:
        # Use push_screen to make dashboard the active screen
        self.push_screen("dashboard")

    def reload_data(self) -> None:
        from .data_loader import CACHE_DIR
        for f in CACHE_DIR.glob("cache_*.pkl"):
            f.unlink(missing_ok=True)
        self.data = self._load_data()
        self.products = self.data.products
        self.category_counts = self.data.category_counts

    # ── All navigation uses push_screen/pop_screen for clean screen stack ──
    def action_go_dashboard(self) -> None:
        self._navigate("dashboard")

    def action_go_catalog(self) -> None:
        self._navigate("catalog")

    def action_go_pricing(self) -> None:
        self._navigate("pricing")

    def action_go_analytics(self) -> None:
        self._navigate("analytics")

    def action_go_settings(self) -> None:
        self._navigate("settings")

    def _navigate(self, screen_name: str) -> None:
        """Pop everything back to base, then push the target screen."""
        # Pop all screens to get back to the base App screen
        while len(self.screen_stack) > 1:
            self.pop_screen()
        self.push_screen(screen_name)


def main():
    """CLI entry point — run the Warehouse TUI."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="warehouse",
        description="Warehouse - Autonomous Dynamic Pricing TUI",
    )
    parser.add_argument(
        "--data", type=str, default=None,
        help="Path to data directory containing CSV files",
    )
    args = parser.parse_args()

    app = WarehouseApp(data_path=args.data)
    app.run()


if __name__ == "__main__":
    main()
