# Xania — Python UI Framework for SPAs

**Build fast, interactive web apps entirely in Python. No JavaScript required.**

Xania compiles Python code to standalone Single-Page Applications (SPAs) that run 100% in the browser.

## Features

- **Write UI in Python** – VDOM elements, components, state management
- **Compile to JavaScript** – Your Python spec → `index.html` + `app.js`
- **Deploy anywhere** – Static SPA with no server needed
- **Production-ready** – Built on FastAPI with auth, rate limiting, CSRF protection
- **Zero client-side code** – Framework handles all routing, state, and rendering

## Quick Start

### Requirements
- Python **3.12+**

### 1. Create a new project

```bash
pip install xania
xania init my_website
cd my_website
```

### 2. Edit your site

Edit `app.py` to add pages and content:

```python
from xania import SpaApp, StaticPage, Div, H1, Button

app = SpaApp(name="MySite")

app.route(
    "/",
    StaticPage(
        title="Home",
        html='<h1>Welcome!</h1><p>Built with Xania</p>'
    )
)
```

### 3. Compile

```bash
python app.py
# Generates: index.html + static/app.js + static/spa_runtime.js
```

### 4. Run

```bash
xania serve .
# 🚀 Serving SPA from /path/to/my_website
# 📍 http://127.0.0.1:8000
```

Open your browser to `http://127.0.0.1:8000`

### 5. Deploy

Copy the generated files to any static host:

```bash
# Upload to Netlify, Vercel, GitHub Pages, S3, etc.
cp -r . /path/to/deployment/
```

## How It Works

### SPA Mode (Recommended)

1. **Define your app in Python** – Use `SpaApp` with routes and pages
2. **Compile** – Xania generates JavaScript that runs entirely in the browser
3. **Deploy** – Copy `index.html` + `static/` to any static host

No server needed for the SPA itself. Client-side routing via History API.

```python
from xania import SpaApp, StaticPage

app = SpaApp(name="MySite")
app.route("/", StaticPage(title="Home", html="..."))
app.route("/about", StaticPage(title="About", html="..."))

# Then: python app.py  →  generates index.html + app.js
```

### Server Mode (Advanced)

If you need a backend, integrate with FastAPI:

```python
from fastapi import FastAPI
from xania import mount_spa

app = FastAPI()

# Add API routes
@app.get("/api/data")
def get_data():
    return {"items": [...]}

# Mount compiled SPA
mount_spa(app, ".")
```

Then: `xania serve .` or `uvicorn app:app`

---

## Two Modes Explained

**SPA Mode** (Default)
- HTML shell + JavaScript SPA
- Client-side routing (History API)
- No server needed for UI
- Perfect for: static sites, blogs, documentation, dashboards
- Deploy to: Netlify, Vercel, GitHub Pages, S3

**Server Mode** (Optional)
- FastAPI backend + SPA frontend
- Add custom APIs, auth, data
- Still compiles to static files
- Perfect for: full-stack apps with complex backends
- Deploy to: Heroku, Railway, AWS, DigitalOcean

---

## Core Concepts

**VDOM Elements** – Python classes representing HTML:

```python
from xania import Div, H1, Button, Input

Div(
    H1("Welcome"),
    Input(type="text", placeholder="Enter name"),
    Button("Click me", onclick="App.dispatch('Counter', 'click')"),
    class_name="flex flex-col gap-4"
)
```

**Components** – Stateful UI units:

```python
from xania import Component, Div, Span, Button

class Counter(Component):
    def initial_state(self):
        return {"count": 0}
    
    def render(self, state):
        return Div(
            Span(str(state.count)),
            Button("+", onclick="App.dispatch('Counter', 'inc')")
        )
    
    def on_inc(self, state, payload):
        state.count += 1
```

**Pages** – Routes in your SPA:

```python
from xania import SpaApp, StaticPage, TemplatePage, JsExpr

app = SpaApp()

# Static page
app.route("/", StaticPage(
    title="Home",
    html="<h1>Welcome</h1>"
))

# Template page with placeholders
app.route("/user/{id}", TemplatePage(
    title="User",
    template="<h1>User {name}</h1>",
    placeholders={"name": "John"}
))
```

---

## Project Structure

**Core Modules:**
- `renderer/` – VDOM elements, components, state management
- `runtime/` – SPA compiler (Python → JavaScript)
- `web/` – FastAPI integration, serving, auth
- `static/` – Browser runtime (`spa_runtime.js`)
- `cli.py` – Command-line interface

**See also:** [documentation/](documentation/) for full tutorial SPA built with Xania

---

## Examples

### Counter with State

```python
from xania import Component, Div, Button, Span

class Counter(Component):
    def initial_state(self):
        return {"count": 0}
    
    def render(self, state):
        return Div(
            Span(f"Count: {state.count}"),
            Button("+", onclick="App.dispatch('Counter', 'inc')"),
            Button("-", onclick="App.dispatch('Counter', 'dec')"),
        )
    
    def on_inc(self, state, payload):
        state.count += 1
    
    def on_dec(self, state, payload):
        state.count -= 1
```

### Multi-Page SPA

```python
from xania import SpaApp, StaticPage, TemplatePage

app = SpaApp(name="MyBlog")

# Home page
app.route("/", StaticPage(
    title="Home",
    html="<h1>Welcome to My Blog</h1>"
))

# About page
app.route("/about", StaticPage(
    title="About",
    html="<h1>About Me</h1><p>I build with Xania.</p>"
))

# Post page with placeholders
app.route("/post/{id}", TemplatePage(
    title="Post",
    template="<h1>{title}</h1><p>{content}</p>",
    placeholders={"title": "My First Post", "content": "..."}
))
```

