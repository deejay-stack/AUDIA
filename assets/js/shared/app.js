// Flask chooses the page. This file starts that page's interactive features.
import { initChatbot } from "../chatbot/chatbot.js";
import { mountStore } from "../catalog/catalog.js";
import { mountAuth } from "../auth/auth.js";
import { mountAdmin } from "../admin/admin.js";
import { mountAccount } from "../account/account.js";
import { $$, icon, animate, api, notice, writeCart, readCart } from "./shared.js";

const root = document.getElementById("root");
const page = root.firstElementChild;
const pageName = document.body.dataset.page;
let user = null;
let loggingOut = false;
let controller;
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
    if (user?.role === "admin" && ["storefront", "orders"].includes(screen)) screen = "dashboard";
    const pages = {
      landing: "/",
      storefront: "/shop",
      account: "/account",
      dashboard: "/admin",
      orders: "/orders",
    };
    let url = pages[screen] || "/login";
    if (screen === "auth" && role === "register") url = "/register";
    if (screen === "auth" && role === "admin") url = "/admin/login";
    window.location.assign(url);
  },
  login(account) {
    user = account;
    localStorage.setItem("audia-auth-event", `login:${Date.now()}`);
    const next=new URLSearchParams(location.search).get('next');
    if(next && /^\/(receipts|verify|refunds)\//.test(next)) {location.assign(next);return;}
    app.navigate(account.role === "admin" ? "dashboard" : "storefront");
  },
  async logout() {
    if (loggingOut) return;
    loggingOut = true;
    root.inert = true;
    try {
      await api("/auth/logout", { method: "POST" });
      user = null;
      writeCart([]);
      sessionStorage.removeItem("audia-checkout");
      sessionStorage.removeItem("audia-auth-message");
      sessionStorage.removeItem("audia-signup-email");
      localStorage.setItem("audia-auth-event", `logout:${Date.now()}`);
      app.navigate("landing");
    } catch (error) {
      notice(error.message);
      root.inert = false;
    } finally {
      loggingOut = false;
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
  const loginRole = user.role;
  user = null;
  writeCart([]);
  app.navigate("auth", loginRole);
});
// Revalidate restored pages and other tabs instead of trusting frozen DOM state.
window.addEventListener("pageshow", (event) => { if (event.persisted) location.reload(); });
window.addEventListener("storage", (event) => {
  if (event.key === "audia-auth-event") { root.inert = true; location.reload(); }
});
window.addEventListener("pagehide", () => controller?.destroy?.());
function cartBadges() {
  const count = readCart().reduce((sum, item) => sum + item.qty, 0);
  document.querySelectorAll("[data-cart-count]").forEach((node) => {
    node.textContent = count;
    node.setAttribute("aria-label", `${count} items in cart`);
  });
}
window.addEventListener("audia:cart-changed", cartBadges);
cartBadges();

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
  let sessionLoaded = false;
  try {
    user = (await api("/auth/session")).user;
    sessionLoaded = true;
  } catch (error) {
    notice(error.message);
  }

  const protectedPage = ["storefront", "account", "orders", "dashboard", "tuner", "lessons"].includes(pageName);
  if (protectedPage && !sessionLoaded) {
    // A network outage is not proof of logout; avoid login/protected-page redirect loops.
    notice("Unable to confirm your session. Check your connection and reload this page.");
  } else if (protectedPage && !user) {
    app.navigate("auth", pageName === "dashboard" ? "admin" : "customer");
  } else {
    if (pageName === "storefront") controller = mountStore(page, app);
    if (pageName === "auth")
      controller = mountAuth(page, app, document.body.dataset.authMode);
    if (["account", "orders"].includes(pageName)) controller = mountAccount(page, app);
    if (pageName === "dashboard") controller = mountAdmin(page, app);
    if (pageName === "tuner") controller = (await import("../tuner/tuner.js")).mountTuner(page);
    if (pageName === "lessons") controller = (await import("../lessons/lessons.js")).mountLessons(page);
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

// Normal route navigation starts at the top; preserve intentional hash anchors.
if (!location.hash && performance.getEntriesByType("navigation")[0]?.type === "navigate") {
  history.scrollRestoration = "manual"; window.scrollTo(0, 0);
}
document.addEventListener("error", (event) => {
  const logo = event.target.closest?.(".provider-logo img");
  if (logo) { logo.hidden = true; logo.nextElementSibling.hidden = false; }
}, true);
