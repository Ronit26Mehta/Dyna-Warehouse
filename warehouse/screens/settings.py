"""Settings screen — configure pricing engine parameters."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from ..models import AppSettings
from ..storage import clear_simulation_history, save_settings
from ..widgets import SectionHeader


class SettingsScreen(Screen):
    """Configure pricing engine weights and app options."""

    BINDINGS = [
        ("d", "app.go_dashboard", "Dashboard"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="settings-container"):
            yield SectionHeader("Settings - Pricing Engine Configuration")
            with Horizontal(id="settings-body"):
                with Vertical(id="weights-panel"):
                    yield SectionHeader("Reward Function Weights")
                    yield Static(
                        "  R(s,a) = a*Profit - b*Competitive - g*Stability - d*Inventory\n",
                        id="formula",
                    )
                    yield Static("  Alpha - Profit Weight", classes="setting-label")
                    yield Input(placeholder="0.40", id="input-alpha", type="number")
                    yield Static("  Beta - Competitive Penalty", classes="setting-label")
                    yield Input(placeholder="0.25", id="input-beta", type="number")
                    yield Static("  Gamma - Stability Penalty", classes="setting-label")
                    yield Input(placeholder="0.20", id="input-gamma", type="number")
                    yield Static("  Delta - Inventory Penalty", classes="setting-label")
                    yield Input(placeholder="0.15", id="input-delta", type="number")

                with Vertical(id="options-panel"):
                    yield SectionHeader("Simulation Defaults")
                    yield Static("  Default Steps", classes="setting-label")
                    yield Input(placeholder="30", id="input-steps", type="integer")
                    yield Static("  Max Price Adjustment (%)", classes="setting-label")
                    yield Input(placeholder="15", id="input-adj", type="number")
                    yield Static("  Max Catalog Display Rows", classes="setting-label")
                    yield Input(placeholder="500", id="input-rows", type="integer")

                    yield SectionHeader("Data Management")
                    yield Button("Save Settings", id="btn-save", variant="primary")
                    yield Button("Clear History", id="btn-clear", variant="warning")
                    yield Button("Reload Data", id="btn-reload", variant="default")
                    yield Static("", id="settings-status")
        yield Footer()

    def on_mount(self) -> None:
        s = self.app.settings
        self.query_one("#input-alpha", Input).value = str(s.alpha)
        self.query_one("#input-beta", Input).value = str(s.beta)
        self.query_one("#input-gamma", Input).value = str(s.gamma)
        self.query_one("#input-delta", Input).value = str(s.delta)
        self.query_one("#input-steps", Input).value = str(s.default_steps)
        self.query_one("#input-adj", Input).value = str(int(s.price_adjustment_range * 100))
        self.query_one("#input-rows", Input).value = str(s.max_catalog_rows)

    def _read(self) -> AppSettings:
        def fv(i, d):
            try: return float(self.query_one(f"#{i}", Input).value)
            except: return d
        def iv(i, d):
            try: return int(self.query_one(f"#{i}", Input).value)
            except: return d

        return AppSettings(
            alpha=fv("input-alpha", 0.4), beta=fv("input-beta", 0.25),
            gamma=fv("input-gamma", 0.2), delta=fv("input-delta", 0.15),
            default_steps=iv("input-steps", 30),
            price_adjustment_range=fv("input-adj", 15) / 100.0,
            max_catalog_rows=iv("input-rows", 500),
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        st = self.query_one("#settings-status", Static)
        if event.button.id == "btn-save":
            self.app.settings = self._read()
            save_settings(self.app.settings)
            st.update("[bold green]Settings saved.[/]")
        elif event.button.id == "btn-clear":
            clear_simulation_history()
            self.app.simulation_history.clear()
            st.update("[bold yellow]History cleared.[/]")
        elif event.button.id == "btn-reload":
            self.app.reload_data()
            st.update("[bold green]Data reloaded.[/]")
