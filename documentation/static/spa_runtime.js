// xania/static/spa_runtime.js
//
// Minimal SPA runtime:
// - client-owned state + render
// - client-side router (History API)
// - backend used only for APIs (no HTML patch endpoint required)
//
// This intentionally stays tiny and framework-agnostic.

(function () {
  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function isModifiedClick(evt) {
    return !!(evt.metaKey || evt.ctrlKey || evt.shiftKey || evt.altKey);
  }

  function splitPath(path) {
    return String(path || "/")
      .split("?")[0]
      .split("#")[0]
      .split("/")
      .filter(Boolean);
  }

  function joinPath(base, path) {
    if (!base.endsWith("/")) base += "/";
    return base + path.replace(/^\//, "");
  }

  function createApp(options) {
    const rootId = (options && options.rootId) || "app";
    const apiBase = (options && options.apiBase) || "/api";
    const scrollRestoration = (options && options.scrollRestoration) || "auto"; // "auto" | "top" | "none"

    const components = Object.create(null);
    const routes = [];
    const stateByKey = new Map();
    const listeners = new Set();
    let renderScheduled = false;
    let lastNavKey = null;

    function getRoot() {
      const el = document.getElementById(rootId);
      if (!el) throw new Error("Root element not found: #" + rootId);
      return el;
    }

    function subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    }

    function notify(evt) {
      for (const fn of listeners) fn(evt);
    }

    function register(name, component) {
      if (!name) throw new Error("Component name required");
      if (!component || typeof component.view !== "function") {
        throw new Error("Component must implement view(ctx)");
      }
      components[name] = component;
    }

    function compileRoute(path) {
      const segments = splitPath(path);
      return { path, segments };
    }

    function route(path, handler) {
      routes.push({ ...compileRoute(path), handler });
    }

    function matchRoute(pathname) {
      const incoming = splitPath(pathname);

      for (const r of routes) {
        const params = Object.create(null);
        if (r.segments.length !== incoming.length) continue;

        let ok = true;
        for (let i = 0; i < r.segments.length; i++) {
          const seg = r.segments[i];
          const val = incoming[i];
          if (seg.startsWith(":")) {
            params[seg.slice(1)] = val;
            continue;
          }
          if (seg !== val) {
            ok = false;
            break;
          }
        }
        if (ok) return { route: r, params };
      }

      return null;
    }

    function withTransition(fn) {
      try {
        if (document && typeof document.startViewTransition === "function") {
          // View Transitions API (Chrome/Edge/Safari TP).
          document.startViewTransition(() => fn());
          return;
        }
      } catch (_) {
        // fall back below
      }

      // Fallback: tiny opacity fade on the root container.
      const root = getRoot();
      root.style.opacity = "0";
      root.style.transition = "opacity 120ms ease";
      window.requestAnimationFrame(() => {
        fn();
        window.requestAnimationFrame(() => {
          root.style.opacity = "1";
        });
      });
    }

    function navigate(href, navOptions) {
      const opts = navOptions || {};
      const to = new URL(String(href || "/"), window.location.href);

      // Ignore cross-origin navigations.
      if (to.origin !== window.location.origin) {
        window.location.href = to.href;
        return;
      }

      const key = to.pathname + to.search + to.hash;
      if (key === lastNavKey) return;
      lastNavKey = key;

      const doNav = () => {
        if (opts.replace) window.history.replaceState(opts.state || {}, "", key);
        else window.history.pushState(opts.state || {}, "", key);
        scheduleRender({ source: "navigate" });
        if (scrollRestoration === "top" || opts.scroll === "top") window.scrollTo(0, 0);
      };

      if (opts.transition) withTransition(doNav);
      else doNav();
    }

    function linkInterceptor(evt) {
      if (!evt || evt.defaultPrevented) return;
      if (evt.button !== 0) return; // only left-click
      if (isModifiedClick(evt)) return;
      const a = evt.target && evt.target.closest ? evt.target.closest("a") : null;
      if (!a) return;
      const href = a.getAttribute("href");
      if (!href) return;
      if (href.startsWith("http://") || href.startsWith("https://")) return;
      if (href.startsWith("mailto:") || href.startsWith("tel:")) return;
      if (href.startsWith("#")) return;
      if (a.hasAttribute("download")) return;
      if (a.getAttribute("target")) return;
      evt.preventDefault();
      navigate(href, { transition: true });
    }

    function ensureState(key, initFn) {
      if (!stateByKey.has(key)) {
        stateByKey.set(key, typeof initFn === "function" ? initFn() : {});
      }
      return stateByKey.get(key);
    }

    function scheduleRender(meta) {
      if (renderScheduled) return;
      renderScheduled = true;
      const m = meta || {};
      window.requestAnimationFrame(() => {
        renderScheduled = false;
        render(m);
      });
    }

    function render(meta) {
      const root = getRoot();
      const url = new URL(window.location.href);
      const pathname = url.pathname || "/";
      const matched = matchRoute(pathname);

      let html = "";
      const t0 = typeof performance !== "undefined" ? performance.now() : Date.now();

      try {
        if (!matched) {
          html =
            '<div class="min-h-screen bg-gray-950 text-white flex items-center justify-center">' +
            '<div class="text-center">' +
            '<div class="text-3xl font-black mb-2">404</div>' +
            '<div class="text-white/70 mb-6">Route not found: ' +
            escapeHtml(pathname) +
            "</div>" +
            '<a href="/" class="underline">Go home</a>' +
            "</div></div>";
        } else {
          const query = Object.create(null);
          for (const [k, v] of url.searchParams.entries()) query[k] = v;
          html = matched.route.handler({
            pathname,
            navigate,
            components,
            ensureState,
            api,
            params: matched.params,
            query,
          });
        }
      } catch (err) {
        const msg = err && err.message ? String(err.message) : String(err);
        html =
          '<div class="min-h-screen bg-gray-950 text-white flex items-center justify-center p-6">' +
          '<div class="max-w-2xl w-full">' +
          '<div class="text-3xl font-black mb-3">Render error</div>' +
          '<div class="text-white/70 mb-6">An exception occurred while rendering <code class="text-white/90">' +
          escapeHtml(pathname) +
          "</code>.</div>" +
          '<pre class="bg-black/40 rounded-xl p-4 overflow-auto text-sm text-red-200 border border-white/10">' +
          escapeHtml(msg) +
          "</pre>" +
          '<div class="mt-6"><a href="/" class="underline">Go home</a></div>' +
          "</div></div>";
      }

      root.innerHTML = html || "";

      const t1 = typeof performance !== "undefined" ? performance.now() : Date.now();
      notify({
        type: "render",
        pathname,
        durationMs: Math.max(0, t1 - t0),
        source: meta && meta.source ? meta.source : "unknown",
      });
    }

    async function api(path, options) {
      const url = joinPath(apiBase, path);
      const res = await fetch(url, options || {});
      if (!res.ok) {
        const txt = await res.text().catch(() => "");
        throw new Error("HTTP " + res.status + " " + txt);
      }
      const ct = (res.headers.get("content-type") || "").toLowerCase();
      if (ct.includes("application/json")) return await res.json();
      return await res.text();
    }

    function start() {
      document.addEventListener("click", linkInterceptor);
      window.addEventListener("popstate", () => scheduleRender({ source: "popstate" }));
      scheduleRender({ source: "start" });
    }

    return { register, route, start, render, navigate, api, subscribe, scheduleRender, withTransition };
  }

  window.XaniaSPA = { createApp };
})();
