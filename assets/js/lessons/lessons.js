// Server-backed lesson completion; learning content stays readable if requests fail.
import { api, notice } from "../shared/shared.js";

export function mountLessons(page) {
  let alive = true;
  const buttons = [...page.querySelectorAll('[data-action="complete-lesson"]')];
  function render(button, completed) {
    button.setAttribute("aria-pressed", String(completed));
    button.textContent = completed ? "Completed · mark unfinished" : "Mark lesson complete";
  }
  if (buttons.length) api("/lessons/progress").then((data) => {
    if (!alive) return;
    buttons.forEach((button) => { render(button, data.completed.includes(button.dataset.lessonSlug)); button.disabled = false; });
  }).catch((error) => {
    if (!alive) return;
    buttons.forEach((button) => { button.textContent = "Progress unavailable · reload to retry"; });
    notice(`Progress unavailable: ${error.message}`);
  });
  page.addEventListener("click", async (event) => {
    const button = event.target.closest('[data-action="complete-lesson"]');
    if (!button || button.disabled) return;
    button.disabled = true;
    try {
      const data = await api(`/lessons/progress/${button.dataset.lessonSlug}`, {
        method: "PUT", body: { completed: button.getAttribute("aria-pressed") !== "true" },
      });
      if (alive) { render(button, data.completed); notice(data.completed ? "Lesson completed. Your progress is saved." : "Lesson marked unfinished."); }
    } catch (error) { if (alive) notice(error.message); }
    finally { button.disabled = false; }
  });
  return { destroy() { alive = false; } };
}
