# mock_api/main.py
"""FastAPI mock server that simulates the SauceDemo backend + HTML frontend."""
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template

from mock_api.products import PRODUCTS

# --- App setup ---------------------------------------------------------------

app = FastAPI(title="Swag Labs Mock API")

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
RENDERED_HTML = TEMPLATES_DIR / "inventory_rendered.html"

# In-memory session store: session_id -> username
sessions: dict[str, str] = {}
# In-memory cart store: session_id -> list of product_ids
carts: dict[str, list[str]] = {}


# --- Helpers -----------------------------------------------------------------

def _load_template(name: str) -> str:
    with open(TEMPLATES_DIR / name, encoding="utf-8") as f:
        return f.read()


def _render_inventory() -> str:
    """Render the inventory page.

    If a chaos-mutated HTML file exists (from ChaosAgent), serve it instead.
    This allows the chaos agent to break locators and have Playwright self-heal.
    """
    if RENDERED_HTML.exists():
        return RENDERED_HTML.read_text(encoding="utf-8")
    template = Template(_load_template("inventory.html"))
    return template.render(products=PRODUCTS)


# --- Auth endpoints ----------------------------------------------------------

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)) -> Response:
    """Authenticate user and return a session cookie."""
    if not username or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    session_id = f"sess_{username}_{os.urandom(8).hex()}"
    sessions[session_id] = username
    carts[session_id] = []

    response = JSONResponse(content={"message": "Login successful", "user": username})
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        path="/",
    )
    return response


# --- Product endpoints -------------------------------------------------------

@app.get("/products")
def get_products() -> JSONResponse:
    """Return the product catalog as JSON."""
    return JSONResponse(content=PRODUCTS)


# --- Cart endpoints ----------------------------------------------------------

def _get_cart(session_id: Optional[str]) -> list[dict]:
    if not session_id or session_id not in sessions:
        return []
    return [
        {**p, "quantity": carts[session_id].count(p["id"])}
        for p in PRODUCTS
        if carts[session_id].count(p["id"]) > 0
    ]


@app.get("/cart")
def get_cart(session_id: Optional[str] = Cookie(None)) -> JSONResponse:
    """Return current cart contents."""
    return JSONResponse(content=_get_cart(session_id))


@app.post("/cart")
def add_to_cart(payload: dict, session_id: Optional[str] = Cookie(None)) -> JSONResponse:
    """Add a product to the cart."""
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")

    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="Missing product_id")

    product = next((p for p in PRODUCTS if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    carts[session_id].append(product_id)
    return JSONResponse(content={"message": "Added", "cart": _get_cart(session_id)})


@app.delete("/cart")
def clear_cart(session_id: Optional[str] = Cookie(None)) -> JSONResponse:
    """Clear the cart."""
    if session_id and session_id in sessions:
        carts[session_id] = []
    return JSONResponse(content={"message": "Cart cleared"})


# --- HTML page endpoints -----------------------------------------------------

@app.get("/inventory.html", response_class=HTMLResponse)
def inventory_page(session_id: Optional[str] = Cookie(None)) -> HTMLResponse:
    """Serve the inventory HTML page (protected by session)."""
    if not session_id or session_id not in sessions:
        # Redirect to login
        return HTMLResponse(content="<h1>Please <a href='/'>login</a> first.</h1>", status_code=401)

    return HTMLResponse(content=_render_inventory())


@app.get("/", response_class=HTMLResponse)
def root() -> HTMLResponse:
    """Simple login page."""
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head><title>Login</title></head>
        <body style="font-family:sans-serif;padding:2rem;text-align:center">
            <h1>Swag Labs</h1>
            <p>Session-based auth demo</p>
            <form method="post" action="/login" style="display:inline-grid;gap:1rem;max-width:300px;margin:auto">
                <input name="username" placeholder="Username" required style="padding:0.5rem" />
                <input name="password" type="password" placeholder="Password" required style="padding:0.5rem" />
                <button type="submit" style="padding:0.5rem;background:#3d5a80;color:white;border:none;border-radius:4px;cursor:pointer">Login</button>
            </form>
        </body>
        </html>
        """,
        status_code=200,
    )
