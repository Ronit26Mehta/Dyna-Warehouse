# Contributing to Warehouse

Thank you for considering contributing to **Warehouse**! This document outlines the process for submitting changes and our coding standards.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/warehouse.git
   cd warehouse
   ```
3. **Create a virtual environment** and install in editable mode:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate    # Windows
   pip install -e .
   ```
4. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Guidelines

### Code Style

- Follow **PEP 8** conventions
- Use **type hints** for all function signatures
- Use **dataclasses** for data models
- Keep functions focused — one responsibility per function
- Add docstrings to all public classes and functions

### Architecture Rules

- **Screens** go in `warehouse/screens/` — one file per screen
- **Widgets** go in `warehouse/widgets.py` — reusable UI components only
- **Models** go in `warehouse/models.py` — data-only, no UI logic
- **No computation in screens** — all data should be precomputed and accessed via `self.app.data`
- **No async/Worker** — synchronous loading with pickle caching for performance

### CSS Styling

- All styles go in `warehouse/app.tcss`
- Use semantic IDs (`#dashboard-container`, `#kpi-row`)
- Avoid inline styles in Python code
- Use `overflow-x: hidden` on all panels to prevent bleedthrough

---

## Submitting Changes

1. **Test** your changes by running the app:
   ```bash
   warehouse --data ./data
   ```
2. Verify all screens load without errors
3. **Commit** with a clear, descriptive message:
   ```bash
   git commit -m "Add: new screen for price history visualization"
   ```
4. **Push** to your fork and open a **Pull Request**

### Commit Message Format

- `Add:` — New features
- `Fix:` — Bug fixes
- `Refactor:` — Code restructuring without behavior change
- `Docs:` — Documentation updates
- `Style:` — CSS or formatting changes

---

## Reporting Bugs

Open an issue with:
- **Description** of the bug
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Terminal** and **OS** information
- Full traceback if applicable

---

## Feature Requests

Open an issue describing:
- **What** you'd like to see
- **Why** it would be useful
- **How** you envision it working (optional)

---

## Code of Conduct

Be respectful, constructive, and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).
