// Controller: connect the existing interface to our Flask chatbot API.
import { getSession, sendChatMessage } from "./chatbot_api.js";
import { createChatUI } from "./chatbot_ui.js";

export function initChatbot(page) {
  const host = page.querySelector("[data-chatbot]");
  if (!host || host.dataset.initialized) return;
  host.dataset.initialized = "true";
  const ui = createChatUI(host);
  let sending = false;
  // Get the CSRF token Flask requires for POST requests, including guest chat.
  // If initialization fails, sending a message can try loading the session again.
  const sessionReady = getSession().catch(() => null);

  async function sendMessage(preset) {
    const message = (preset ?? ui.readMessage()).trim();
    if (!message || sending) return;
    if (message.length > 2000) {
      ui.showError("Please keep your message under 2,000 characters.");
      return;
    }
    sending = true;
    ui.addUserMessage(message);
    ui.clearInput();
    ui.setChatLoading(true);
    ui.showTypingIndicator();
    try {
      await sessionReady;
      const data = await sendChatMessage(message);
      // Filters, sources and other backend metadata are never rendered.
      ui.addAssistantMessage(data.answer);
    } catch (error) {
      ui.showError(error.message);
    } finally {
      ui.hideTypingIndicator();
      ui.setChatLoading(false);
      sending = false;
    }
  }

  host.addEventListener("click", (event) => {
    const button = event.target.closest("[data-action]");
    if (button?.dataset.action === "chat") ui.toggleChat();
    if (button?.dataset.action === "chat-suggestion")
      sendMessage(button.textContent);
  });
  // The existing single-line input submits this form on Enter as well as Send.
  host.addEventListener("submit", (event) => {
    if (!event.target.matches('[data-form="chat"]')) return;
    event.preventDefault();
    sendMessage();
  });
}
