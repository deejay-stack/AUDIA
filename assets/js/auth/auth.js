import { $, field, icon, api } from "../shared/shared.js";

export function mountAuth(page, app, initialRole) {
  const role = initialRole === "admin" ? "admin" : "customer";
  let mode =
    initialRole === "reset"
      ? "reset"
      : initialRole === "register"
        ? "register"
        : "login";
  let loading = false,
    alive = true;
  const titles = {
    login: role === "admin" ? "Administrator sign in" : "Customer sign in",
    register: "Find your people. Find your sound.",
    forgot: "Let’s get you back in.",
    reset: "A fresh start.",
  };
  const subtitles = {
    login:
      role === "admin" ? "Use the authorized administrator account to manage the store." : "Use your customer account to shop and track your orders.",
    register:
      "Create your account to save instruments, place orders, and keep track of your gear.",
    forgot:
      "Enter your account email and we’ll send you a password reset link.",
    reset: "Choose a new password for your AUDIA account.",
  };
  const labels = {
    login: role === "admin" ? "Open dashboard" : "Sign in",
    register: "Create account",
    forgot: "Send reset link",
    reset: "Reset password",
  };
  function error(message) {
    field(page, "login-error").textContent = message;
    field(page, "login-error").hidden = !message;
  }
  function success(message) {
    field(page, "auth-success").textContent = message;
    field(page, "auth-success").hidden = !message;
  }
  function render() {
    field(page, "auth-title").textContent = titles[mode];
    field(page, "auth-subtitle").textContent = subtitles[mode];
    field(page, "roles").hidden = mode !== "login";
    field(page, "signup").hidden = mode !== "login" || role === "admin";
    field(page, "back-login").hidden = mode === "login";
    field(page, "login-options").hidden = mode !== "login";
    for (const [name, visible] of [
      ["name", mode === "register"],
      ["email", mode !== "reset"],
      ["password", mode !== "forgot"],
      ["confirm", ["register", "reset"].includes(mode)],
    ]) {
      field(page, `${name}-wrap`).hidden = !visible;
      field(page, name).required = visible;
      field(page, name).disabled = !visible;
    }
    field(page, "password").minLength = mode === "login" ? 1 : 10;
    field(page, "password").autocomplete =
      mode === "login" ? "current-password" : "new-password";
    field(page, "password-hint").hidden = !["register", "reset"].includes(mode);
    labels.login = role === "admin" ? "Open dashboard" : "Sign in";
    const submit = field(page, "login-submit");
    submit.disabled = loading;
    submit.replaceChildren(
      loading ? "Please wait… " : labels[mode] + " ",
      icon("arrow-right", 16),
    );
  }
  function change(next) {
    mode = next;
    error("");
    success("");
    render();
  }
  page.addEventListener("click", (event) => {
    const action = event.target.closest("[data-action]")?.dataset.action;
    if (action === "home" || action === "store") {
      app.catalogCategory = "";
      app.navigate(app.user ? "storefront" : "landing");
    }
    if (loading) return;
    if (action === "register") {
      app.navigate("auth", "register");
    }
    if (action === "forgot") change("forgot");
    if (action === "back-login") {
      if (["register", "reset"].includes(mode)) app.navigate("auth", role);
      else change("login");
    }
    if (action === "password") {
      const input = field(page, "password"),
        showing = input.type === "password";
      input.type = showing ? "text" : "password";
      const button = $(page, '[data-action="password"]');
      button.setAttribute(
        "aria-label",
        showing ? "Hide password" : "Show password",
      );
      button.replaceChildren(icon(showing ? "eye-off" : "eye", 16));
    }
  });
  page.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (loading) return;
    const password = field(page, "password").value;
    if (
      ["register", "reset"].includes(mode) &&
      password !== field(page, "confirm").value
    )
      return error("The passwords do not match.");
    loading = true;
    error("");
    success("");
    render();
    const submitted = mode;
    try {
      const paths = {
        login: role === "admin" ? "admin/login" : "login",
        register: "register",
        forgot: "forgot-password",
        reset: "reset-password",
      };
      const data = await api(`/auth/${paths[submitted]}`, {
        method: "POST",
        body: {
          email: field(page, "email").value,
          password,
          name: field(page, "name").value,
          role,
          remember: field(page, "remember").checked,
          token: app.resetToken || "",
        },
      });
      if (!alive) return;
      if (submitted === "register") {
        sessionStorage.setItem(
          "audia-signup-email",
          field(page, "email").value,
        );
        sessionStorage.setItem("audia-auth-message", data.message);
        field(page, "password").value = "";
        field(page, "confirm").value = "";
        app.navigate("auth");
      } else if (data.user) {
        if (data.user.role !== role) throw new Error("Incorrect email or password.");
        app.login(data.user);
      } else {
        if (submitted === "reset") {
          app.resetToken = "";
          sessionStorage.setItem("audia-auth-message", data.message);
          app.navigate("auth", data.login_role === "admin" ? "admin" : "customer");
          return;
        }
        success(data.message);
      }
    } catch (failure) {
      if (alive) error(failure.message);
    } finally {
      loading = false;
      if (alive) render();
    }
  });
  render();
  if (mode === "login" && sessionStorage.getItem("audia-auth-message")) {
    field(page, "email").value =
      sessionStorage.getItem("audia-signup-email") || "";
    success(sessionStorage.getItem("audia-auth-message"));
    sessionStorage.removeItem("audia-auth-message");
    sessionStorage.removeItem("audia-signup-email");
  }
  return {
    destroy() {
      alive = false;
    },
  };
}
