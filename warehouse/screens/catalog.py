"""Product Catalog screen — paginated product browsing."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Input, Static, Tree

from ..widgets import SectionHeader

PAGE_SIZE = 200


class CatalogScreen(Screen):
    """Browse all products with category filtering, search, and pagination."""

    BINDINGS = [
        ("d", "app.go_dashboard", "Dashboard"),
        ("p", "app.go_pricing", "Pricing"),
        ("a", "app.go_analytics", "Analytics"),
        ("escape", "app.pop_screen", "Back"),
        ("n", "next_page", "Next Page"),
        ("b", "prev_page", "Prev Page"),
    ]

    def __init__(self):
        super().__init__()
        self._page = 0
        self._filtered: list = []
        self._category: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="catalog-container"):
            yield SectionHeader("Product Catalog")
            with Horizontal(id="catalog-toolbar"):
                yield Input(placeholder="Search products...", id="search-input")
                yield Static("  Filter: All Categories", id="filter-label")

            with Horizontal(id="catalog-body"):
                with Vertical(id="category-tree-panel"):
                    yield SectionHeader("Categories")
                    tree: Tree[str] = Tree("All Products", id="category-tree")
                    tree.root.expand()
                    yield tree

                with Vertical(id="product-table-panel"):
                    yield DataTable(id="product-table", cursor_type="row")
                    yield Static("", id="product-count")
        yield Footer()

    def on_mount(self) -> None:
        self._build_tree()
        self._apply_filter()

    def _build_tree(self) -> None:
        tree = self.query_one("#category-tree", Tree)
        for cat, count in self.app.category_counts.items():
            tree.root.add_leaf(f"{cat} ({count:,})")

    def _apply_filter(self, search: str = "") -> None:
        products = self.app.products
        f = products
        if self._category:
            f = [p for p in f if p.category == self._category]
        if search:
            sl = search.lower()
            f = [p for p in f if sl in p.name.lower()]
        self._filtered = f
        self._page = 0
        self._render_page()

    def _render_page(self) -> None:
        table = self.query_one("#product-table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Product Name", "Category", "Price", "Unit")

        start = self._page * PAGE_SIZE
        end = start + PAGE_SIZE
        page = self._filtered[start:end]

        for p in page:
            price = f"${p.price:,.2f}" if p.price > 0 else "—"
            table.add_row(str(p.sample_id), p.display_name, p.category, price, p.unit or "—")

        total = len(self._filtered)
        pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        self.query_one("#product-count", Static).update(
            f"  Page {self._page + 1}/{pages} | "
            f"{start + 1}–{min(end, total):,} of {total:,} | "
            f"[bold cyan]N[/]=Next [bold cyan]B[/]=Prev"
        )

    def action_next_page(self) -> None:
        pages = max(1, (len(self._filtered) + PAGE_SIZE - 1) // PAGE_SIZE)
        if self._page < pages - 1:
            self._page += 1
            self._render_page()

    def action_prev_page(self) -> None:
        if self._page > 0:
            self._page -= 1
            self._render_page()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-input":
            self._apply_filter(search=event.value)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        label = str(event.node.label)
        if label == "All Products":
            self._category = None
            display = "All Categories"
        else:
            self._category = label.split(" (")[0] if " (" in label else label
            display = self._category

        self.query_one("#filter-label", Static).update(f"  Filter: {display}")
        search = self.query_one("#search-input", Input).value
        self._apply_filter(search=search)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = self.query_one("#product-table", DataTable)
        row = table.get_row(event.row_key)
        if row:
            self.app.selected_product_id = int(row[0])
            self.app.push_screen("product_detail")
