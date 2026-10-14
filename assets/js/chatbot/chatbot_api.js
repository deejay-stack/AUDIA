// Flask communication only. Tokens stay in memory, never in browser storage.
let csrfToken = "";
let sessionRequest = null;
const unavailable =
  "Sorry, I couldn't process your message right now. Please try again.";

async function requestJson(url, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(url, {
      ...options,
      credentials: "same-origin",
      signal: controller.signal,
    });
    const value = await response.json().catch(() => null);
    const data =
      value && typeof value === "object" && !Array.isArray(value) ? value : {};
    return { response, data };
  } catch {
    // Do not show network exceptions or server internals to customers.
    throw new Error(unavailable);
  } finally {
    clearTimeout(timeout);
  }
}

export async function getSession() {
  // Share an in-flight request if opening chat and sending happen together.
  if (!sessionRequest) {
    sessionRequest = (async () => {
      const { response, data } = await requestJson("/api/auth/session");
      if (
        !response.ok ||
        typeof data.csrf_token !== "string" ||
        !data.csrf_token
      ) {
        throw new Error(unavailable);
      }
      csrfToken = data.csrf_token;
      return data;
    })();
  }
  try {
    return await sessionRequest;
  } finally {
    sessionRequest = null;
  }
}

export async function refreshCsrfToken() {
  csrfToken = "";
  return getSession();
}

export async function sendChatMessage(message) {
  if (!csrfToken) await getSession();

  // Retry only a rejected CSRF request, once. Other failures are not retried.
  for (let attempt = 0; attempt < 2; attempt += 1) {
    // The browser talks only to Flask. Flask owns the Gemini key and AI calls.
    const { response, data } = await requestJson("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "X-CSRF-Token": csrfToken,
      },
      body: JSON.stringify({ message }),
    });
    const sessionChanged =
      response.status === 403 &&
      typeof data.error === "string" &&
      data.error.startsWith("Your session has changed.");
    if (sessionChanged && attempt === 0) {
      await refreshCsrfToken();
      continue;
    }
    if (
      !response.ok ||
      typeof data.answer !== "string" ||
      !data.answer.trim()
    ) {
      throw new Error(
        response.status === 429
          ? "Please wait a moment before sending another message."
          : unavailable,
      );
    }
    return data;
  }
}
