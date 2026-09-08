(function () {
  const scroller = document.querySelector("[data-filter-scroll]");
  if (!scroller) return;

  const inner = scroller.querySelector(".vv-filterbar__inner");
  if (!inner) return;

  const update = () => {
    const max = inner.scrollWidth - inner.clientWidth;
    const notScrollable = max <= 2;
    scroller.setAttribute("data-not-scrollable", notScrollable ? "true" : "false");
    scroller.setAttribute("data-at-end", !notScrollable && inner.scrollLeft >= max - 2 ? "true" : "false");
  };

  inner.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);
  update();
})();
