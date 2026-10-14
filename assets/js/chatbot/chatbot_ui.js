// DOM behavior only: reuse the existing chat, message and suggestion templates.
import { clone, field, icon, animate } from "../shared/shared.js";

export function createChatUI(host) {
  const toggle = host.querySelector('[data-action="chat"]');
  let panel;
  let typing;

  function scrollToLatestMessage() {
    const messages = field(panel, "messages");
    messages.scrollTop = messages.scrollHeight;
  }

  function addMessage(message, role) {
    const bubble = clone("message");
    if (role === "user") {
      bubble.className =
        "max-w-[86%] rounded-2xl px-4 py-3 text-xs leading-5 ml-auto bg-zinc-950 text-white dark:bg-acid dark:text-ink";
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
      animate(panel);
    } else {
      panel.hidden = !panel.hidden;
    }
    const open = !panel.hidden;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute(
      "aria-label",
      open ? "Close customer support" : "Open customer support",
    );
    toggle.replaceChildren(icon(open ? "x" : "message-circle", open ? 20 : 21));
    if (open) {
      scrollToLatestMessage();
      field(panel, "chat-input").focus();
    }
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
    showError: (message) => addMessage(message, "assistant"),
    showTypingIndicator() {
      typing = addMessage("AUDI is typing…", "assistant");
      typing.setAttribute("role", "status");
    },
    hideTypingIndicator() {
      typing?.remove();
      typing = null;
    },
    setChatLoading,
  };
}
