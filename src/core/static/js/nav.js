(function () {
  const header = document.querySelector("[data-site-header]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const drawer = document.querySelector("[data-site-drawer]");
  const backdrop = document.querySelector("[data-nav-backdrop]");
  const closeBtn = document.querySelector("[data-nav-close]");
  if (!header || !toggle || !drawer) return;

  let scrollY = 0;

  const setOpen = (open) => {
    header.classList.toggle("is-open", open);
    document.body.classList.toggle("is-nav-open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (backdrop) {
      backdrop.hidden = !open;
    }
    if (open) {
      scrollY = window.scrollY;
      document.body.style.top = `-${scrollY}px`;
    } else {
      document.body.style.top = "";
      window.scrollTo(0, scrollY);
    }
  };

  toggle.addEventListener("click", () => {
    setOpen(!document.body.classList.contains("is-nav-open"));
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", () => setOpen(false));
  }

  if (backdrop) {
    backdrop.addEventListener("click", () => setOpen(false));
  }

  drawer.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setOpen(false));
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setOpen(false);
  });

  window.addEventListener("resize", () => {
    if (window.matchMedia("(min-width: 992px)").matches) {
      setOpen(false);
    }
  });
})();
