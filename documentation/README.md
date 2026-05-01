# Running Xania SPAs on FastAPI

After compiling a Xania SPA, you have several options for serving it.

## Quick Start (Easiest)

### 1. Compile your SPA
```bash
# Your SPA definition (e.g., tutorial.py with SpaApp)
python tutorial.py
# Generates: index.html + static/app.js + static/spa_runtime.js
```

### 2. Serve with one command
```bash
xania serve .
# 🚀 Serving SPA from /home/seems/supreme/documentation
# 📍 http://127.0.0.1:8000
```

That's it! Your SPA is live.

---

## Advanced: Custom FastAPI Integration

### Using `mount_spa()` helper

For SPAs that need custom API routes or middleware:

```python
from fastapi import FastAPI
from xania.web.serve import mount_spa

app = FastAPI()

# Add your custom API routes first
@app.get("/api/hello")
def hello():
    return {"message": "Hello from API!"}

# Then mount the SPA (with history API fallback)
mount_spa(app, "documentation")

# Run with uvicorn
# uvicorn app:app --reload
```

### See full example
```bash
python examples/spa_server.py
```

---

## Workflow Summary

```
┌─────────────────────┐
│ Python SPA Spec     │
│ (tutorial.py)       │
└──────────┬──────────┘
           │ python tutorial.py
           ▼
┌─────────────────────┐
│ Compiled SPA        │
│ - index.html        │
│ - static/app.js     │
│ - static/runtime.js │
└──────────┬──────────┘
           │ xania serve . (or mount_spa in code)
           ▼
┌─────────────────────┐
│ Running on FastAPI  │
│ http://localhost:8000
└─────────────────────┘
```

---

## Options

| Method | Command | Use Case |
|--------|---------|----------|
| **CLI** | `xania serve ./docs` | Simple static SPA, no backend |
| **mount_spa()** | In Python code | SPA + custom API routes |
| **Static hosting** | Any web server | S3, Netlify, Vercel, etc. |

---

## How it Works

- **SPA compilation** converts Python routes + pages to `app.js`
- **mount_spa()** serves `index.html` for all routes (History API fallback)
- Static assets (`/static/`) bypass the fallback
- Your custom `/api/*` routes take precedence

---

## Next Steps

- Add API routes under `/api/*`
- Use `ctx.escapeHtml()` in templates for safety
- Deploy compiled `static/` files to a CDN
- See [examples/](../examples/) for more patterns
