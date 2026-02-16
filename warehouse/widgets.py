"""Custom Textual widgets for the Warehouse TUI."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class KPICard(Static):
    """A styled KPI metric card for the dashboard."""

    def __init__(self, label: str, value: str, sub: str = "", **kwargs):
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._sub = sub

    def compose(self) -> ComposeResult:
        yield Static(self._label, classes="kpi-label")
        yield Static(self._value, classes="kpi-value")
        if self._sub:
            yield Static(self._sub, classes="kpi-sub")


class SparklineBar(Static):
    """Simple text sparkline for inline visualization."""

    BARS = " _.-~*=#"

    def __init__(self, values: list[float], label: str = "", **kwargs):
        super().__init__(**kwargs)
        self._values = values
        self._label = label

    def render(self) -> str:
        if not self._values:
            return f"{self._label} [dim]no data[/]"

        mn = min(self._values)
        mx = max(self._values)
        rng = mx - mn if mx != mn else 1.0

        step = max(1, len(self._values) // 30)
        sampled = self._values[::step][:30]

        chars = []
        for v in sampled:
            idx = int(((v - mn) / rng) * (len(self.BARS) - 1))
            idx = max(0, min(len(self.BARS) - 1, idx))
            chars.append(self.BARS[idx])

        spark = "".join(chars)
        return f"{self._label} [green]{spark}[/] [dim][{mn:.2f}-{mx:.2f}][/]"

    def update_values(self, values: list[float]) -> None:
        self._values = values
        self.refresh()


class MarketStatePanel(Static):
    """Compact panel displaying market state."""

    def __init__(self, market_data: dict | None = None, **kwargs):
        super().__init__(**kwargs)
        self._data = market_data or {}

    def render(self) -> str:
        d = self._data
        if not d:
            return "[dim]No market data[/]"

        lines = [
            "[bold cyan]--- Market State ---[/]",
            f"  Current Price:  ${d.get('current_price', 0):,.2f}",
            f"  Competitor:     ${d.get('competitor_price', 0):,.2f}",
            f"  Inventory:      {d.get('inventory_level', 0)} units",
            f"  Engagement:     {d.get('user_engagement', 0):.0%}",
            f"  Seasonal:       {d.get('seasonal_factor', 1.0):.2f}x",
            f"  Elasticity:     {d.get('demand_elasticity', -1.5):.2f}",
        ]
        return "\n".join(lines)

    def update_data(self, data: dict) -> None:
        self._data = data
        self.refresh()


class RewardBreakdown(Static):
    """Display reward breakdown with simple text bars."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._reward = 0.0
        self._profit = 0.0
        self._competitive = 0.0
        self._stability = 0.0
        self._inventory = 0.0

    def render(self) -> str:
        def bar(val: float, mx: float) -> str:
            w = 15
            filled = int(abs(val) / max(abs(mx), 0.001) * w)
            filled = min(w, max(0, filled))
            return "#" * filled + "." * (w - filled)

        entries = [
            ("Total Reward", self._reward, "bold"),
            ("a Profit", self._profit, "green"),
            ("b Competitive", -self._competitive, "red"),
            ("g Stability", -self._stability, "yellow"),
            ("d Inventory", -self._inventory, "magenta"),
        ]
        mx = max((abs(e[1]) for e in entries), default=1.0)

        lines = ["[bold yellow]--- Reward Breakdown ---[/]"]
        for label, val, style in entries:
            sign = "+" if val >= 0 else "-"
            b = bar(val, mx)
            lines.append(f"  {label:<14} [{style}]{sign}{abs(val):.4f} {b}[/]")
        return "\n".join(lines)

    def update_values(self, reward: float, profit: float,
                      competitive: float, stability: float,
                      inventory: float) -> None:
        self._reward = reward
        self._profit = profit
        self._competitive = competitive
        self._stability = stability
        self._inventory = inventory
        self.refresh()


class SectionHeader(Static):
    """A styled section header for screen areas."""

    DEFAULT_CSS = """
    SectionHeader {
        width: 100%;
        height: 1;
        background: $primary-background;
        color: $text;
        text-style: bold;
        padding: 0 1;
    }
    """

    def __init__(self, title: str, **kwargs):
        super().__init__(f" * {title}", **kwargs)
