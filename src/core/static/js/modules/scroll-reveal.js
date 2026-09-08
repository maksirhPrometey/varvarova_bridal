const REVEAL_SEL = ".reveal:not(.is-visible):not([data-reveal-hold])";
const HOLD_SEL = ".reveal[data-reveal-hold]:not(.is-visible)";

function prefersReduced() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function show(el) {
  el.classList.add("is-visible");
}

function observePlain(root) {
  const nodes = root.querySelectorAll(REVEAL_SEL);
  if (!nodes.length) return;

  if (prefersReduced()) {
    nodes.forEach(show);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        show(entry.target);
        observer.unobserve(entry.target);
      }
    },
    { threshold: 0.15 },
  );

  nodes.forEach((el) => observer.observe(el));
}

function observeHold(root) {
  const nodes = root.querySelectorAll(HOLD_SEL);
  if (!nodes.length) return;

  if (prefersReduced()) {
    nodes.forEach(show);
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const target = entry.target;
        window.setTimeout(() => show(target), 200);
        observer.unobserve(target);
      }
    },
    { threshold: 0.15, rootMargin: "0px 0px -22% 0px" },
  );

  nodes.forEach((el) => observer.observe(el));
}

export function initReveal(root = document) {
  if (!root || !root.querySelectorAll) return;
  observePlain(root);
  observeHold(root);
}

initReveal(document);

document.body.addEventListener("htmx:afterSwap", (event) => {
  initReveal(event.detail && event.detail.target ? event.detail.target : document);
});
