# Supreme (Python UI Framework, React-like)

Supreme is a **minimal, production-oriented** Python UI framework built on **FastAPI** that provides:

- **VDOM elements in Python** (`renderer/elements.py`)
- **Component system** with state + hooks (`renderer/component.py`, `renderer/state.py`)
- **Client-side rendering** (CSR) via a tiny runtime (`static/runtime.js`)
- **Event-driven updates** via a single backend endpoint (`POST /event`)

This repository currently ships a working example (`example/counter.py`) and a clean, extensible architecture you can build on (diffing/hydration later).

## Quick start

### Requirements
- Python **3.14+** (per `pyproject.toml`)

### Run

```bash
cd supreme
source .venv/bin/activate  # if you use a venv
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/`.

## Core idea (CSR, no SSR)

- `GET /` returns an HTML **shell** with mount points and a script tag:
  - `<div id="counter" data-component="Counter"></div>`
  - `<script src="/static/runtime.js"></script>`
- `static/runtime.js` mounts components by calling:
  - `POST /event` with `{ component, action: "__mount__", payload: {} }`
- UI events call:
  - `onclick="App.dispatch('Counter','increment')"`

Important: **state changes do not automatically trigger backend requests**. The backend is only called when the browser calls `App.dispatch(...)`.

## Project structure (strict)

```text
renderer/
  __init__.py
  elements.py        # VDOM elements (Element/VoidElement)
  render.py          # render(Element) -> HTML string
  state.py           # State + hooks (useState/useRef)
  component.py       # Base Component class
  registry.py        # Component registry

engine/
  runtime.py         # HTML shell generator (no inline JS)
  serializer.py      # Safe HTML serialization (escaping)

web/
  routes.py          # FastAPI routes (API layer)
  schemas.py         # Request/response models (Pydantic)

static/
  runtime.js         # Client runtime (window.App)

app.py               # FastAPI entry point

example/
  counter.py         # Example component
```

## Component API

Create a component by subclassing `renderer.component.Component`.

Key rules:
- Every component has a **stable** `id` (used as DOM mount target).
- `render(state)` returns `renderer.elements.Element` trees (or text).
- Event handlers are methods named `on_<action>(state, payload)`.

Example (`example/counter.py`) uses:

- `render()` returning `Div(...)`
- `on_increment()` mutating `state.count`
- DOM events calling `App.dispatch('Counter', 'increment')`

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
- **Performance**:
  - Current updates replace `innerHTML` of the whole component.
  - Next step: **diffing + patching** (you already have a base architecture for it).
- **Testing**:
  - No unit tests or integration tests yet.
- **Packaging polish**:
  - `pyproject.toml` project name/metadata is placeholder (`name = "shohana"`).
  - Add license, classifiers, long description, and versioning strategy.

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
# python-fullstack-web-
# python-fullstack-web-
