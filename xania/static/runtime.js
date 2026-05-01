// static/runtime.js
//
// Minimal client runtime: mounts components and dispatches events.
// No frameworks, no eval, no inline JS required.

(function () {
  const App = {};
  const localHandlers = {};

  function serverEventsEnabled() {
    return Boolean(window.XaniaConfig && window.XaniaConfig.serverEvents === true);
  }

  async function postJSON(url, body) {
    if (!serverEventsEnabled()) {
      throw new Error("Server events disabled (set window.XaniaConfig.serverEvents = true to enable)");
    }
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const txt = await res.text().catch(() => "");
      throw new Error("HTTP " + res.status + " " + txt);
    }
    return await res.json();
  }

  App.applyUpdates = function applyUpdates(updates) {
    if (!Array.isArray(updates)) return;
    for (const u of updates) {
      if (!u || !u.id) continue;
      const el = document.getElementById(u.id);
      if (!el) continue;
      el.innerHTML = u.html || "";
    }
  };

  App.dispatch = async function dispatch(component, action, payload) {
    const handler = localHandlers[component];
    if (handler && handler(action, payload || {}) === true) {
      return;
    }
    try {
      const data = await postJSON("/event", {
        component,
        action,
        payload: payload || {},
      });
      App.applyUpdates(data.updates);
    } catch (err) {
      console.error("[App.dispatch] failed", err);
    }
  };

  App.mount = async function mount() {
    const mounts = document.querySelectorAll("[data-component]");
    for (const el of mounts) {
      const component = el.getAttribute("data-component");
      if (!component) continue;
      // Fetch initial HTML for each mount point.
      await App.dispatch(component, "__mount__", {});
    }
  };

  window.App = App;

  // Optional local (no-backend) handlers for simple demo components.
  // If a handler returns true, the network request is skipped.
  localHandlers["Counter"] = function counterLocalHandler(action, payload) {
    // Expect a single mount point with id="counter" for the demo.
    const root = document.getElementById("counter");
    if (!root) return false;

    if (action === "__mount__") {
      // Fully client-side mount to avoid any backend calls for the demo counter.
      if (root.childNodes.length > 0) return true;
      root.innerHTML = [
        '<div class="flex flex-col items-center justify-center min-h-screen bg-gray-950">',
        '  <h1 class="text-2xl font-black text-white mb-6">Counter</h1>',
        '  <span class="text-6xl font-black text-white block mb-8">0</span>',
        '  <div class="flex gap-4 justify-center">',
        '    <button class="bg-red-600 text-white px-6 py-3 rounded-xl text-xl font-bold cursor-pointer border-0 hover:bg-red-500" onclick="App.dispatch(\\'Counter\\',\\'decrement\\')">−</button>',
        '    <button class="bg-gray-700 text-white px-6 py-3 rounded-xl text-xl font-bold cursor-pointer border-0" onclick="App.dispatch(\\'Counter\\',\\'reset\\')">Reset</button>',
        '    <button class="bg-green-600 text-white px-6 py-3 rounded-xl text-xl font-bold cursor-pointer border-0 hover:bg-green-500" onclick="App.dispatch(\\'Counter\\',\\'increment\\')">+</button>',
        "  </div>",
        "</div>",
      ].join("\n");
      return true;
    }

    const valueEl = root.querySelector("span");
    if (!valueEl) return false;

    const current = parseInt(valueEl.textContent || "0", 10) || 0;
    let next = current;
    if (action === "increment") next = current + 1;
    else if (action === "decrement") next = current - 1;
    else if (action === "reset") next = 0;
    else return false;

    valueEl.textContent = String(next);
    valueEl.classList.remove("text-green-400", "text-red-400", "text-white");
    valueEl.classList.add(next > 0 ? "text-green-400" : next < 0 ? "text-red-400" : "text-white");
    return true;
  };

  document.addEventListener("DOMContentLoaded", () => {
    App.mount();
  });
})();
