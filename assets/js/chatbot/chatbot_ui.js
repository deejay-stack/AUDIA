// DOM behavior only: reuse the existing chat, message and suggestion templates.
import { clone, field, icon } from "../shared/shared.js";

export function createChatUI(host) {
  const toggle = host.querySelector('[data-action="chat"]');
  let panel;
  let typing;
  let opened = false, motion;

  function scrollToLatestMessage() {
    const messages = field(panel, "messages");
    messages.scrollTop = messages.scrollHeight;
  }

  function addMessage(message, role) {
    const bubble = clone("message");
    if (role === "user") {
      bubble.className =
        "chatbot-message--customer";
    }
    // Both customer text and model responses are untrusted plain text.
    bubble.textContent = message;
    field(panel, "messages").append(bubble);
    scrollToLatestMessage();
    return bubble;
  }

  function toggleChat() {
    if (!panel) {
      panel = clone("chat");
      host.append(panel);
      field(panel, "messages").append(
        clone("message"),
        clone("chat-suggestions"),
      );
    }
    const open = opened = !opened;
    motion?.cancel();
    panel.hidden = false;
    panel.inert = !open;
    const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
    motion = panel.animate(open ? [
      { opacity: 0, transform: "translateY(14px) scale(.98)" }, { opacity: 1, transform: "none" },
    ] : [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(14px) scale(.98)" }],
    { duration: reduced ? 0 : 180, easing: "ease-out" });
    motion.finished.then(() => { if (!opened) panel.hidden = true; }).catch(() => {});
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute(
      "aria-label",
      open ? "Close AUDI, Our AI Assistant" : "Ask AUDI, Our AI Assistant",
    );
    toggle.replaceChildren(icon(open ? "x" : "message-circle", open ? 20 : 21));
    if (open) {
      scrollToLatestMessage();
      field(panel, "chat-input").focus();
    } else toggle.focus();
  }

  function setChatLoading(loading) {
    // Disable the form while the previous request is still running.
    field(panel, "chat-input").disabled = loading;
    panel.querySelector('button[type="submit"]').disabled = loading;
    panel
      .querySelectorAll('[data-action="chat-suggestion"]')
      .forEach((button) => {
        button.disabled = loading;
      });
    panel
      .querySelector('[data-form="chat"]')
      .setAttribute("aria-busy", String(loading));
    if (!loading && !panel.hidden) field(panel, "chat-input").focus();
  }

  return {
    toggleChat,
    readMessage: () => field(panel, "chat-input").value,
    clearInput: () => {
      field(panel, "chat-input").value = "";
    },
    addUserMessage(message) {
      panel
        .querySelector('[data-action="chat-suggestion"]')
        ?.parentElement.remove();
      addMessage(message, "user");
    },
    addAssistantMessage: (message) => addMessage(message, "assistant"),
    showError: (message) => { const bubble = addMessage(message, "assistant"); bubble.classList.add("chatbot-message--error"); bubble.setAttribute("role", "alert"); },
    showTypingIndicator() {
      typing = addMessage("AUDI is typing…", "assistant");
      typing.setAttribute("role", "status");
      typing.classList.add("chatbot-typing");
    },
    hideTypingIndicator() {
      typing?.remove();
      typing = null;
    },
    setChatLoading,
    closeChat() { if (opened) toggleChat(); },
  };
}
