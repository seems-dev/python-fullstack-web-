# Xania Architecture & Design Principles

## What Xania Is

Xania is a **static-first Python web framework** optimized for:

- ✅ Content-heavy websites (blogs, documentation, portfolios)
- ✅ Multi-page SPA navigation without full JavaScript frameworks
- ✅ Server-side rendering with type-safe Python
- ✅ SEO-friendly static site generation
- ✅ Fast page loads (thin runtime, no bloat)

## What Xania Is NOT (By Design)

Xania is **not** a real-time reactive framework like React, Vue, or Svelte. That's intentional.

- ❌ No live reactive state (components update on demand, not automatically)
- ❌ No event handlers (clicks, form submissions, etc.)
- ❌ No client-side routing updates (full page loads on navigation)
- ❌ No WebSocket or real-time features
- ❌ Not designed for complex interactive applications

## Design Philosophy

### 1. Separation of Concerns

**Python layer** (server-side):
- Build HTML with type-safe Python
- Compose components and pages
- Generate static files or serve dynamic content

**JavaScript layer** (client-side):
- Navigate between pages
- Basic runtime support (minimal footprint)
- Progressive enhancement hooks (future)

### 2. Progressive Enhancement

The framework is designed with progressive enhancement in mind:

1. **Tier 0** (current): Pure HTML + CSS via Tailwind
2. **Tier 1** (future): Event handlers for basic interaction
3. **Tier 2** (future, optional): Component state management

This keeps the framework simple and fast.

### 3. Explicit Over Implicit

- No magic: All data flow is explicit
- No global state: Context and props are passed explicitly
- No hidden dependencies: Imports are clear

## Current Architecture

```
┌─────────────────────┐
│   Your Pages        │
│  (Python code)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Xania Framework   │
│  - Element builder  │
│  - Component model  │
│  - Page rendering   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   SPA Compiler      │
│  - Generates JS     │
│  - Creates HTML     │
│  - Bundles assets   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Static Output     │
│  - index.html       │
│  - /static/app.js   │
│  - /static/assets   │
└─────────────────────┘
```

## Component Model

Components are the primary unit of composition:

```python
from xania import component, Div, H1, P

@component(props={"title": str, "count": int})
def Card(ctx):
    return Div(
        H1(ctx.props["title"]),
        P(f"Items: {ctx.props['count']}"),
        class_name="p-4 border rounded"
    )

# Usage
card = Card(title="My Card", count=42)
html = card.to_html()
```

**Benefits:**
- Props are type-checked
- Metadata available for introspection
- Can be composed into larger components
- Consistent rendering

## Future: Event Handlers (Planned)

When interactivity is needed, the pattern would be:

```python
@component(props={"initial": int})
def Counter(ctx):
    count = ctx.props["initial"]
    
    return Div(
        P(f"Count: {count}"),
        Button(
            "+1",
            on_click=ctx.on_increment,  # Future: event handler
            class_name="btn"
        )
    )
```

This would:
1. Keep component definitions in Python
2. Auto-generate JS event handlers
3. Persist state server-side (per session)
4. Use the existing `State` class for server-side data

**Design principle**: Keep components testable and debuggable in Python, not tied to JS logic.

## When to Use Xania

| Use Case | Xania | Not Xania |
|----------|-------|----------|
| Blog/documentation site | ✅ Great fit | N/A |
| Portfolio/resume | ✅ Great fit | N/A |
| Marketing site | ✅ Great fit | N/A |
| Static site generator | ✅ Great fit | N/A |
| Dashboard with real-time updates | ❌ Not ideal | Use Streamlit/React |
| Chat app | ❌ Not ideal | Use Socket.io/WebSocket |
| Collaborative editor | ❌ Not ideal | Use Yjs/OT |
| Complex SPA (many interactions) | ⚠️ Possible but heavy | Use React/Vue |

## Design Trade-offs

### ✅ Advantages

- Simple mental model (server renders Python → HTML)
- Type-safe (use Python's type system)
- SEO-friendly (pure HTML output)
- Fast (minimal runtime, no bloat)
- Easy testing (components are functions)
- Pythonic (no template language to learn)

### ⚠️ Limitations

- Not ideal for highly interactive apps
- No live state binding (page reloads to update)
- Learning curve for component composition
- Limited reusable libraries (ecosystem is new)

## Best Practices

1. **Use components** for all reusable UI patterns
2. **Keep pages simple** — views that compose components
3. **Use the PageContext** — explicit data passing
4. **Test components** — they're just functions
5. **Organize by feature** — not all code in app.py
6. **Document pages** — each page module should have docstring

## Roadmap

### Phase 1 (Current) ✅
- ✅ Element builder API
- ✅ Component model with @decorator
- ✅ StaticPage and TemplatePage
- ✅ Type-safe props validation
- ✅ SPA compilation

### Phase 2 (Planned)
- Event handlers for buttons, forms
- Server-side state persistence
- Form validation
- Better error messages

### Phase 3 (Future)
- Optional client-side state (signals/reactive)
- Component library
- Better dev tools and debugging
- Performance optimizations

## Architecture Decisions Explained

### Why Server-Side Rendering?

- **Simplicity**: Build UIs with Python, not JS
- **Performance**: No massive JS bundles
- **SEO**: Content is in HTML, search engines see it
- **Accessibility**: Progressive enhancement works better

### Why Component Decorator?

- **Consistency**: All components follow same pattern
- **Type safety**: Props are validated
- **Tooling**: IDE can help with completion
- **Future-proofing**: Can add lifecycle hooks later

### Why PageContext?

- **Explicitness**: No hidden data flow
- **Type-safety**: IDE knows what's available
- **Composability**: Context can be nested
- **Testing**: Easy to mock for testing

## Extending Xania

You can extend the framework:

```python
# Custom component
@component(props={"items": list})
def MyComponent(ctx):
    return Div(*[item for item in ctx.props["items"]])

# Custom page factory
def create_dynamic_page(data):
    return StaticPage(
        title=data["title"],
        html=MyComponent(items=data["items"]).to_html()
    )

# Register with app
app.route("/items", create_dynamic_page(my_data))
```

This keeps extensions simple and Pythonic.

---

**Summary**: Xania is a static-first framework that makes it easy to build content-heavy websites with Python. It's not for everything, but for what it's designed for, it's excellent.