---

## Deployment

### Option 1: Static Hosting (Simplest)

```bash
# Compile
python app.py

# Upload everything to your host
# - Netlify (drag & drop)
# - Vercel (git integration)
# - GitHub Pages
# - S3 + CloudFront
```

### Option 2: FastAPI Server

```python
# serve.py
from fastapi import FastAPI
from xania import mount_spa

app = FastAPI()

@app.get("/api/hello")
def hello():
    return {"message": "Hello from API!"}

mount_spa(app, ".")
```

```bash
# Local: uvicorn serve:app --reload
# Production: gunicorn serve:app (on Heroku, Railway, etc.)
```

---

## Development

Clone and install:

```bash
git clone https://github.com/xania/framework.git
cd xania
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run examples:

```bash
xania serve documentation      # Full tutorial
xania dev                      # Dev server
```

---

## Contributing

PRs welcome! See [GitHub](https://github.com/xania/framework)
- DOM events calling `App.dispatch('Counter', 'increment')`

## Tags / Elements (VDOM)

Xania’s “tags” are Python functions/classes that build a VDOM tree in `renderer/elements.py`.

- **Use built-in tag helpers**: `Div(...)`, `Span(...)`, `Button(...)`, `H1(...)`, etc.
- **Use `Element(tag, ...)` for any HTML tag** (even if there is no helper yet):

```python
from renderer.elements import Element

node = Element("section", "Hello")
```

### Children
- **Text children**: strings (they are HTML-escaped by `engine/serializer.py`)
- **Element children**: nested `Element` instances
- **Lists**: spread them with `*items` when building children

### Attributes (“props”)
Attributes are passed as keyword args:

- **`class_name` → `class`**
- **`for_` → `for`**
- **`http_equiv` → `http-equiv`**
- **Any `_` becomes `-`** (e.g. `data_component="Counter"` → `data-component="Counter"`)
- **Booleans**:
  - `disabled=True` renders `disabled`
  - `disabled=False` omits it

Example:

```python
from renderer.elements import Button

Button(
    "Click",
    class_name="px-3 py-2 rounded",
    data_component="Counter",
    disabled=False,
)
```

## Registering components

In `app.py`:

```python
from renderer.registry import ComponentRegistry
from example.counter import Counter

ComponentRegistry.register("Counter", Counter(id="counter"))
```

The string `"Counter"` must match what the client dispatches:

```html
onclick="App.dispatch('Counter','increment')"
```

## Web API

### `GET /`
Returns the HTML shell (mount points + `<script src="/static/runtime.js">`).

### `POST /event`
Request (`web/schemas.py`):

```json
{
  "component": "Counter",
  "action": "increment",
  "payload": {}
}
```

Response:

```json
{
  "updates": [
    { "id": "counter", "html": "<div>...</div>" }
  ]
}
```

The client applies updates by doing `document.getElementById(id).innerHTML = html`.

## Publish readiness (honest checklist)

This codebase is **a solid architectural baseline**, but it is **not ready to publish as a production framework** yet. Here’s what’s missing / risky:

- **Session/user isolation**: `ComponentRegistry` stores **singletons** in-process.
  - In production you need per-user (cookie/session) component instances or a state store.
- **Concurrency & scaling**:
  - Multiple workers/processes will not share component state.
  - Need a storage layer (Redis/DB) or stateless model (client-owned state + patches).
- **Security**:
  - `onclick="App.dispatch(...)"` is safe here because HTML is generated server-side, but any user-provided text/attrs must be carefully validated.
  - Consider CSRF protection for `/event`.
  - Demo auth exists for stress-testing, but production needs strong secrets + HTTPS-only cookies + real user storage.
- **Performance**:
  - Current updates replace `innerHTML` of the whole component.
  - Next step: **diffing + patching** (you already have a base architecture for it).
- **Testing**:
  - No unit tests or integration tests yet.
- **Packaging polish**:
  - Ensure `pyproject.toml` metadata is correct (name/urls/authors).
  - Add a changelog and decide versioning strategy.

## Roadmap (recommended next steps)

- Add per-session registry/state store (cookie -> component state)
- Add diff/patch engine (update minimal DOM, not full `innerHTML`)
- Add router + multipage CSR navigation
- Add test suite + CI
- Add docs site and examples gallery

## Publish checklist (minimal)

- **Package identity**: confirm `pyproject.toml` name/version/description are correct.
- **License**: ensure `LICENSE` exists and matches `pyproject.toml` (`MIT` here).
- **Versioning**: adopt SemVer (`0.x` while APIs are changing quickly).
- **README**: keep Quick start + minimal example runnable.
- **Security**: decide on CSRF/auth strategy for `/event` before public deploys.
- **State model**: decide per-user state persistence (sessions/Redis) before scaling.
- **CI**: add at least `python -m py_compile` + basic tests on every push.

## Demo auth (stress testing only)

This repo includes a minimal cookie-session auth demo used by the SPA stress page:

- Login endpoint: `POST /api/auth/login` (demo user: `admin/admin`)
- Logout endpoint: `POST /api/auth/logout`
- Current user: `GET /api/auth/me`
- Protected stress endpoints: `GET /api/private/big-json`, `POST /api/private/write-echo`

Environment variables:

- `XANIA_ENV=dev|prod` (default `dev`)
- `XANIA_SECRET_KEY=...` (required when `XANIA_ENV` is not dev)
- `XANIA_COOKIE_SECURE=true|false` (defaults to true outside dev)
