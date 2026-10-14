// Default: deterministic UI checks against tests/serve.py, with AI responses mocked.
// AUDIA_CHAT_LIVE=1: send the four requested prompts to the actual running backend.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const base = process.env.AUDIA_BASE_URL || "http://127.0.0.1:5056";
const prompts = [
  "Hello",
  "I am a beginner and I want a black acoustic guitar with a cutaway.",
  "I am a beginner looking for an acoustic guitar under ₱10,000. What do you recommend?",
  "How much is ACOUSTIC_001 and is it still available?",
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({
      viewport: { width: 390, height: 844 },
      reducedMotion: "reduce",
    });
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    await page.goto(base);
    await page
      .getByRole("button", { name: "Open customer support", exact: true })
      .click();
    const panel = page.locator(".chat-panel");
    const input = panel.locator('[data-field="chat-input"]');
    const send = panel.getByRole("button", {
      name: "Send message",
      exact: true,
    });
    const messages = panel.locator('[data-field="messages"]');
    const typing = panel.getByRole("status");
    async function recovered() {
      await page.waitForFunction(() => {
        const input = document.querySelector(
          '.chat-panel [data-field="chat-input"]',
        );
        return (
          input &&
          !input.disabled &&
          !document.querySelector('.chat-panel [role="status"]')
        );
      });
    }

    if (process.env.AUDIA_CHAT_LIVE === "1") {
      for (const prompt of prompts) {
        const responseReady = page.waitForResponse(
          (response) =>
            response.url().endsWith("/api/chat") &&
            response.request().method() === "POST",
          { timeout: 70000 },
        );
        await input.fill(prompt);
        await send.click();
        const response = await responseReady;
        const data = await response.json();
        assert.equal(
          response.status(),
          200,
          `Live backend did not succeed for: ${prompt}`,
        );
        assert.equal(response.request().postDataJSON().message, prompt);
        assert.ok(data.answer?.trim(), "Live backend returned no answer");
        await recovered();
        assert.ok((await messages.innerText()).includes(data.answer.trim()));
        console.log(
          JSON.stringify({
            prompt,
            answer: data.answer,
            sql_match_count: data.sql_match_count,
          }),
        );
      }
      assert.deepEqual(errors, []);
      console.log(
        "PASS: Four live backend answers displayed for a guest, with Unicode preserved.",
      );
      return;
    }

    let requests = [];
    const requestTokens = [];
    let mode = "success";
    let release;
    let receivedDelayedRequest;
    const delayedRequest = new Promise((resolve) => {
      receivedDelayedRequest = resolve;
    });
    let attempts = 0;
    let sessionRefreshes = 0;
    page.on("request", (request) => {
      if (request.url().endsWith("/api/auth/session")) sessionRefreshes += 1;
    });
    const friendlyError =
      "Sorry, I couldn't process your message right now. Please try again.";
    await page.route("**/api/chat", async (route) => {
      const request = route.request();
      requests.push(request.postDataJSON());
      requestTokens.push(request.headers()["x-csrf-token"]);
      assert.equal(
        request.headers()["content-type"],
        "application/json; charset=utf-8",
      );
      assert.ok(request.headers()["x-csrf-token"]);
      assert.ok(request.headers().cookie, "Use the same-origin Flask session");
      if (mode === "delay")
        await new Promise((resolve) => {
          release = resolve;
          receivedDelayedRequest();
        });
      if (mode === "network") return route.abort();
      if (mode === "csrf-once" || mode === "csrf-always") {
        attempts += 1;
        if (mode === "csrf-always" || attempts === 1) {
          return route.fulfill({
            status: 403,
            json: {
              error:
                "Your session has changed. Refresh the page and try again.",
            },
          });
        }
      }
      if (mode === "forbidden")
        return route.fulfill({
          status: 403,
          json: { error: "Private authorization exception" },
        });
      if (mode === "server")
        return route.fulfill({
          status: 500,
          json: { error: "psycopg.errors SECRET_INTERNAL" },
        });
      if (mode === "invalid")
        return route.fulfill({
          status: 200,
          body: "null",
          contentType: "application/json",
        });
      if (mode === "html")
        return route.fulfill({
          status: 502,
          body: "<h1>Internal exception</h1>",
          contentType: "text/html",
        });
      return route.fulfill({
        json: {
          answer: `Answer: ${request.postDataJSON().message}`,
          sources: [{ title: "SECRET_INTERNAL" }],
          applied_filters: { secret: "SECRET_INTERNAL" },
        },
      });
    });
    await input.fill("   ");
    await send.click();
    assert.equal(requests.length, 0, "Whitespace must not call Flask");

    mode = "delay";
    await input.fill(prompts[0]);
    await send.click();
    await typing.waitFor();
    await delayedRequest;
    assert.equal(await input.isDisabled(), true);
    assert.equal(await send.isDisabled(), true);
    await panel.locator("form").evaluate((form) => {
      form.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true }),
      );
      form.dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true }),
      );
    });
    // Closing and reopening must preserve both the pending request and the draft/history.
    await page
      .getByRole("button", { name: "Close customer support", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Open customer support", exact: true })
      .click();
    assert.equal(await send.isDisabled(), true);
    assert.equal(requests.length, 1);
    release();
    await messages.getByText("Answer: Hello", { exact: true }).waitFor();
    await recovered();
    mode = "success";
    for (const prompt of prompts.slice(1)) {
      await input.fill(prompt);
      await input.press("Enter");
      await messages.getByText(`Answer: ${prompt}`, { exact: true }).waitFor();
      await recovered();
      assert.equal(requests.at(-1).message, prompt);
    }
    const unsafe = '<img src=x onerror="window.chatInjected=true"> ₱10,000';
    await input.fill(unsafe);
    await send.click();
    await messages.getByText(`Answer: ${unsafe}`, { exact: true }).waitFor();
    await recovered();
    assert.equal(await messages.locator("img").count(), 0);
    assert.equal(await page.evaluate(() => !!window.chatInjected), false);
    assert.equal(
      (await messages.innerText()).includes("SECRET_INTERNAL"),
      false,
    );

    for (const failure of [
      "server",
      "network",
      "invalid",
      "html",
      "forbidden",
      "csrf-always",
    ]) {
      mode = failure;
      attempts = 0;
      const count = requests.length;
      const previousErrors = await messages
        .getByText(friendlyError, { exact: true })
        .count();
      await input.fill(`Failure ${failure}`);
      await send.click();
      await messages
        .getByText(friendlyError, { exact: true })
        .nth(previousErrors)
        .waitFor();
      await recovered();
      assert.equal(requests.length - count, failure === "csrf-always" ? 2 : 1);
      assert.equal(
        (await messages.innerText()).includes("SECRET_INTERNAL"),
        false,
      );
    }
    mode = "csrf-once";
    attempts = 0;
    // Rotate the real Flask cookie as another tab would, without updating chat's memory.
    const oldSession = await (
      await page.request.get(base + "/api/auth/session")
    ).json();
    const logout = await page.request.post(base + "/api/auth/logout", {
      headers: { "X-CSRF-Token": oldSession.csrf_token },
    });
    assert.equal(logout.status(), 200);
    const rotatedSession = await logout.json();
    const refreshes = sessionRefreshes;
    await input.fill("Refresh session");
    await send.click();
    await messages
      .getByText("Answer: Refresh session", { exact: true })
      .waitFor();
    await recovered();
    assert.equal(attempts, 2);
    assert.equal(sessionRefreshes - refreshes, 1);
    assert.equal(requests.at(-1).message, requests.at(-2).message);
    assert.equal(requestTokens.at(-2), oldSession.csrf_token);
    assert.equal(requestTokens.at(-1), rotatedSession.csrf_token);
    assert.notEqual(requestTokens.at(-1), requestTokens.at(-2));
    mode = "success";
    await input.fill("Still usable");
    await send.click();
    await messages.getByText("Answer: Still usable", { exact: true }).waitFor();
    await recovered();
    assert.equal(
      await messages.evaluate(
        (node) =>
          Math.abs(node.scrollHeight - node.scrollTop - node.clientHeight) < 3,
      ),
      true,
    );
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );

    // The same interface also works in the protected shop after a real fixture login.
    const session = await (
      await page.request.get(base + "/api/auth/session")
    ).json();
    const login = await page.request.post(base + "/api/auth/login", {
      headers: { "X-CSRF-Token": session.csrf_token },
      data: {
        email: "admin@example.com",
        password: "admin-password-123",
        role: "admin",
      },
    });
    assert.equal(login.status(), 200);
    await page.goto(base + "/shop");
    await page
      .getByRole("button", { name: "Open customer support", exact: true })
      .click();
    await panel
      .getByRole("button", { name: "I am a beginner", exact: true })
      .click();
    await messages
      .getByText("Answer: I am a beginner", { exact: true })
      .waitFor();
    await recovered();
    assert.deepEqual(errors, []);
    console.log(
      "PASS: Guest/member chat, Send/Enter/suggestions, Unicode, answer-only safe text, empty/duplicate prevention, typing, close/reopen and scrolling.",
    );
    console.log(
      "PASS: Server/network/malformed errors recover; CSRF refresh retries once; unrelated 403 is not retried.",
    );
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
