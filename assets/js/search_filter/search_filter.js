// Search, type filters, sorting, and the existing budget/skill Guitar Finder.
import { imageSource, api, notice, $, field, text, clone, icon, peso, animate, dismiss } from "../shared/shared.js";

const questions = [
  { key: "budget", title: "What is your budget?" },
  {
    key: "level",
    title: "What is your experience level?",
    options: ["Beginner", "Intermediate", "Advanced"],
  },
  {
    key: "genre",
    title: "What do you want to play?",
    options: ["Rock", "Pop", "Blues", "Jazz", "Classical"],
  },
  {
    key: "category",
    title: "Which guitar type do you prefer?",
    options: ["Electric", "Acoustic", "Classical", "Bass"],
  },
];
const selectedOption =
  "rounded-2xl border p-5 text-left text-sm transition border-zinc-950 bg-zinc-950 text-white dark:border-acid dark:bg-acid/10 dark:text-acid";
const plainOption =
  "rounded-2xl border p-5 text-left text-sm transition border-zinc-200 hover:border-zinc-400 dark:border-white/10";

export function mountSearchFilter(page, app, { renderProducts, closeMobile, addToCart }) {
  let filter = app.catalogCategory || "All";
  app.catalogCategory = "";
  let search = app.searchProduct || "";
  app.searchProduct = "";
  field(page, "search").value = search;
  let sort = "Featured";
  let finder;
  let finderStep = 0;
  let results = [];
  let answers = {
    budget: 20000,
    level: "Beginner",
    genre: "Rock",
    category: "Electric",
  };
  const timers = new Set();
  let alive = true;

  function filterProducts(products) {
    let list = products.filter(
      (p) =>
        (filter === "All" || p.category === filter) &&
        `${p.name} ${p.brand}`.toLowerCase().includes(search.toLowerCase()),
    );
    if (sort === "Price: low")
      list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "Price: high")
      list = [...list].sort((a, b) => b.price - a.price);
    if (sort === "Rating") list = [...list].sort((a, b) => b.rating - a.rating);
    return list;
  }

  function renderFinder() {
    if (!finder) return;
    const modal = $(finder, ".finder-modal");
    modal.children[1]?.remove();
    if (finderStep === 4) {
      const body = clone("finder-results");
      field(body, "matches").replaceChildren(
        ...results.map((product, index) => {
          const row = clone("finder-match");
          row.dataset.productId = product.id;
          field(row, "image").src = imageSource(product.image);
          text(row, "rank", index + 1);
          text(row, "name", product.name);
          text(row, "category", `${product.category} · ${product.level}`);
          text(row, "price", peso(product.price));
          return row;
        }),
      );
      modal.append(body);
    } else {
      const body = field(clone("finder"), "finder-body");
      const question = questions[finderStep];
      text(body, "question-number", `Question ${finderStep + 1} of 4`);
      text(body, "question-title", question.title);
      [...field(body, "progress").children].forEach((bar, i) => {
        bar.className = `h-1 flex-1 rounded-full ${i <= finderStep ? "bg-zinc-950 dark:bg-acid" : "bg-zinc-200 dark:bg-white/10"}`;
      });
      field(body, "budget").hidden = finderStep !== 0;
      text(body, "budget-value", peso(answers.budget));
      field(body, "budget-input").value = answers.budget;
      const options = field(body, "options");
      options.hidden = finderStep === 0;
      options.replaceChildren(
        ...(question.options || []).map((option) => {
          const button = clone("finder-option");
          button.dataset.option = option;
          button.textContent = option;
          const selected = answers[question.key] === option;
          button.className = selected ? selectedOption : plainOption;
          if (selected) button.append(clone("check"));
          return button;
        }),
      );
      $(body, '[data-action="finder-next"]').replaceChildren(
        finderStep === 3 ? "Show my matches " : "Continue ",
        icon("arrow-right", 16),
      );
      modal.append(body);
    }
  }
  function openFinder() {
    closeMobile();
    if (finder) return;
    finder = clone("finder");
    page.append(finder);
    renderFinder();
    animate(finder);
  }
  function closeFinder() {
    const closing = finder;
    finder = null;
    finderStep = 0;
    results = [];
    dismiss(closing);
  }
  async function finishFinder() {
    const button = $(finder, '[data-action="finder-next"]');
    if (button.disabled) return;
    button.disabled = true;
    try {
      const data = await api("/finder", { method: "POST", body: answers });
      results = data.recommendations;
      finderStep = 4;
      if (alive) renderFinder();
    } catch (error) {
      notice(error.message);
      button.disabled = false;
    }
  }

  function handleAction(button) {
    const id = Number(button.closest("[data-product-id]")?.dataset.productId);
    switch (button.dataset.action) {
      case "finder":
        openFinder();
        break;
      case "close-finder":
        closeFinder();
        break;
      case "finder-next":
        if (finderStep === 3) finishFinder();
        else {
          finderStep += 1;
          renderFinder();
        }
        break;
      case "finder-option":
        answers = {
          ...answers,
          [questions[finderStep].key]: button.dataset.option,
        };
        renderFinder();
        break;
      case "finder-restart":
        finderStep = 0;
        renderFinder();
        break;
      case "add-match":
        addToCart(results.find((p) => p.id === id));
        closeFinder();
        break;
      case "search":
        $(page, "#shop").scrollIntoView({ behavior: "smooth" });
        timers.add(setTimeout(() => field(page, "search")?.focus(), 450));
        break;
      case "category":
        filter = button.dataset.category;
        renderProducts();
        $(page, "#shop").scrollIntoView({ behavior: "smooth" });
        break;
      case "filter":
        filter = button.dataset.category;
        renderProducts();
        break;
      default:
        return false;
    }
    return true;
  }
  page.addEventListener("input", (event) => {
    switch (event.target.dataset.field) {
      case "search":
        search = event.target.value;
        renderProducts();
        break;

      case "budget-input":
        answers = { ...answers, budget: Number(event.target.value) };
        text(finder, "budget-value", peso(answers.budget));
        break;
    }
  });
  page.addEventListener("change", (event) => {
    if (event.target.dataset.field === "sort") {
      sort = event.target.value;
      renderProducts();
    }
  });
  return {
    filterProducts, handleAction, openFinder,
    get category() { return filter; },
    get hasSelection() { return Boolean(search || filter !== "All"); },
    restoreProfile(profile) { answers = profile; },
    destroy() { alive = false; timers.forEach(clearTimeout); },
  };
}
