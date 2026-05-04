// xania/static/app.js
//
// Multi-page stress-demo app for Xania's tiny SPA runtime.

(function () {
  const spa = window.XaniaSPA.createApp({ rootId: "app", apiBase: "/api" });

  let appState = null;
  let lastPathname = null;
  let rootEventsBound = false;

  function esc(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function initAppState() {
    return {
      debug: { renders: 0, lastRenderMs: 0, pathname: "/" },
      auth: { user: null, csrf: null, loading: false, error: null, checked: false },
      dashboard: { loading: false, error: null, metrics: null, poll: false, pollMs: 2000, pollTimer: null },
      users: {
        q: "",
        page: 1,
        pageSize: 50,
        loading: false,
        error: null,
        total: 0,
        items: [],
        lastKey: "",
        searchTimer: null,
      },
      userDetail: { cache: Object.create(null), loading: false, error: null },
      forms: { sending: false, response: null, error: null },
      settings: { density: "comfortable", notifications: true, bio: "" },
      bench: { rows: 1000, cols: 6, intervalMs: 250, running: false, tick: 0, timer: null },
      private: { loading: false, error: null, count: 0, sample: null, wrote: null, writing: false },
    };
  }

  function clampInt(v, lo, hi) {
    const n = (v | 0) || 0;
    return Math.max(lo, Math.min(hi, n));
  }

  function pill(label, tone) {
    const cls =
      tone === "green"
        ? "bg-green-500/15 text-green-200 border-green-500/30"
        : tone === "yellow"
          ? "bg-yellow-500/15 text-yellow-200 border-yellow-500/30"
          : tone === "red"
            ? "bg-red-500/15 text-red-200 border-red-500/30"
            : "bg-white/10 text-white/80 border-white/10";
    return '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs border ' + cls + '">' + esc(label) + "</span>";
  }

  function sidebarLink(path, label, currentPath) {
    const active = currentPath === path || currentPath.startsWith(path + "/");
    const cls = active
      ? "bg-white/10 text-white"
      : "text-white/70 hover:text-white hover:bg-white/5";
    return (
      '<a href="' +
      esc(path) +
      '" class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-semibold ' +
      cls +
      '">' +
      esc(label) +
      "</a>"
    );
  }

  function layout(currentPath, title, content) {
    const debug = appState ? appState.debug : { renders: 0, lastRenderMs: 0, pathname: currentPath };
    const renderMs = typeof debug.lastRenderMs === "number" ? debug.lastRenderMs.toFixed(1) : "0.0";
    const auth = appState ? appState.auth : { user: null, csrf: null, loading: false, error: null, checked: false };
    const authChip =
      auth && auth.user
        ? '<div class="flex items-center gap-2"><span class="text-white/50 text-xs">signed in</span><span class="text-xs font-semibold">' +
          esc(auth.user.username || "user") +
          '</span><button data-action="auth.logout" class="ml-2 px-2 py-1 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-xs font-semibold">Logout</button></div>'
        : '<a href="/login" class="px-2 py-1 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-xs font-semibold">Login</a>';

    return [
      '<div class="min-h-screen bg-gray-950 text-white">',
      '  <div class="flex">',
      '    <aside class="hidden md:block w-64 border-r border-white/10 min-h-screen p-4">',
      '      <div class="text-lg font-black tracking-tight mb-4">Xania</div>',
      '      <nav class="space-y-1">',
      sidebarLink("/", "Home", currentPath),
      sidebarLink("/dashboard", "Dashboard", currentPath),
      sidebarLink("/users", "Users", currentPath),
      sidebarLink("/forms", "Forms", currentPath),
      sidebarLink("/private", "Private", currentPath),
      sidebarLink("/bench", "Bench", currentPath),
      sidebarLink("/about", "About", currentPath),
      "      </nav>",
      '      <div class="mt-6 text-xs text-white/50">',
      "        Stress-demo: big lists, polling, timers, and dynamic routes.",
      "      </div>",
      "    </aside>",
      '    <main class="flex-1">',
      '      <header class="sticky top-0 z-10 bg-gray-950/80 backdrop-blur border-b border-white/10">',
      '        <div class="px-4 md:px-8 py-4 flex items-center justify-between gap-4">',
      '          <div class="min-w-0">',
      '            <div class="text-xs text-white/50">Multipage stress demo</div>',
      '            <div class="text-xl md:text-2xl font-black truncate">' + esc(title) + "</div>",
      "          </div>",
      '          <div class="text-xs text-white/60 text-right">',
      '            <div class="mb-1">' + authChip + "</div>",
      '            <div><span class="text-white/40">route</span> ' + esc(currentPath) + "</div>",
      '            <div><span class="text-white/40">render</span> ' + esc(renderMs) + "ms · " + esc(String(debug.renders)) + "</div>",
      "          </div>",
      "        </div>",
      "      </header>",
      '      <div class="px-4 md:px-8 py-6">',
      content,
      "      </div>",
      "    </main>",
      "  </div>",
      "</div>",
    ].join("\n");
  }

  async function loadMetrics() {
    if (!appState || appState.dashboard.loading) return;
    appState.dashboard.loading = true;
    appState.dashboard.error = null;
    spa.render();
    try {
      appState.dashboard.metrics = await spa.api("metrics");
    } catch (e) {
      appState.dashboard.error = e && e.message ? String(e.message) : String(e);
    } finally {
      appState.dashboard.loading = false;
      spa.render();
    }
  }

  async function ensureAuthChecked() {
    if (!appState || appState.auth.checked || appState.auth.loading) return;
    appState.auth.loading = true;
    appState.auth.error = null;
    spa.render();
    try {
      const res = await spa.api("auth/me");
      if (res && res.ok) {
        appState.auth.user = res.user || null;
        appState.auth.csrf = res.csrf || null;
      } else {
        appState.auth.user = null;
        appState.auth.csrf = null;
      }
    } catch (_) {
      appState.auth.user = null;
      appState.auth.csrf = null;
    } finally {
      appState.auth.loading = false;
      appState.auth.checked = true;
      spa.render();
    }
  }

  async function doLogout() {
    if (!appState || appState.auth.loading) return;
    appState.auth.loading = true;
    appState.auth.error = null;
    spa.render();
    try {
      await spa.api("auth/logout", { method: "POST" });
    } catch (_) {
      // ignore
    } finally {
      appState.auth.user = null;
      appState.auth.csrf = null;
      appState.auth.loading = false;
      appState.auth.checked = true;
      spa.navigate("/", { transition: true, scroll: "top" });
    }
  }

  async function loadPrivateBig() {
    if (!appState || appState.private.loading) return;
    appState.private.loading = true;
    appState.private.error = null;
    spa.render();
    try {
      const res = await spa.api("private/big-json");
      appState.private.count = res.count || 0;
      appState.private.sample = res.items && res.items.length ? res.items[0] : null;
    } catch (e) {
      appState.private.error = e && e.message ? String(e.message) : String(e);
    } finally {
      appState.private.loading = false;
      spa.render();
    }
  }

  function startMetricsPoll() {
    if (!appState) return;
    stopMetricsPoll();
    const ms = clampInt(appState.dashboard.pollMs, 250, 10000);
    appState.dashboard.pollTimer = setInterval(() => {
      loadMetrics();
    }, ms);
  }

  function stopMetricsPoll() {
    if (!appState) return;
    if (appState.dashboard.pollTimer) clearInterval(appState.dashboard.pollTimer);
    appState.dashboard.pollTimer = null;
  }

  function usersKey() {
    const q = (appState.users.q || "").trim();
    return q + "|" + appState.users.page + "|" + appState.users.pageSize;
  }

  async function loadUsers() {
    if (!appState || appState.users.loading) return;
    const key = usersKey();
    appState.users.loading = true;
    appState.users.error = null;
    spa.render();
    try {
      const q = (appState.users.q || "").trim();
      const params = new URLSearchParams({
        page: String(appState.users.page),
        page_size: String(appState.users.pageSize),
      });
      if (q) params.set("q", q);
      const res = await spa.api("users?" + params.toString());
      appState.users.items = res.items || [];
      appState.users.total = res.total || 0;
      appState.users.lastKey = key;
    } catch (e) {
      appState.users.error = e && e.message ? String(e.message) : String(e);
    } finally {
      appState.users.loading = false;
      spa.render();
    }
  }

  function ensureUsersLoaded() {
    if (!appState) return;
    const key = usersKey();
    if (key !== appState.users.lastKey && !appState.users.loading) loadUsers();
  }

  async function ensureUserLoaded(id) {
    if (!appState) return;
    const key = String(id);
    if (appState.userDetail.cache[key]) return;
    if (appState.userDetail.loading) return;
    appState.userDetail.loading = true;
    appState.userDetail.error = null;
    spa.render();
    try {
      appState.userDetail.cache[key] = await spa.api("users/" + encodeURIComponent(key));
    } catch (e) {
      appState.userDetail.error = e && e.message ? String(e.message) : String(e);
    } finally {
      appState.userDetail.loading = false;
      spa.render();
    }
  }

  function stopBench() {
    if (!appState) return;
    if (appState.bench.timer) clearInterval(appState.bench.timer);
    appState.bench.timer = null;
    appState.bench.running = false;
  }

  function startBench() {
    if (!appState) return;
    stopBench();
    const ms = clampInt(appState.bench.intervalMs, 16, 2000);
    appState.bench.running = true;
    appState.bench.timer = setInterval(() => {
      appState.bench.tick++;
      spa.render();
    }, ms);
  }

  function bindRootEvents() {
    if (rootEventsBound) return;
    rootEventsBound = true;

    const root = document.getElementById("app");
    if (!root) return;

    root.addEventListener("click", (evt) => {
      const el = evt.target && evt.target.closest ? evt.target.closest("[data-action]") : null;
      if (!el) return;
      const name = el.dataset.action || "";

      if (name === "dashboard.refresh") return loadMetrics();
      if (name === "dashboard.togglePoll") {
        appState.dashboard.poll = !appState.dashboard.poll;
        if (appState.dashboard.poll) startMetricsPoll();
        else stopMetricsPoll();
        return spa.render();
      }

      if (name === "users.prev") {
        appState.users.page = Math.max(1, (appState.users.page | 0) - 1);
        appState.users.lastKey = "";
        return spa.render();
      }
      if (name === "users.next") {
        const maxPage = Math.max(1, Math.ceil((appState.users.total || 0) / appState.users.pageSize));
        appState.users.page = Math.min(maxPage, (appState.users.page | 0) + 1);
        appState.users.lastKey = "";
        return spa.render();
      }
      if (name === "users.clear") {
        appState.users.q = "";
        appState.users.page = 1;
        appState.users.lastKey = "";
        return spa.render();
      }

      if (name === "bench.toggle") {
        if (appState.bench.running) stopBench();
        else startBench();
        return spa.render();
      }
      if (name === "bench.bump") {
        appState.bench.tick++;
        return spa.render();
      }

      if (name === "auth.logout") return doLogout();

      if (name === "private.load") return loadPrivateBig();

      if (name === "private.write") {
        if (!appState.auth.csrf || appState.private.writing) return;
        appState.private.writing = true;
        appState.private.wrote = null;
        appState.private.error = null;
        spa.render();
        spa
          .api("private/write-echo", {
            method: "POST",
            headers: {
              "content-type": "application/json",
              "X-CSRF-Token": appState.auth.csrf,
            },
            body: JSON.stringify({ ts: Date.now(), note: "stress-write" }),
          })
          .then((res) => {
            appState.private.wrote = res;
          })
          .catch((e) => {
            appState.private.error = e && e.message ? String(e.message) : String(e);
          })
          .finally(() => {
            appState.private.writing = false;
            spa.render();
          });
      }
    });

    function handleBind(el) {
      const path = el.dataset.bind;
      if (!path || !appState) return;

      const parts = path.split(".");
      let cur = appState;
      for (let i = 0; i < parts.length - 1; i++) {
        const k = parts[i];
        if (!cur[k]) cur[k] = {};
        cur = cur[k];
      }
      const key = parts[parts.length - 1];

      let value = el.type === "checkbox" ? !!el.checked : el.value;
      const t = el.dataset.bindType || "";
      if (t === "int") value = clampInt(parseInt(value, 10), 0, 10_000_000);
      if (t === "bool") value = !!value;
      cur[key] = value;

      if (path === "users.q") {
        appState.users.page = 1;
        appState.users.lastKey = "";
        if (appState.users.searchTimer) clearTimeout(appState.users.searchTimer);
        appState.users.searchTimer = setTimeout(() => {
          loadUsers();
        }, 250);
        return;
      }

      if (path === "users.pageSize") {
        appState.users.pageSize = clampInt(parseInt(appState.users.pageSize, 10), 10, 1000);
        appState.users.page = 1;
        appState.users.lastKey = "";
        return spa.render();
      }

      if (path === "bench.rows" || path === "bench.cols" || path === "bench.intervalMs") {
        appState.bench.rows = clampInt(parseInt(appState.bench.rows, 10), 100, 20000);
        appState.bench.cols = clampInt(parseInt(appState.bench.cols, 10), 2, 20);
        appState.bench.intervalMs = clampInt(parseInt(appState.bench.intervalMs, 10), 16, 2000);
        if (appState.bench.running) startBench();
        return spa.render();
      }

      if (el.dataset.autorender === "0") return;
      spa.render();
    }

    root.addEventListener("input", (evt) => {
      const el = evt.target;
      if (!el || !el.dataset) return;
      if (!el.dataset.bind) return;
      handleBind(el);
    });

    root.addEventListener("change", (evt) => {
      const el = evt.target;
      if (!el || !el.dataset) return;
      if (!el.dataset.bind) return;
      handleBind(el);
    });

    root.addEventListener("submit", async (evt) => {
      const form = evt.target;
      if (!form || !form.dataset) return;
      if (form.dataset.action !== "forms.submit" && form.dataset.action !== "auth.login") return;
      evt.preventDefault();
      if (!appState) return;

      if (form.dataset.action === "auth.login") {
        if (appState.auth.loading) return;
        appState.auth.loading = true;
        appState.auth.error = null;
        spa.render();
        try {
          const fd = new FormData(form);
          const username = String(fd.get("username") || "").trim();
          const password = String(fd.get("password") || "");
          const res = await spa.api("auth/login", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ username, password }),
          });
          appState.auth.user = res.user || null;
          appState.auth.csrf = res.csrf || null;
          appState.auth.checked = true;
          spa.navigate("/private", { transition: true, scroll: "top" });
          return;
        } catch (e) {
          appState.auth.error = e && e.message ? String(e.message) : String(e);
        } finally {
          appState.auth.loading = false;
          spa.render();
        }
        return;
      }

      if (appState.forms.sending) return;

      appState.forms.sending = true;
      appState.forms.error = null;
      appState.forms.response = null;
      spa.render();

      try {
        const fd = new FormData(form);
        const payload = Object.create(null);
        for (const [k, v] of fd.entries()) payload[k] = String(v);

        const res = await spa.api("echo", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify(payload),
        });
        appState.forms.response = res;
      } catch (e) {
        appState.forms.error = e && e.message ? String(e.message) : String(e);
      } finally {
        appState.forms.sending = false;
        spa.render();
      }
    });
  }

  spa.subscribe((info) => {
    if (!info || info.type !== "render") return;
    if (!appState) return;

    appState.debug.renders++;
    appState.debug.pathname = info.pathname || "/";
    appState.debug.lastRenderMs = typeof info.durationMs === "number" ? info.durationMs : 0;

    if (lastPathname && lastPathname !== info.pathname) {
      if (lastPathname.startsWith("/bench") && !String(info.pathname).startsWith("/bench")) stopBench();
      if (lastPathname.startsWith("/dashboard") && !String(info.pathname).startsWith("/dashboard")) stopMetricsPoll();
    }
    lastPathname = info.pathname;

    if (!rootEventsBound) bindRootEvents();
  });

  // Routes
  spa.route("/", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    const cards = [
      { href: "/dashboard", title: "Dashboard", desc: "Polling metrics + charts + cards." },
      { href: "/users", title: "Users", desc: "Large, paginated table (API-backed)." },
      { href: "/forms", title: "Forms", desc: "Client state + POST to /api/echo." },
      { href: "/private", title: "Private", desc: "Cookie auth + CSRF + huge JSON payload." },
      { href: "/bench", title: "Bench", desc: "Big DOM render + timer-driven rerenders." },
    ]
      .map((c) => {
        return (
          '<a href="' +
          esc(c.href) +
          '" class="block rounded-2xl border border-white/10 bg-white/5 hover:bg-white/10 p-5 transition">' +
          '<div class="text-lg font-black mb-1">' +
          esc(c.title) +
          "</div>" +
          '<div class="text-sm text-white/70">' +
          esc(c.desc) +
          "</div>" +
          "</a>"
        );
      })
      .join("\n");

    const content = [
      '<div class="max-w-5xl">',
      '  <div class="rounded-3xl border border-white/10 bg-gradient-to-br from-white/10 to-transparent p-8">',
      '    <div class="text-sm text-white/60 mb-2">Xania SPA runtime</div>',
      '    <h1 class="text-3xl md:text-4xl font-black tracking-tight mb-3">Multipage stress-demo site</h1>',
      '    <p class="text-white/70 max-w-2xl">Navigate between pages, fetch large lists, toggle polling, submit forms, and run a timer-driven DOM benchmark. This is designed to put load on routing, state, and repeated full renders.</p>',
      '    <div class="mt-6 flex flex-wrap gap-3">',
      '      <a href="/about" class="px-4 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">About</a>',
      '      <a href="/users/42" class="px-4 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">User detail (dynamic route)</a>',
      "    </div>",
      "  </div>",
      '  <div class="grid md:grid-cols-2 gap-4 mt-6">',
      cards,
      "  </div>",
      "</div>",
    ].join("\n");
    return layout(ctx.pathname, "Home", content);
  });

  spa.route("/login", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();

    if (appState.auth.user) {
      return layout(
        ctx.pathname,
        "Login",
        [
          '<div class="max-w-xl">',
          '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
          '    <div class="text-sm text-white/70 mb-3">Already signed in as <span class="text-white font-semibold">' +
            esc(appState.auth.user.username) +
            "</span>.</div>",
          '    <a href="/private" class="underline">Go to private stress page</a>',
          "  </div>",
          "</div>",
        ].join("\n")
      );
    }

    const err = appState.auth.error
      ? '<div class="rounded-xl border border-red-500/30 bg-red-500/10 text-red-200 px-4 py-3 text-sm mb-4">' +
        esc(appState.auth.error) +
        "</div>"
      : "";

    const content = [
      '<div class="max-w-xl">',
      '  <div class="rounded-3xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-sm text-white/60 mb-2">Demo auth</div>',
      '    <div class="text-2xl font-black mb-4">Sign in</div>',
      err,
      '    <form data-action="auth.login" class="space-y-3">',
      '      <label class="block text-xs text-white/60">Username<input name="username" autocomplete="username" class="mt-1 w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm" placeholder="admin" /></label>',
      '      <label class="block text-xs text-white/60">Password<input type="password" name="password" autocomplete="current-password" class="mt-1 w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm" placeholder="admin" /></label>',
      '      <button class="w-full px-4 py-2.5 rounded-xl border border-white/10 bg-white/10 hover:bg-white/15 text-sm font-semibold">' +
        (appState.auth.loading ? "Signing in…" : "Sign in") +
        "</button>",
      '      <div class="text-xs text-white/50">Demo credentials: <code class="text-white/80">admin / admin</code></div>',
      "    </form>",
      "  </div>",
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "Login", content);
  });

  spa.route("/private", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();

    if (!appState.auth.user) {
      const content = [
        '<div class="max-w-xl">',
        '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
        '    <div class="text-lg font-black mb-2">Private</div>',
        '    <div class="text-sm text-white/70 mb-4">This page calls protected APIs. Please sign in first.</div>',
        '    <a href="/login" class="underline">Go to login</a>',
        "  </div>",
        "</div>",
      ].join("\n");
      return layout(ctx.pathname, "Private", content);
    }

    const err = appState.private.error
      ? '<div class="rounded-xl border border-red-500/30 bg-red-500/10 text-red-200 px-4 py-3 text-sm mb-4">' +
        esc(appState.private.error) +
        "</div>"
      : "";

    const content = [
      '<div class="max-w-5xl space-y-4">',
      '  <div class="rounded-3xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-sm text-white/60 mb-1">Protected stress endpoints</div>',
      '    <div class="text-2xl font-black mb-2">Auth + CSRF + huge JSON</div>',
      '    <div class="text-sm text-white/70">Read endpoint returns 50k items. Write endpoint requires <code class="text-white/80">X-CSRF-Token</code> matching the session.</div>',
      "  </div>",
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
      err,
      '    <div class="flex flex-wrap gap-2 items-center">',
      '      <button data-action="private.load" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">' +
        (appState.private.loading ? "Loading…" : "Load 50k JSON") +
        "</button>",
      '      <button data-action="private.write" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">' +
        (appState.private.writing ? "Writing…" : "POST write (CSRF)") +
        "</button>",
      "    </div>",
      '    <div class="mt-4 grid md:grid-cols-2 gap-4">',
      '      <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
      '        <div class="text-xs text-white/50 mb-2">big-json</div>',
      '        <div class="text-sm">count: <span class="font-semibold">' + esc(String(appState.private.count || 0)) + "</span></div>",
      '        <pre class="mt-2 text-xs text-white/70 overflow-auto max-h-40">' +
        esc(appState.private.sample ? JSON.stringify(appState.private.sample, null, 2) : "") +
        "</pre>",
      "      </div>",
      '      <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
      '        <div class="text-xs text-white/50 mb-2">write-echo</div>',
      '        <pre class="text-xs text-white/70 overflow-auto max-h-52">' +
        esc(appState.private.wrote ? JSON.stringify(appState.private.wrote, null, 2) : "") +
        "</pre>",
      "      </div>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "Private", content);
  });

  spa.route("/about", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    const content = [
      '<div class="max-w-3xl space-y-6">',
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-xl font-black mb-2">What this tests</div>',
      '    <ul class="list-disc list-inside text-white/70 space-y-1">',
      "      <li>Client-side routing + History API refresh fallback</li>",
      "      <li>Shared app state across routes (ensureState)</li>",
      "      <li>API usage via ctx.api (metrics, users, echo)</li>",
      "      <li>Timer-driven rerenders (polling + bench)</li>",
      "      <li>Large HTML string replacement performance</li>",
      "    </ul>",
      "  </div>",
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-xl font-black mb-2">Tips</div>',
      '    <div class="text-white/70">Try <code class="text-white/90">/bench</code> with 5,000–20,000 rows, and toggle <b>polling</b> on the dashboard. Watch the render time counter in the header.</div>',
      "  </div>",
      "</div>",
    ].join("\n");
    return layout(ctx.pathname, "About", content);
  });

  spa.route("/dashboard", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    if (!appState.dashboard.metrics && !appState.dashboard.loading) loadMetrics();
    if (appState.dashboard.poll && !appState.dashboard.pollTimer) startMetricsPoll();

    const m = appState.dashboard.metrics;
    const cards = m
      ? [
          { k: "Users", v: String(m.users_total), sub: pill(String(m.users_active) + " active", "green") },
          { k: "Requests/min", v: String(m.requests_per_min_estimate), sub: pill("estimate", "yellow") },
          { k: "DB p95", v: String(m.db_latency_ms_p95) + "ms", sub: pill("p50 " + String(m.db_latency_ms_p50) + "ms", "gray") },
          { k: "Render budget", v: String(m.render_budget_ms) + "ms", sub: pill("target", "gray") },
        ]
          .map((c) => {
            return (
              '<div class="rounded-2xl border border-white/10 bg-white/5 p-5">' +
              '<div class="text-sm text-white/60 mb-1">' +
              esc(c.k) +
              "</div>" +
              '<div class="text-2xl font-black mb-2">' +
              esc(c.v) +
              "</div>" +
              '<div class="text-xs text-white/70">' +
              c.sub +
              "</div>" +
              "</div>"
            );
          })
          .join("\n")
      : "";

    const error = appState.dashboard.error
      ? '<div class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">API error: ' +
        esc(appState.dashboard.error) +
        "</div>"
      : "";

    const loading = appState.dashboard.loading
      ? '<div class="text-sm text-white/60">Loading metrics…</div>'
      : "";

    const spark = (function () {
      const seed = m ? (m.users_total | 0) + (m.db_latency_ms_p95 | 0) : 1337;
      let x = seed;
      const pts = [];
      for (let i = 0; i < 24; i++) {
        x = (x * 1103515245 + 12345) >>> 0;
        const y = 20 + (x % 60);
        pts.push({ x: 10 + i * 12, y });
      }
      const d = pts
        .map((p, i) => (i === 0 ? "M" : "L") + p.x + " " + (90 - p.y))
        .join(" ");
      return (
        '<svg viewBox="0 0 300 100" class="w-full h-24">' +
        '<path d="' +
        d +
        '" fill="none" stroke="rgba(255,255,255,0.6)" stroke-width="3" stroke-linecap="round"/>' +
        '<path d="' +
        d +
        " L 300 100 L 0 100 Z" +
        '" fill="rgba(59,130,246,0.15)"/>' +
        "</svg>"
      );
    })();

    const content = [
      '<div class="max-w-6xl space-y-4">',
      '  <div class="flex flex-wrap gap-3 items-center justify-between">',
      '    <div class="text-sm text-white/70">Metrics come from <code class="text-white/90">GET /api/metrics</code>.</div>',
      '    <div class="flex flex-wrap gap-2">',
      '      <button data-action="dashboard.refresh" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Refresh</button>',
      '      <button data-action="dashboard.togglePoll" class="px-3 py-2 rounded-xl border border-white/10 ' +
        (appState.dashboard.poll ? "bg-blue-500/20 hover:bg-blue-500/30" : "bg-white/5 hover:bg-white/10") +
        ' text-sm font-semibold">Polling: ' +
        (appState.dashboard.poll ? "on" : "off") +
        "</button>",
      "    </div>",
      "  </div>",
      error,
      loading,
      '  <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">',
      cards,
      "  </div>",
      '  <div class="grid lg:grid-cols-3 gap-4">',
      '    <div class="lg:col-span-2 rounded-2xl border border-white/10 bg-white/5 p-5">',
      '      <div class="text-sm text-white/60 mb-2">Synthetic throughput (SVG)</div>',
      spark,
      '      <div class="mt-2 text-xs text-white/60">Rendered client-side. Toggle polling to stress repeated fetch + rerender.</div>',
      "    </div>",
      '    <div class="rounded-2xl border border-white/10 bg-white/5 p-5">',
      '      <div class="text-sm text-white/60 mb-3">Quick actions</div>',
      '      <div class="space-y-2">',
      '        <a href="/users" class="block px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Open users table</a>',
      '        <a href="/bench" class="block px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Run DOM bench</a>',
      '        <a href="/forms" class="block px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Submit a form</a>',
      "      </div>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "Dashboard", content);
  });

  spa.route("/users", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    ensureUsersLoaded();

    const q = esc(appState.users.q || "");
    const page = appState.users.page | 0;
    const size = appState.users.pageSize | 0;
    const total = appState.users.total | 0;
    const maxPage = Math.max(1, Math.ceil(total / Math.max(1, size)));

    const head = [
      '<div class="flex flex-col lg:flex-row lg:items-end gap-3 justify-between">',
      '  <div class="min-w-0">',
      '    <div class="text-sm text-white/70">API-backed table from <code class="text-white/90">GET /api/users</code>.</div>',
      '    <div class="text-xs text-white/50">Try searching, changing page size, and clicking a row to open a dynamic route.</div>',
      "  </div>",
      '  <div class="flex flex-wrap gap-2 items-center">',
      '    <input data-bind="users.q" data-autorender="0" type="text" value="' +
        q +
        '" placeholder="Search name or email…" class="w-64 max-w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm outline-none focus:ring-2 focus:ring-blue-500/40" />',
      '    <select data-bind="users.pageSize" data-bind-type="int" class="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm">',
      [10, 50, 200, 500, 1000]
        .map((n) => '<option value="' + n + '"' + (n === size ? " selected" : "") + ">" + n + "/page</option>")
        .join(""),
      "    </select>",
      '    <button data-action="users.clear" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Clear</button>',
      "  </div>",
      "</div>",
    ].join("\n");

    const status = appState.users.error
      ? '<div class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">API error: ' +
        esc(appState.users.error) +
        "</div>"
      : appState.users.loading
        ? '<div class="text-sm text-white/60">Loading users…</div>'
        : "";

    const rows = (appState.users.items || [])
      .map((u) => {
        const s = String(u.status || "");
        const tone = s === "active" ? "green" : s === "invited" ? "yellow" : s === "disabled" ? "red" : "gray";
        return (
          '<tr class="border-t border-white/10 hover:bg-white/5">' +
          '<td class="py-2 px-3 text-xs text-white/50">' +
          esc(String(u.id)) +
          "</td>" +
          '<td class="py-2 px-3 text-sm font-semibold"><a class="underline decoration-white/20 hover:decoration-white/60" href="/users/' +
          esc(String(u.id)) +
          '">' +
          esc(String(u.name)) +
          "</a></td>" +
          '<td class="py-2 px-3 text-sm text-white/70">' +
          esc(String(u.email)) +
          "</td>" +
          '<td class="py-2 px-3 text-sm text-white/70">' +
          esc(String(u.role)) +
          "</td>" +
          '<td class="py-2 px-3 text-sm">' +
          pill(s, tone) +
          "</td>" +
          '<td class="py-2 px-3 text-sm text-white/70 text-right tabular-nums">' +
          esc(String(u.score)) +
          "</td>" +
          '<td class="py-2 px-3 text-xs text-white/50">' +
          esc(String(u.created_at)) +
          "</td>" +
          "</tr>"
        );
      })
      .join("\n");

    const pager = [
      '<div class="flex items-center justify-between gap-3 mt-4">',
      '  <div class="text-xs text-white/60">Total: <span class="text-white/80">' +
        esc(String(total)) +
        "</span> · Page <span class=\"text-white/80\">" +
        esc(String(page)) +
        "</span> / <span class=\"text-white/80\">" +
        esc(String(maxPage)) +
        "</span></div>",
      '  <div class="flex gap-2">',
      '    <button data-action="users.prev" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold" ' +
        (page <= 1 ? "disabled" : "") +
        ">Prev</button>",
      '    <button data-action="users.next" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold" ' +
        (page >= maxPage ? "disabled" : "") +
        ">Next</button>",
      "  </div>",
      "</div>",
    ].join("\n");

    const table = [
      '<div class="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">',
      '  <div class="overflow-auto">',
      '    <table class="min-w-[900px] w-full">',
      '      <thead class="bg-white/5 text-left">',
      '        <tr class="text-xs text-white/60">',
      '          <th class="py-2 px-3 font-semibold">ID</th>',
      '          <th class="py-2 px-3 font-semibold">Name</th>',
      '          <th class="py-2 px-3 font-semibold">Email</th>',
      '          <th class="py-2 px-3 font-semibold">Role</th>',
      '          <th class="py-2 px-3 font-semibold">Status</th>',
      '          <th class="py-2 px-3 font-semibold text-right">Score</th>',
      '          <th class="py-2 px-3 font-semibold">Created</th>',
      "        </tr>",
      "      </thead>",
      '      <tbody class="text-white">',
      rows || '<tr><td class="py-4 px-3 text-sm text-white/60" colspan="7">No results.</td></tr>',
      "      </tbody>",
      "    </table>",
      "  </div>",
      "</div>",
    ].join("\n");

    const content = ['<div class="max-w-6xl space-y-4">', head, status, table, pager, "</div>"].join("\n");
    return layout(ctx.pathname, "Users", content);
  });

  spa.route("/users/:id", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    const id = clampInt(parseInt(ctx.params.id || "0", 10), 0, 10_000_000);
    if (id > 0) ensureUserLoaded(id);

    const u = appState.userDetail.cache[String(id)] || null;
    const error = appState.userDetail.error
      ? '<div class="rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">API error: ' +
        esc(appState.userDetail.error) +
        "</div>"
      : "";

    const content = [
      '<div class="max-w-3xl space-y-4">',
      '  <div class="flex items-center justify-between gap-3">',
      '    <a href="/users" class="text-sm text-white/70 underline decoration-white/20 hover:decoration-white/60">← Back to users</a>',
      '    <a href="/users/' + esc(String(id + 1)) + '" class="text-sm text-white/70 underline decoration-white/20 hover:decoration-white/60">Next →</a>',
      "  </div>",
      error,
      !u
        ? '<div class="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/60">Loading user…</div>'
        : [
            '<div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
            '  <div class="text-xs text-white/50 mb-1">User #' + esc(String(u.id)) + "</div>",
            '  <div class="text-2xl font-black mb-2">' + esc(String(u.name)) + "</div>",
            '  <div class="text-white/70">' + esc(String(u.email)) + "</div>",
            '  <div class="mt-4 grid sm:grid-cols-2 gap-3">',
            '    <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
            '      <div class="text-xs text-white/50 mb-1">Role</div>',
            '      <div class="text-sm font-semibold">' + esc(String(u.role)) + "</div>",
            "    </div>",
            '    <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
            '      <div class="text-xs text-white/50 mb-1">Status</div>',
            '      <div class="text-sm font-semibold">' + pill(String(u.status), String(u.status) === "active" ? "green" : "gray") + "</div>",
            "    </div>",
            '    <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
            '      <div class="text-xs text-white/50 mb-1">Score</div>',
            '      <div class="text-sm font-semibold tabular-nums">' + esc(String(u.score)) + "</div>",
            "    </div>",
            '    <div class="rounded-xl border border-white/10 bg-black/20 p-4">',
            '      <div class="text-xs text-white/50 mb-1">Created</div>',
            '      <div class="text-sm font-semibold">' + esc(String(u.created_at)) + "</div>",
            "    </div>",
            "  </div>",
            "</div>",
          ].join("\n"),
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "User detail", content);
  });

  spa.route("/forms", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();
    const sending = !!appState.forms.sending;
    const resp = appState.forms.response ? esc(JSON.stringify(appState.forms.response, null, 2)) : "";
    const err = appState.forms.error ? esc(appState.forms.error) : "";

    const content = [
      '<div class="max-w-5xl grid lg:grid-cols-2 gap-4">',
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-xl font-black mb-2">Contact (POST /api/echo)</div>',
      '    <div class="text-sm text-white/70 mb-4">Submit JSON to test request/response and rerender paths.</div>',
      '    <form data-action="forms.submit" class="space-y-3">',
      '      <div class="grid sm:grid-cols-2 gap-3">',
      '        <input name="name" placeholder="Name" class="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm outline-none focus:ring-2 focus:ring-blue-500/40" />',
      '        <input name="email" placeholder="Email" class="px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm outline-none focus:ring-2 focus:ring-blue-500/40" />',
      "      </div>",
      '      <textarea name="message" rows="5" placeholder="Message" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm outline-none focus:ring-2 focus:ring-blue-500/40"></textarea>',
      '      <button type="submit" class="px-4 py-2 rounded-xl border border-white/10 ' +
        (sending ? "bg-white/10" : "bg-blue-500/20 hover:bg-blue-500/30") +
        ' text-sm font-semibold" ' +
        (sending ? "disabled" : "") +
        ">" +
        (sending ? "Sending…" : "Send") +
        "</button>",
      "    </form>",
      err ? '<pre class="mt-4 text-xs text-red-200 bg-red-500/10 border border-red-500/20 rounded-xl p-4 overflow-auto">' + err + "</pre>" : "",
      resp ? '<pre class="mt-4 text-xs text-white/80 bg-black/40 border border-white/10 rounded-xl p-4 overflow-auto">' + resp + "</pre>" : "",
      "  </div>",
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-6">',
      '    <div class="text-xl font-black mb-2">Client-only settings</div>',
      '    <div class="text-sm text-white/70 mb-4">Exercise controlled inputs bound into shared app state.</div>',
      '    <div class="space-y-3">',
      '      <div class="flex items-center justify-between gap-3">',
      '        <div><div class="text-sm font-semibold">Notifications</div><div class="text-xs text-white/50">Toggle state updates without API calls.</div></div>',
      '        <input data-bind="settings.notifications" type="checkbox" ' +
        (appState.settings.notifications ? "checked" : "") +
        ' class="h-5 w-5 accent-blue-500" />',
      "      </div>",
      '      <div class="grid sm:grid-cols-2 gap-3">',
      '        <div class="space-y-1">',
      '          <div class="text-sm font-semibold">Density</div>',
      '          <select data-bind="settings.density" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm">',
      '            <option value="comfortable"' +
        (appState.settings.density === "comfortable" ? " selected" : "") +
        ">Comfortable</option>",
      '            <option value="compact"' +
        (appState.settings.density === "compact" ? " selected" : "") +
        ">Compact</option>",
      "          </select>",
      "        </div>",
      '        <div class="space-y-1">',
      '          <div class="text-sm font-semibold">Bio</div>',
      '          <input data-bind="settings.bio" value="' +
        esc(appState.settings.bio || "") +
        '" placeholder="A short sentence…" class="w-full px-3 py-2 rounded-xl bg-white/5 border border-white/10 text-sm outline-none focus:ring-2 focus:ring-blue-500/40" />',
      "        </div>",
      "      </div>",
      '      <div class="rounded-xl border border-white/10 bg-black/20 p-4 text-xs text-white/70">',
      "        <div class=\"text-white/50 mb-1\">Current state</div>",
      "        <pre class=\"overflow-auto\">" +
        esc(JSON.stringify(appState.settings, null, 2)) +
        "</pre>",
      "      </div>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "Forms", content);
  });

  spa.route("/bench", (ctx) => {
    appState = ctx.ensureState("app", initAppState);
    ensureAuthChecked();

    const rows = clampInt(parseInt(appState.bench.rows, 10), 100, 20000);
    const cols = clampInt(parseInt(appState.bench.cols, 10), 2, 20);
    const tick = appState.bench.tick | 0;

    const headerRow = [];
    for (let c = 0; c < cols; c++) headerRow.push("<th class=\"py-2 px-3 text-xs text-white/60 font-semibold\">C" + c + "</th>");

    const bodyRows = [];
    for (let r = 0; r < rows; r++) {
      const cells = [];
      for (let c = 0; c < cols; c++) {
        const v = ((r + 1) * (c + 3) + tick) % 9973;
        const hot = v % 17 === 0;
        cells.push(
          '<td class="py-1.5 px-3 text-xs tabular-nums ' +
            (hot ? "text-blue-200" : "text-white/70") +
            '">' +
            v +
            "</td>"
        );
      }
      bodyRows.push('<tr class="border-t border-white/10 hover:bg-white/5">' + cells.join("") + "</tr>");
    }

    const content = [
      '<div class="max-w-6xl space-y-4">',
      '  <div class="rounded-2xl border border-white/10 bg-white/5 p-5">',
      '    <div class="flex flex-col lg:flex-row lg:items-end gap-3 justify-between">',
      '      <div class="min-w-0">',
      '        <div class="text-sm text-white/70">Timer-driven rerenders + big DOM. Use this to stress raw <code class="text-white/90">innerHTML</code> replacement.</div>',
      '        <div class="text-xs text-white/50">Hot cells highlight deterministically as tick changes.</div>',
      "      </div>",
      '      <div class="flex flex-wrap gap-2 items-center">',
      '        <label class="text-xs text-white/60">Rows <input data-bind="bench.rows" data-bind-type="int" value="' +
        esc(String(rows)) +
        '" class="ml-2 w-24 px-2 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm" /></label>',
      '        <label class="text-xs text-white/60">Cols <input data-bind="bench.cols" data-bind-type="int" value="' +
        esc(String(cols)) +
        '" class="ml-2 w-20 px-2 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm" /></label>',
      '        <label class="text-xs text-white/60">Interval <input data-bind="bench.intervalMs" data-bind-type="int" value="' +
        esc(String(appState.bench.intervalMs)) +
        '" class="ml-2 w-24 px-2 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm" /></label>',
      '        <button data-action="bench.bump" class="px-3 py-2 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-semibold">Tick</button>',
      '        <button data-action="bench.toggle" class="px-3 py-2 rounded-xl border border-white/10 ' +
        (appState.bench.running ? "bg-blue-500/20 hover:bg-blue-500/30" : "bg-white/5 hover:bg-white/10") +
        ' text-sm font-semibold">' +
        (appState.bench.running ? "Stop" : "Start") +
        "</button>",
      "      </div>",
      "    </div>",
      "  </div>",
      '  <div class="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">',
      '    <div class="overflow-auto max-h-[70vh]">',
      '      <table class="min-w-full">',
      '        <thead class="sticky top-0 bg-gray-950/80 backdrop-blur border-b border-white/10">',
      '          <tr class="text-left">' + headerRow.join("") + "</tr>",
      "        </thead>",
      '        <tbody class="text-white">' + bodyRows.join("") + "</tbody>",
      "      </table>",
      "    </div>",
      "  </div>",
      "</div>",
    ].join("\n");

    return layout(ctx.pathname, "Bench", content);
  });

  spa.start();
})();
