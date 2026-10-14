// Flask chooses the page. This file starts that page's interactive features.
import { initChatbot } from "../chatbot/chatbot.js";
import { mountStore } from "../catalog/catalog.js";
import { mountAuth } from "../auth/auth.js";
import { mountAdmin } from "../admin/admin.js";
import { mountAccount } from "../account/account.js";
import { $$, icon, animate, api, notice, writeCart } from "./shared.js";

const root = document.getElementById("root");
const page = root.firstElementChild;
const pageName = document.body.dataset.page;
let user = null;
let theme = localStorage.getItem("audia-theme") || "dark";

// Keep only small navigation preferences across normal page loads.
const app = {
  get user() {
    return user;
  },
  set user(value) {
    user = value;
  },
  get catalogCategory() {
    return sessionStorage.getItem("audia-category") || "";
  },
  set catalogCategory(value) {
    sessionStorage.setItem("audia-category", value);
  },
  get searchProduct() {
    return sessionStorage.getItem("audia-search") || "";
  },
  set searchProduct(value) {
    sessionStorage.setItem("audia-search", value);
  },
  get openFinder() {
    return sessionStorage.getItem("audia-finder") === "true";
  },
  set openFinder(value) {
    sessionStorage.setItem("audia-finder", String(value));
  },
  resetToken: document.body.dataset.resetToken || "",
  navigate(screen, role = "customer") {
    const pages = {
      landing: "/",
      storefront: "/shop",
      account: "/account",
      dashboard: "/admin",
    };
    let url = pages[screen] || "/login";
    if (screen === "auth" && role === "register") url = "/register";
    if (screen === "auth" && role === "admin") url = "/login?role=admin";
    window.location.assign(url);
  },
  login(account) {
    user = account;
    app.navigate(account.role === "admin" ? "dashboard" : "storefront");
  },
  async logout() {
    try {
      await api("/auth/logout", { method: "POST" });
      user = null;
      writeCart([]);
      app.navigate("landing");
    } catch (error) {
      notice(error.message);
    }
  },
};

function updateTheme() {
  document.documentElement.classList.toggle("dark", theme === "dark");
  localStorage.setItem("audia-theme", theme);
  $$(root, '[data-action="theme"]').forEach((button) => {
    const label = `Switch to ${theme === "dark" ? "light" : "dark"} mode`;
    button.setAttribute("aria-label", label);
    button.title = label;
    button.replaceChildren(icon(theme === "dark" ? "sun" : "moon", 17));
  });
}
root.addEventListener("click", (event) => {
  if (event.target.closest('[data-action="theme"]')) {
    theme = theme === "dark" ? "light" : "dark";
    updateTheme();
  }
});
window.addEventListener("audia:unauthorized", () => {
  if (!user) return;
  user = null;
  writeCart([]);
  app.navigate("auth");
});

// Old bookmarks and emailed reset links remain usable after the route change.
function followOldBookmark() {
  const legacy = {
    "#storefront": "/shop",
    "#auth": "/login",
    "#account": "/account",
    "#dashboard": "/admin",
    "#landing": "/",
  };
  if (legacy[location.hash]) {
    location.replace(legacy[location.hash]);
    return true;
  }
  if (location.hash.startsWith("#reset/")) {
    location.replace(
      "/reset-password?token=" + encodeURIComponent(location.hash.slice(7)),
    );
    return true;
  }
  return false;
}
window.addEventListener("hashchange", followOldBookmark);

if (!followOldBookmark()) {
  try {
    user = (await api("/auth/session")).user;
  } catch (error) {
    notice(error.message);
  }

  if (["storefront", "account", "dashboard", "tuner", "lessons"].includes(pageName) && !user) {
    app.navigate("auth");
  } else {
    if (pageName === "storefront") mountStore(page, app);
    if (pageName === "auth")
      mountAuth(page, app, document.body.dataset.authMode);
    if (pageName === "account") mountAccount(page, app);
    if (pageName === "dashboard") mountAdmin(page, app);
    if (pageName === "tuner") (await import("../tuner/tuner.js")).mountTuner(page);
    if (pageName === "landing") {
      page.querySelectorAll("[data-auth-entry]").forEach((node) => {
        node.hidden = Boolean(user);
      });
      page.querySelectorAll("[data-member-entry]").forEach((node) => {
        node.hidden = !user;
      });
      page.addEventListener("click", (event) => {
        const button = event.target.closest("[data-action]");
        if (!button) return;
        const action = button.dataset.action;
        if (action === "register") app.navigate("auth", "register");
        if (action === "sign-in") app.navigate("auth");
        if (action === "browse") {
          app.catalogCategory = button.dataset.category || "";
          app.navigate(user ? "storefront" : "auth");
        }
      });
    }
    initChatbot(page);
    updateTheme();
    animate(page);
    // Enable controls after their handlers and session have loaded.
    root.inert = false;
    root.removeAttribute("aria-busy");
  }
}
