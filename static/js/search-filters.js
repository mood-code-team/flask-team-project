/** 검색·카테고리 필터 UI */
(function () {
  const form = document.getElementById("search-filter-form");
  if (!form) return;

  const filters = form.querySelectorAll(".search-filter");

  function closeAll(except) {
    filters.forEach((filter) => {
      if (filter === except) return;
      filter.classList.remove("is-open");
      const trigger = filter.querySelector(".search-filter__trigger");
      const panel = filter.querySelector(".search-filter__panel");
      trigger?.setAttribute("aria-expanded", "false");
      panel?.setAttribute("hidden", "");
    });
  }

  function setFilterValue(key, value) {
    const input = document.getElementById(`filter-${key}`);
    if (input) {
      input.value = value;
    }
  }

  function submitForm() {
    form.submit();
  }

  filters.forEach((filter) => {
    const trigger = filter.querySelector(".search-filter__trigger");
    const panel = filter.querySelector(".search-filter__panel");
    if (!trigger || !panel) return;

    trigger.addEventListener("click", (e) => {
      e.stopPropagation();
      const willOpen = !filter.classList.contains("is-open");
      closeAll(willOpen ? filter : null);

      if (willOpen) {
        filter.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
        panel.removeAttribute("hidden");
      } else {
        filter.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        panel.setAttribute("hidden", "");
      }
    });

    panel.querySelectorAll(".search-filter__option").forEach((option) => {
      option.addEventListener("click", () => {
        setFilterValue(option.dataset.filterKey, option.dataset.filterValue ?? "");
        submitForm();
      });
    });
  });

  form.querySelectorAll(".search-filter-tag__remove").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const key = btn.dataset.filterKey;
      if (!key) return;
      setFilterValue(key, key === "sort" ? "newest" : "");
      submitForm();
    });
  });

  document.getElementById("search-filter-reset")?.addEventListener("click", () => {
    setFilterValue("sort", "newest");
    ["space", "style", "color", "subcategory"].forEach((key) => {
      setFilterValue(key, "");
    });
    submitForm();
  });

  document.addEventListener("click", () => closeAll());
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAll();
  });
})();
