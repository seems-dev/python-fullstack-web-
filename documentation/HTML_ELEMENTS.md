# HTML Elements in Xania

Xania provides Python helpers for all HTML elements, including `<script>` and `<style>`. **You don't need to write raw HTML strings** — use Python element functions instead.

## Available Elements

All standard HTML elements are available as Python functions in `xania.renderer.elements`:

- **Block elements**: `Div()`, `Section()`, `Article()`, `Header()`, `Footer()`, `Nav()`, etc.
- **Text elements**: `H1()`, `H2()`, `P()`, `Span()`, `Strong()`, `Em()`, etc.
- **Form elements**: `Form()`, `Input()`, `Label()`, `Select()`, `Textarea()`, etc.
- **Special elements**: `Script()`, `Style()`, `Details()`, `Dialog()`, etc.

## Script Element

### Basic Usage

Instead of writing raw HTML:
```python
html='''<script>
console.log("Hello from Xania!");
</script>'''
```

Use the `Script()` function:
```python
from xania.renderer.elements import Script

Script('console.log("Hello from Xania!");')
```

### With Attributes

Add scripts from CDN with attributes:
```python
from xania.renderer.elements import Script

# External script
Script(src="https://cdn.example.com/lib.js", async_=True)

# Inline script with type attribute
Script('alert("Hello!");', type="module")
```

### Common Attributes

- `src`: Load script from URL
- `async_`: Execute asynchronously (use `async_` instead of `async` in Python)
- `defer`: Defer script execution
- `type`: Script type (e.g., `"module"`, `"application/json"`)

## Style Element

### Basic Usage

Instead of raw HTML:
```python
html='''<style>
body { background: blue; }
</style>'''
```

Use the `Style()` function:
```python
from xania.renderer.elements import Style

Style('body { background: blue; color: white; }')
```

### CSS Blocks

Create more complex styles:
```python
from xania.renderer.elements import Style

css_content = """
.card {
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 8px;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
"""

Style(css_content)
```

## Building Pages with Elements

Instead of raw HTML strings, build your entire page using element functions:

### Example: Page with Custom Styles and Scripts

```python
from xania.runtime.spa import SpaApp, StaticPage
from xania.renderer.elements import Div, H1, P, Style, Script

app = SpaApp(name="MyApp", root_id="app")

# Create page with styled content and inline script
page_content = Div(
    Style("""
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4rem 2rem;
            text-align: center;
            border-radius: 8px;
        }
        .hero h1 {
            font-size: 2.5rem;
            margin: 0;
        }
    """),
    
    Div(
        H1("Welcome to Xania"),
        P("Build beautiful UIs with Python, not raw HTML"),
        class_="hero"
    ),
    
    Script("""
        document.addEventListener('DOMContentLoaded', () => {
            console.log('Page loaded! No raw HTML needed.');
        });
    """)
)

app.route("/", StaticPage(title="Home", html=page_content.render()))

if __name__ == "__main__":
    from xania.runtime.compiler import SpaCompiler
    from pathlib import Path
    compiler = SpaCompiler(title="My App", tailwind=True)
    compiler.write(app, Path.cwd())
```

## Benefits of Using Element Functions

✅ **Pythonic** — Use Python syntax, not string templates
✅ **Type-safe** — Catch mistakes before rendering
✅ **Composable** — Build complex UIs from simple components
✅ **Readable** — Clear structure, no escaping issues
✅ **Maintainable** — Refactor easily without string manipulation

## Rendering Elements to HTML

All elements have a `.render()` method:

```python
from xania.renderer.elements import Div, H1, Style

element = Div(
    H1("Hello"),
    Style("h1 { color: blue; }"),
    class_="container"
)

html_string = element.render()
# Output: <div class="container"><h1>Hello</h1><style>h1 { color: blue; }</style></div>
```

Or use the `.to_dict()` method for serialization:

```python
element.to_dict()
# Returns: {
#   "tag": "div",
#   "attrs": {"class": "container"},
#   "children": [
#     {"tag": "h1", "children": ["Hello"]},
#     {"tag": "style", "children": ["h1 { color: blue; }"]}
#   ]
# }
```

## Complete Element Reference

### Block Elements
`Div`, `Section`, `Article`, `Aside`, `Header`, `Footer`, `Main`, `Nav`, `Ul`, `Ol`, `Li`, `Table`, `Thead`, `Tbody`, `Tr`, `Th`, `Td`, `Form`, `Select`, `Option`, `Textarea`, `Label`, `Fieldset`, `Legend`, `Details`, `Summary`, `Dialog`

### Text Elements
`H1`, `H2`, `H3`, `H4`, `H5`, `H6`, `P`, `Span`, `A`, `Strong`, `Em`, `B`, `I`, `U`, `S`, `Code`, `Pre`, `Blockquote`, `Small`, `Mark`, `Sub`, `Sup`

### Special Elements
`Button`, `Script`, `Style`

### Void/Self-closing Elements
`Img`, `Input`, `Br`, `Hr`, `Meta`, `Link`, etc.

## Next Steps

- Check [tutorial.py](tutorial.py) for a complete working example
- See [README.md](README.md) for compilation and deployment instructions
- Build your first SPA with Xania!
