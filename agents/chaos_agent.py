# agents/chaos_agent.py
"""Chaos Agent — randomly mutates HTML locators in the mock server template to test self-healing.

The agent pre-renders the Jinja2 template, then applies random mutations to
CSS IDs used by ProductsPage (e.g. #product-title-1 -> #xyz-abcd-1),
writes the mutated file back, and runs the Playwright tests. If Grok is
available, smart_locator() recovers the broken selectors on the fly.
"""
import hashlib
import random
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMPLATE_PATH = BASE_DIR / "mock_api" / "templates" / "inventory.html"
RENDERED_PATH = BASE_DIR / "mock_api" / "templates" / "inventory_rendered.html"
TEMPLATE_BACKUP = BASE_DIR / "mock_api" / "templates" / "inventory_rendered.html.bak"

# The IDs that ProductsPage depends on — these are the targets for mutation
# After Jinja2 rendering, loop.index is expanded (e.g. 1, 2, 3...)
CHAOS_TARGETS = [
    # (regex pattern to find in rendered HTML, template for replacement)
    (r'id="product-title-(\d+)"', r'id="chaos-title-\1"'),
    (r'id="product-price-(\d+)"', r'id="chaos-price-\1"'),
    (r'id="product-desc-(\d+)"', r'id="chaos-desc-\1"'),
    (r'id="product-image-(\d+)"', r'id="chaos-img-\1"'),
    (r'id="add-to-cart-btn-(\d+)"', r'id="chaos-cart-btn-\1"'),
    (r'id="products-grid"', "id=\"chaos-grid\""),
    (r'id="cart-badge"', "id=\"chaos-badge\""),
    (r'id="sort-select"', "id=\"chaos-sort\""),
]


class ChaosAgent:
    """Agent that injects random locator chaos into the mock server's rendered HTML."""

    def __init__(self, mutation_rate: float = 0.5, seed: int = None):
        """Configure the chaos agent.

        Args:
            mutation_rate: Probability (0.0-1.0) that any given locator is mutated.
                           1.0 = all locators mutated, 0.0 = none.
            seed: Optional random seed for reproducible chaos runs.
        """
        self.mutation_rate = mutation_rate
        if seed is not None:
            random.seed(seed)
        self._mutations_applied: list[str] = []

    def _render_template(self) -> str:
        """Render the Jinja2 template to static HTML."""
        try:
            from jinja2 import Environment, FileSystemLoader
        except ImportError:
            raise RuntimeError("jinja2 is required for chaos injection. Install it: pip install jinja2")

        products_module = Path(__file__).parent.parent / "mock_api" / "products.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location("mock_api.products", products_module)
        products_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(products_module)

        env = Environment(loader=FileSystemLoader(str(TEMPLATE_PATH.parent)))
        template = env.get_template(TEMPLATE_PATH.name)
        return template.render(products=products_module.PRODUCTS)

    def _apply_mutations(self, html: str) -> tuple[str, list[str]]:
        """Apply random mutations to the HTML content.

        Returns:
            (mutated_html, list_of_mutations_applied)
        """
        mutations = []
        mutated = html

        for pattern, replacement_template in CHAOS_TARGETS:
            has_index = r"\1" in replacement_template

            def make_repl(tmpl, has_idx):
                def replace_fn(match):
                    if random.random() >= self.mutation_rate:
                        return match.group(0)
                    if has_idx:
                        expanded = match.expand(tmpl)
                    else:
                        expanded = tmpl
                    mutations.append(f"  {match.group(0)} -> {expanded}")
                    return expanded
                return replace_fn

            mutated = re.sub(pattern, make_repl(replacement_template, has_index), mutated)

        # Update JavaScript getElementById calls to use the new chaos IDs
        if mutations:
            mutated = self._update_js_references(mutated, mutations)

        return mutated, mutations

    def _update_js_references(self, html: str, mutations: list[str]) -> str:
        """Update JavaScript getElementById calls to use the new chaos IDs."""
        prefix_map = {}
        for m in mutations:
            parts = m.split("->")
            if len(parts) == 2:
                old = parts[0].strip().replace('id="', "").replace('"', "")
                new = parts[1].strip().replace('id="', "").replace('"', "")
                old_base = re.sub(r"-\d+$", "", old)
                new_base = re.sub(r"-\d+$", "", new)
                prefix_map[old_base] = new_base

        def js_replace(match):
            func = match.group(1)
            qid = match.group(2)
            for old_base, new_base in prefix_map.items():
                if old_base in qid:
                    qid = qid.replace(old_base, new_base, 1)
                    break
            return f'{func}("{qid}")'

        return re.sub(
            r"(getElementById\s*\()[\"']([^\"']+)[\"'](\))",
            js_replace,
            html
        )

    def inject_chaos(self) -> list[str]:
        """Pre-render the Jinja2 template, apply mutations, write mutated rendered HTML.

        We write a separate "rendered" HTML file that the FastAPI server can serve
        in place of the dynamic template — effectively freezing the chaos.
        """
        if not TEMPLATE_PATH.exists():
            raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")

        # Render the Jinja2 template to static HTML
        rendered_html = self._render_template()
        RENDERED_PATH.write_text(rendered_html, encoding="utf-8")

        # Backup existing rendered file
        backup_path = Path(str(RENDERED_PATH) + ".bak")
        if RENDERED_PATH.exists():
            shutil.copy(RENDERED_PATH, backup_path)

        # Apply mutations to the rendered HTML
        mutated_html, mutations = self._apply_mutations(rendered_html)

        if mutations:
            RENDERED_PATH.write_text(mutated_html, encoding="utf-8")
            print(f"[ChaosAgent] Injected {len(mutations)} mutations:")
            for m in mutations:
                print(f"    {m}")
            print(f"[ChaosAgent] Mutated HTML written to: {RENDERED_PATH}")
        else:
            print("[ChaosAgent] No mutations applied (mutation_rate too low or no targets matched)")

        self._mutations_applied = mutations
        return mutations

    def restore(self):
        """Restore the original rendered file from backup."""
        backup_path = Path(str(RENDERED_PATH) + ".bak")
        if backup_path.exists():
            shutil.copy(backup_path, RENDERED_PATH)
            backup_path.unlink()
            print("[ChaosAgent] Template restored to original state")
        else:
            print("[ChaosAgent] No backup found to restore")

    @property
    def is_chaos_active(self) -> bool:
        """Returns True if chaos is currently active (mutations were applied)."""
        return len(self._mutations_applied) > 0


if __name__ == "__main__":
    # CLI for manual testing: python -m agents.chaos_agent --rate 1.0
    import argparse

    parser = argparse.ArgumentParser(description="Chaos Agent — inject locator mutations")
    parser.add_argument("--rate", type=float, default=1.0, help="Mutation rate 0.0-1.0")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--restore", action="store_true", help="Restore original template")
    args = parser.parse_args()

    agent = ChaosAgent(mutation_rate=args.rate, seed=args.seed)

    if args.restore:
        agent.restore()
    else:
        agent.inject_chaos()
