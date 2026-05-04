"""
Xania Framework Tutorial Website
Demonstrates the framework's capabilities through an interactive SPA.
"""

from xania.runtime.spa import SpaApp, StaticPage, TemplatePage, JsExpr

# Create the tutorial app
tutorial_app = SpaApp(
    name="XaniaTutorial",
    root_id="app",
    api_base="/api",
)


def code_block(code: str, lang: str = "python") -> str:
    """Helper to format code blocks."""
    escaped = (
        code.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f'<pre class="bg-slate-800 p-4 rounded text-sm overflow-x-auto text-green-400"><code>{escaped}</code></pre>'


# ============================================================================
# HOME PAGE
# ============================================================================
home_html = """
<div class="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
  <!-- Header -->
  <div class="border-b border-slate-700 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
    <div class="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
      <div class="text-2xl font-black text-blue-400">⚡ Xania</div>
      <nav class="flex gap-6 text-sm">
        <a href="/" class="hover:text-blue-400 transition">Home</a>
        <a href="/quickstart" class="hover:text-blue-400 transition">Quick Start</a>
        <a href="/components" class="hover:text-blue-400 transition">Components</a>
        <a href="/spa" class="hover:text-blue-400 transition">SPA Mode</a>
        <a href="/examples" class="hover:text-blue-400 transition">Examples</a>
      </nav>
    </div>
  </div>

  <!-- Hero -->
  <div class="max-w-6xl mx-auto px-4 py-24 text-center">
    <h1 class="text-6xl font-black mb-4 bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
      Build UIs with Python
    </h1>
    <p class="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
      A minimal, production-oriented Python UI framework on FastAPI. Write components in Python, run SPAs client-side.
    </p>
    <div class="flex gap-4 justify-center">
      <a href="/quickstart" class="bg-blue-600 hover:bg-blue-500 px-8 py-3 rounded-lg font-semibold transition">
        Get Started →
      </a>
      <a href="/examples" class="bg-slate-700 hover:bg-slate-600 px-8 py-3 rounded-lg font-semibold transition">
        See Examples
      </a>
    </div>
  </div>

  <!-- Features -->
  <div class="max-w-6xl mx-auto px-4 py-16">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div class="bg-slate-800 border border-slate-700 p-6 rounded-lg hover:border-blue-500 transition">
        <div class="text-3xl mb-4">🐍</div>
        <h3 class="text-xl font-bold mb-2">Pure Python</h3>
        <p class="text-slate-400">Write UI components directly in Python with VDOM elements and hooks.</p>
      </div>
      <div class="bg-slate-800 border border-slate-700 p-6 rounded-lg hover:border-blue-500 transition">
        <div class="text-3xl mb-4">⚙️</div>
        <h3 class="text-xl font-bold mb-2">SPA Ready</h3>
        <p class="text-slate-400">Compile Python specs to JavaScript SPAs with client-side routing and state.</p>
      </div>
      <div class="bg-slate-800 border border-slate-700 p-6 rounded-lg hover:border-blue-500 transition">
        <div class="text-3xl mb-4">🚀</div>
        <h3 class="text-xl font-bold mb-2">Production-Ready</h3>
        <p class="text-slate-400">Built on FastAPI with built-in auth, rate limiting, and CSRF protection.</p>
      </div>
    </div>
  </div>

  <!-- Code Preview -->
  <div class="max-w-6xl mx-auto px-4 py-16">
    <h2 class="text-3xl font-bold mb-8">Simple Example</h2>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div>
        <h3 class="font-semibold text-blue-400 mb-4">Python Component</h3>
        <div class="bg-slate-800 border border-slate-700 p-4 rounded text-sm font-mono text-slate-200 overflow-x-auto">
          <div><span class="text-purple-400">class</span> Counter(Component):</div>
          <div class="ml-4"><span class="text-purple-400">def</span> initial_state(self):</div>
          <div class="ml-8"><span class="text-purple-400">return</span> {<span class="text-green-400">"count"</span>: <span class="text-orange-400">0</span>}</div>
          <div class="ml-4"><span class="text-purple-400">def</span> render(self, state):</div>
          <div class="ml-8"><span class="text-purple-400">return</span> Div(</div>
          <div class="ml-12">H1(<span class="text-green-400">"Counter"</span>),</div>
          <div class="ml-12">Span(str(state.count)),</div>
          <div class="ml-12">Button(<span class="text-green-400">"+"</span>),</div>
          <div class="ml-8">)</div>
        </div>
      </div>
      <div>
        <h3 class="font-semibold text-blue-400 mb-4">Compiles to SPA</h3>
        <div class="bg-slate-800 border border-slate-700 p-4 rounded text-sm font-mono text-slate-200 overflow-x-auto">
          <div><span class="text-orange-400">const</span> spa = XaniaSPA.createApp(...);</div>
          <div><span class="text-orange-400">spa</span>.route(<span class="text-green-400">"/"</span>, (ctx) =&gt; {</div>
          <div class="ml-4"><span class="text-orange-400">const</span> html = <span class="text-green-400">"&lt;h1&gt;Counter&lt;/h1&gt;..."</span>;</div>
          <div class="ml-4"><span class="text-orange-400">return</span> html;</div>
          <div>});</div>
          <div><span class="text-orange-400">spa</span>.start();</div>
        </div>
      </div>
    </div>
  </div>
</div>
"""

tutorial_app.route("/", StaticPage(title="Xania", html=home_html))


# ============================================================================
# QUICK START
# ============================================================================
quickstart_html = """
<div class="max-w-4xl">
  <h1 class="text-4xl font-bold mb-8">Quick Start</h1>

  <div class="space-y-12">
    <!-- Installation -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">1. Installation</h2>
      <p class="text-slate-300 mb-4">Clone the repository and install dependencies:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-green-400">
        <div>$ git clone https://github.com/xania/framework</div>
        <div>$ cd xania && python -m venv .venv</div>
        <div>$ source .venv/bin/activate</div>
        <div>$ pip install -e .</div>
      </div>
    </section>

    <!-- Requirements -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">2. Requirements</h2>
      <p class="text-slate-300 mb-4">Xania requires Python 3.14+</p>
      <ul class="list-disc list-inside space-y-2 text-slate-300">
        <li>FastAPI for server</li>
        <li>Uvicorn for ASGI</li>
        <li>Modern browser with ES6 support</li>
      </ul>
    </section>

    <!-- Running the Server -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">3. Run the Server</h2>
      <p class="text-slate-300 mb-4">Start the development server:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-green-400">
        <div>$ python app.py Xania --reload</div>
        <div class="text-slate-400">Starting Xania server on 127.0.0.1:8000</div>
      </div>
      <p class="text-slate-300 mt-4">Open <a href="http://127.0.0.1:8000" class="text-blue-400 hover:underline">http://127.0.0.1:8000</a></p>
    </section>

    <!-- Build for Production -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">4. Build Static Files</h2>
      <p class="text-slate-300 mb-4">Generate a static SPA:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-green-400">
        <div>$ python app.py Xania build --out ./dist</div>
      </div>
      <p class="text-slate-300 mt-4">Serve the generated HTML and static assets from any static host.</p>
    </section>

    <!-- Next Steps -->
    <section class="bg-slate-800 border border-slate-700 p-6 rounded-lg">
      <h3 class="font-bold text-lg mb-4">Next Steps</h3>
      <ul class="space-y-2 text-slate-300">
        <li>📖 Learn about <a href="/components" class="text-blue-400 hover:underline">Components</a></li>
        <li>🌐 Explore <a href="/spa" class="text-blue-400 hover:underline">SPA Mode</a></li>
        <li>💡 Check <a href="/examples" class="text-blue-400 hover:underline">Examples</a></li>
      </ul>
    </section>
  </div>
</div>
"""

tutorial_app.route("/quickstart", StaticPage(title="Quick Start", html=quickstart_html))


# ============================================================================
# COMPONENTS
# ============================================================================
components_html = """
<div class="max-w-4xl">
  <h1 class="text-4xl font-bold mb-8">Components</h1>

  <div class="space-y-12">
    <!-- Intro -->
    <section>
      <p class="text-slate-300 text-lg mb-6">
        Components are the building blocks of Xania UIs. Each component has state and a render method.
      </p>
    </section>

    <!-- Basic Component -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Basic Component</h2>
      <p class="text-slate-300 mb-4">Extend the <code class="bg-slate-800 px-2 py-1 rounded">Component</code> base class:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">from</span> xania.renderer.component <span class="text-purple-400">import</span> Component</div>
        <div><span class="text-purple-400">from</span> xania.renderer.elements <span class="text-purple-400">import</span> *</div>
        <div></div>
        <div><span class="text-purple-400">class</span> <span class="text-blue-400">MyComponent</span>(Component):</div>
        <div class="ml-4"><span class="text-purple-400">def</span> render(self, state):</div>
        <div class="ml-8"><span class="text-purple-400">return</span> Div(</div>
        <div class="ml-12">H1(<span class="text-green-400">"Hello"</span>),</div>
        <div class="ml-12">P(<span class="text-green-400">"Welcome to Xania"</span>)</div>
        <div class="ml-8">)</div>
      </div>
    </section>

    <!-- State Management -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">State Management</h2>
      <p class="text-slate-300 mb-4">Define initial state and event handlers:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">class</span> <span class="text-blue-400">Counter</span>(Component):</div>
        <div class="ml-4"><span class="text-purple-400">def</span> initial_state(self):</div>
        <div class="ml-8"><span class="text-purple-400">return</span> {<span class="text-green-400">"count"</span>: <span class="text-orange-400">0</span>}</div>
        <div></div>
        <div class="ml-4"><span class="text-purple-400">def</span> render(self, state):</div>
        <div class="ml-8"><span class="text-purple-400">return</span> Span(str(state.count))</div>
        <div></div>
        <div class="ml-4"><span class="text-purple-400">def</span> on_increment(self, state, payload):</div>
        <div class="ml-8">state.count += <span class="text-orange-400">1</span></div>
      </div>
    </section>

    <!-- Events -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Event Handling</h2>
      <p class="text-slate-300 mb-4">Wire up buttons to event handlers:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div>Button(</div>
        <div class="ml-4"><span class="text-green-400">"Click Me"</span>,</div>
        <div class="ml-4">onclick=<span class="text-green-400">"App.dispatch('Counter', 'increment')"</span></div>
        <div>)</div>
      </div>
      <p class="text-slate-300 mt-4">This calls the <code class="bg-slate-800 px-2 py-1 rounded">on_increment</code> method on your component.</p>
    </section>

    <!-- Available Elements -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Available Elements</h2>
      <div class="grid grid-cols-2 gap-4 text-slate-300">
        <div>• Div, Span, P</div>
        <div>• H1, H2, H3, H4, H5, H6</div>
        <div>• Button, Input, Textarea</div>
        <div>• Form, Label</div>
        <div>• Ul, Ol, Li</div>
        <div>• A, Img</div>
      </div>
    </section>
  </div>
</div>
"""

tutorial_app.route("/components", StaticPage(title="Components", html=components_html))


# ============================================================================
# SPA MODE
# ============================================================================
spa_html = """
<div class="max-w-4xl">
  <h1 class="text-4xl font-bold mb-8">SPA Mode</h1>

  <div class="space-y-12">
    <!-- What is SPA Mode -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">What is SPA Mode?</h2>
      <p class="text-slate-300 mb-4">
        SPA mode compiles your Python app into a standalone single-page application. 
        The frontend owns all routing and state — no round trips to the server.
      </p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded">
        <div class="flex items-center gap-4 text-sm">
          <div>🐍 Python Spec</div>
          <div>→</div>
          <div>📦 Compiler</div>
          <div>→</div>
          <div>📄 HTML + JS</div>
        </div>
      </div>
    </section>

    <!-- SpaApp -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">SpaApp Definition</h2>
      <p class="text-slate-300 mb-4">Define routes with Python pages:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">from</span> xania.runtime.spa <span class="text-purple-400">import</span> SpaApp, StaticPage</div>
        <div></div>
        <div>app = SpaApp(name=<span class="text-green-400">"MyApp"</span>)</div>
        <div></div>
        <div>app.route(</div>
        <div class="ml-4"><span class="text-green-400">"/"</span>,</div>
        <div class="ml-4">StaticPage(title=<span class="text-green-400">"Home"</span>, html=<span class="text-green-400">"&lt;h1&gt;Welcome&lt;/h1&gt;"</span>)</div>
        <div>)</div>
      </div>
    </section>

    <!-- Compilation -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Compiling to Static Files</h2>
      <p class="text-slate-300 mb-4">Use <code class="bg-slate-800 px-2 py-1 rounded">SpaCompiler</code> to generate files:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">from</span> xania.runtime.compiler <span class="text-purple-400">import</span> SpaCompiler</div>
        <div></div>
        <div>compiler = SpaCompiler(title=<span class="text-green-400">"My App"</span>)</div>
        <div>compiler.write(app, <span class="text-orange-400">Path</span>(<span class="text-green-400">"./dist"</span>))</div>
      </div>
      <p class="text-slate-300 mt-4">Generates:</p>
      <ul class="list-disc list-inside text-slate-300 mt-2 space-y-1">
        <li><code class="bg-slate-800 px-2 py-1 rounded">index.html</code> – HTML shell</li>
        <li><code class="bg-slate-800 px-2 py-1 rounded">static/spa_runtime.js</code> – Runtime</li>
        <li><code class="bg-slate-800 px-2 py-1 rounded">static/app.js</code> – Generated routes</li>
      </ul>
    </section>

    <!-- Page Types -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Page Types</h2>
      
      <h3 class="font-semibold text-blue-300 mb-3 mt-4">StaticPage – Fixed HTML</h3>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto mb-4">
        <div>StaticPage(title=<span class="text-green-400">"About"</span>, html=<span class="text-green-400">"&lt;h1&gt;About Us&lt;/h1&gt;..."</span>)</div>
      </div>

      <h3 class="font-semibold text-blue-300 mb-3">TemplatePage – With Placeholders</h3>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div>TemplatePage(</div>
        <div class="ml-4">title=<span class="text-green-400">"Post"</span>,</div>
        <div class="ml-4">template=<span class="text-green-400">"&lt;h1&gt;{title}&lt;/h1&gt;&lt;p&gt;{content}&lt;/p&gt;"</span>,</div>
        <div class="ml-4">placeholders={</div>
        <div class="ml-8"><span class="text-green-400">"title"</span>: <span class="text-green-400">"Hello"</span>,</div>
        <div class="ml-8"><span class="text-green-400">"content"</span>: <span class="text-green-400">"World"</span></div>
        <div class="ml-4">}</div>
        <div>)</div>
      </div>
    </section>
  </div>
</div>
"""

tutorial_app.route("/spa", StaticPage(title="SPA Mode", html=spa_html))


# ============================================================================
# EXAMPLES
# ============================================================================
examples_html = """
<div class="max-w-4xl">
  <h1 class="text-4xl font-bold mb-8">Examples</h1>

  <div class="space-y-12">
    <!-- Counter -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Counter Component</h2>
      <p class="text-slate-300 mb-4">A simple interactive counter demonstrating state and events:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">class</span> <span class="text-blue-400">Counter</span>(Component):</div>
        <div class="ml-4"><span class="text-purple-400">def</span> initial_state(self):</div>
        <div class="ml-8"><span class="text-purple-400">return</span> {<span class="text-green-400">"count"</span>: <span class="text-orange-400">0</span>}</div>
        <div></div>
        <div class="ml-4"><span class="text-purple-400">def</span> render(self, state):</div>
        <div class="ml-8">count = <span class="text-blue-400">int</span>(state.count)</div>
        <div class="ml-8"><span class="text-purple-400">return</span> Div(</div>
        <div class="ml-12">Span(str(count)),</div>
        <div class="ml-12">Button(<span class="text-green-400">"+"</span>, onclick=<span class="text-green-400">"App.dispatch('Counter', 'increment')"</span>),</div>
        <div class="ml-8">)</div>
        <div></div>
        <div class="ml-4"><span class="text-purple-400">def</span> on_increment(self, state, payload):</div>
        <div class="ml-8">state.count += <span class="text-orange-400">1</span></div>
      </div>
    </section>

    <!-- Todo List -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Todo List</h2>
      <p class="text-slate-300 mb-4">Track multiple items with add/remove:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">class</span> <span class="text-blue-400">TodoList</span>(Component):</div>
        <div class="ml-4"><span class="text-purple-400">def</span> initial_state(self):</div>
        <div class="ml-8"><span class="text-purple-400">return</span> {<span class="text-green-400">"todos"</span>: [], <span class="text-green-400">"next_id"</span>: <span class="text-orange-400">0</span>}</div>
        <div></div>
        <div class="ml-4"><span class="text-purple-400">def</span> on_add_todo(self, state, payload):</div>
        <div class="ml-8">state.todos.append({<span class="text-green-400">"id"</span>: state.next_id, <span class="text-green-400">"text"</span>: payload.get(<span class="text-green-400">"text"</span>)})</div>
        <div class="ml-8">state.next_id += <span class="text-orange-400">1</span></div>
      </div>
    </section>

    <!-- Form Handling -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Form Handling</h2>
      <p class="text-slate-300 mb-4">Capture form input and submit data:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div>Form(</div>
        <div class="ml-4">Input(type=<span class="text-green-400">"text"</span>, name=<span class="text-green-400">"username"</span>, placeholder=<span class="text-green-400">"Name"</span>),</div>
        <div class="ml-4">Button(<span class="text-green-400">"Submit"</span>, type=<span class="text-green-400">"submit"</span>, onclick=<span class="text-green-400">"App.dispatch('Form', 'submit')"</span>)</div>
        <div>)</div>
      </div>
    </section>

    <!-- Conditional Rendering -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">Conditional Rendering</h2>
      <p class="text-slate-300 mb-4">Show/hide elements based on state:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">def</span> render(self, state):</div>
        <div class="ml-4">children = []</div>
        <div class="ml-4"><span class="text-purple-400">if</span> state.loading:</div>
        <div class="ml-8">children.append(P(<span class="text-green-400">"Loading..."</span>))</div>
        <div class="ml-4"><span class="text-purple-400">else</span>:</div>
        <div class="ml-8">children.append(P(state.data))</div>
        <div class="ml-4"><span class="text-purple-400">return</span> Div(*children)</div>
      </div>
    </section>

    <!-- List Rendering -->
    <section>
      <h2 class="text-2xl font-bold mb-4 text-blue-400">List Rendering</h2>
      <p class="text-slate-300 mb-4">Render dynamic lists from state:</p>
      <div class="bg-slate-800 border border-slate-700 p-4 rounded font-mono text-sm text-slate-200 overflow-x-auto">
        <div><span class="text-purple-400">def</span> render(self, state):</div>
        <div class="ml-4">items = [Li(item, key=i) <span class="text-purple-400">for</span> i, item <span class="text-purple-400">in</span> <span class="text-blue-400">enumerate</span>(state.items)]</div>
        <div class="ml-4"><span class="text-purple-400">return</span> Ul(*items)</div>
      </div>
    </section>
  </div>
</div>
"""

tutorial_app.route("/examples", StaticPage(title="Examples", html=examples_html))


if __name__ == "__main__":
    from pathlib import Path
    from xania.runtime.compiler import SpaCompiler

    compiler = SpaCompiler(title="Xania Tutorial", tailwind=True)
    compiler.write(tutorial_app, Path(__file__).parent)
    print("✅ Tutorial website generated!")
