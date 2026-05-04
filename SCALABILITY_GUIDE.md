# Xania Scalability Guide: Multi-Module Page Organization

## Problem

When all pages are defined in a single `app.py`, the file becomes unmaintainable at scale:

```python
# app.py (2000+ lines)
from xania import SpaApp, StaticPage
from xania import Div, H1, P, A

app = SpaApp()

# Home page (50 lines)
home_html = Div(
    H1("Welcome"),
    P("..."),
).render()
app.route("/", StaticPage(title="Home", html=home_html))

# About page (40 lines)
# Blog post page (80 lines)
# Contact page (120 lines)
# ... 15 more pages
```

## Solution: Module-Based Organization

Organize pages into feature-based modules, with a registry pattern that keeps `app.py` clean.

### Directory Structure

```
my_app/
├── app.py                 # Main entry point (stays small)
├── pages/
│   ├── __init__.py        # Page registration function
│   ├── home.py            # Home page
│   ├── about.py           # About page
│   ├── blog/
│   │   ├── __init__.py
│   │   ├── index.py       # Blog index
│   │   └── post.py        # Individual post
│   └── contact.py         # Contact page
└── components/            # Shared components
    ├── navbar.py
    ├── footer.py
    └── card.py
```

### Example Implementation

#### `pages/home.py`
```python
"""Home page module."""
from xania import StaticPage, PageContext, Div, H1, P, component

@component()
def HeroSection(ctx):
    from xania import Div, H1, P, Button
    return Div(
        H1("Welcome to My App"),
        P("Built with Xania"),
        Button("Get Started", href="/docs"),
        class_name="hero py-20"
    )


def create_home_page():
    """Factory function to create the home page."""
    def render(ctx: PageContext):
        return Div(
            HeroSection().render(),
            class_name="container"
        )
    
    return StaticPage(
        title="Home",
        html=render(PageContext())
    )
```

#### `pages/blog/post.py`
```python
"""Blog post page module."""
from xania import TemplatePage, PageContext, Div, H1, P, A


def create_blog_post_page(post_id: int):
    """Factory function to create a blog post page."""
    
    def render_post(ctx: PageContext):
        # In a real app, you'd fetch the post from a database
        return Div(
            A("← Back to blog", href="/blog", class_name="text-sm text-gray-600"),
            H1(f"Post {post_id}"),
            P(ctx.content),
            class_name="max-w-3xl"
        )
    
    return TemplatePage(
        title="Blog Post",
        render_fn=render_post
    )
```

#### `pages/__init__.py`
```python
"""Page registration registry.

This module imports all pages and provides a register_pages() function
that the main app can call to set up routes.
"""

from pages.home import create_home_page
from pages.about import create_about_page
from pages.blog.index import create_blog_index_page
from pages.blog.post import create_blog_post_page
from pages.contact import create_contact_page


def register_pages(app):
    """Register all pages with the SpaApp."""
    app.route("/", create_home_page())
    app.route("/about", create_about_page())
    app.route("/blog", create_blog_index_page())
    app.route("/blog/{id}", create_blog_post_page())  # Dynamic routes
    app.route("/contact", create_contact_page())
```

#### `app.py` (Clean and Minimal)
```python
"""Main application entry point."""
from xania import SpaApp
from xania.runtime.compiler import SpaCompiler
from pages import register_pages


def create_app():
    """Create and configure the SPA application."""
    app = SpaApp(
        name="My App",
        root_id="app",
        api_base="/api"
    )
    
    # Register all pages from the pages module
    register_pages(app)
    
    return app


if __name__ == "__main__":
    app = create_app()
    
    # For development server
    import uvicorn
    uvicorn.run("app:app", reload=True)
    
    # For static build
    compiler = SpaCompiler(title="My App")
    from pathlib import Path
    compiler.write(app, Path("dist"))
```

## Benefits

✅ **Scalability**: Add new pages without modifying `app.py`  
✅ **Organization**: Pages grouped by feature/section  
✅ **Testability**: Each page module can be tested independently  
✅ **Maintainability**: Clear separation of concerns  
✅ **Team-friendly**: Multiple developers can work on different page modules  

## Advanced Patterns

### 1. Page Metadata Registry
```python
# pages/__init__.py
PAGES = {
    "home": ("home", create_home_page, {"nav_label": "Home"}),
    "about": ("about", create_about_page, {"nav_label": "About"}),
    "blog": ("blog", create_blog_index_page, {"nav_label": "Blog"}),
}

def register_pages(app):
    for route_path, (key, factory, metadata) in PAGES.items():
        app.route(f"/{route_path}", factory())
```

### 2. Dynamic Route Generation
```python
# For routes with parameters like /blog/{id}
def register_dynamic_pages(app):
    for post_id in range(1, 101):  # 100 posts
        app.route(f"/blog/{post_id}", create_blog_post_page(post_id))
```

### 3. Shared Components
```python
# components/navbar.py
from xania import component

@component(props={"pages": list})
def NavBar(ctx):
    # Renders navbar with links to all pages
    pass

# pages/home.py
from components.navbar import NavBar

def create_home_page():
    return StaticPage(
        title="Home",
        html=NavBar(pages=PAGES).to_html()
    )
```

## Tips

1. **Use factory functions** (`create_*_page()`) to keep page creation consistent
2. **Group related pages** in subdirectories (`blog/`, `docs/`, etc.)
3. **Centralize page registration** in `pages/__init__.py`
4. **Document page structure** with docstrings
5. **Use components** for shared UI patterns across pages

## Migration Path

If you have an existing `app.py` with all routes:

1. Create a `pages/` directory
2. Move each route into a separate module
3. Create factories for each page
4. Update `pages/__init__.py` to register them
5. Replace your app.py with the clean version above

This keeps your app maintainable as it grows!
