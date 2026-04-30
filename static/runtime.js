// static/runtime.js
//
// Minimal client runtime: mounts components and dispatches events.
// No frameworks, no eval, no inline JS required.

(function () {
  const App = {};

  async function postJSON(url, body) {
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

  document.addEventListener("DOMContentLoaded", () => {
    App.mount();
  });
})();

