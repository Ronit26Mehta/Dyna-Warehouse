"""JSON-based persistent storage for user preferences and pricing history."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from .models import AppSettings, PricingAction, SimulationResult

STORAGE_DIR = Path.home() / ".warehouse"


def _ensure_dir():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_settings(settings: AppSettings) -> None:
    """Persist application settings to JSON."""
    _ensure_dir()
    path = STORAGE_DIR / "settings.json"
    path.write_text(json.dumps(settings.to_dict(), indent=2), encoding="utf-8")


def load_settings() -> AppSettings:
    """Load application settings from JSON, or return defaults."""
    path = STORAGE_DIR / "settings.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return AppSettings.from_dict(data)
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    return AppSettings()


def save_simulation(result: SimulationResult) -> None:
    """Append a simulation result to the history file."""
    _ensure_dir()
    path = STORAGE_DIR / "simulations.json"
    history: list[dict] = []
    if path.exists():
        try:
            history = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            history = []

    record = {
        "product_id": result.product_id,
        "product_name": result.product_name,
        "total_reward": round(result.total_reward, 4),
        "avg_reward": round(result.avg_reward, 4),
        "initial_price": round(result.initial_price, 2),
        "final_price": round(result.final_price, 2),
        "steps": result.steps,
        "price_change_pct": round(result.price_change_pct, 2),
        "actions": [
            {
                "step": a.step,
                "old_price": round(a.old_price, 2),
                "new_price": round(a.new_price, 2),
                "reward": round(a.reward, 4),
            }
            for a in result.actions
        ],
    }
    history.append(record)

    # Keep last 200 simulations
    if len(history) > 200:
        history = history[-200:]

    path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def load_simulation_history() -> list[dict]:
    """Load all past simulation results."""
    path = STORAGE_DIR / "simulations.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def clear_simulation_history() -> None:
    """Delete all simulation history."""
    path = STORAGE_DIR / "simulations.json"
    if path.exists():
        path.unlink()


def save_app_state(state: dict[str, Any]) -> None:
    """Save arbitrary app state."""
    _ensure_dir()
    path = STORAGE_DIR / "state.json"
    path.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


def load_app_state() -> dict[str, Any]:
    """Load app state."""
    path = STORAGE_DIR / "state.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}
