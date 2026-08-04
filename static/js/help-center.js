/**
 * 고객센터 — 카테고리 필터·검색
 */
(function () {
  "use strict";

  const root = document.getElementById("help-center");
  if (!root) return;

  const searchInput = document.getElementById("help-search");
  const chips = root.querySelectorAll(".help-chip");
  const groups = root.querySelectorAll(".help-group");
  const items = root.querySelectorAll(".help-item");
  const metaLabel = document.getElementById("help-meta-label");
  const metaCount = document.getElementById("help-meta-count");
  const noResult = document.getElementById("help-no-result");

  let activeCategory = root.querySelector(".help-chip.is-active")?.dataset.category || "all";

  function countVisible() {
    let count = 0;
    items.forEach((item) => {
      if (!item.classList.contains("is-hidden")) count += 1;
    });
    return count;
  }

  function updateMeta() {
    const chip = root.querySelector(`.help-chip[data-category="${activeCategory}"]`);
    if (metaLabel && chip) metaLabel.textContent = chip.textContent.trim();
    if (metaCount) metaCount.textContent = String(countVisible());
    if (noResult) noResult.hidden = countVisible() > 0;
  }

  function applyFilters() {
    const query = (searchInput?.value || "").trim().toLowerCase();

    groups.forEach((group) => {
      const cat = group.dataset.category;
      const catMatch = activeCategory === "all" || cat === activeCategory;
      let groupVisible = false;

      group.querySelectorAll(".help-item").forEach((item) => {
        const text = item.dataset.question || "";
        const searchMatch = !query || text.includes(query);
        const visible = catMatch && searchMatch;
        item.classList.toggle("is-hidden", !visible);
        if (visible) groupVisible = true;
      });

      group.classList.toggle("is-hidden", !groupVisible);
    });

    updateMeta();
  }

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      activeCategory = chip.dataset.category || "all";
      chips.forEach((c) => {
        const active = c === chip;
        c.classList.toggle("is-active", active);
        c.setAttribute("aria-selected", active ? "true" : "false");
      });
      applyFilters();
    });
  });

  searchInput?.addEventListener("input", applyFilters);

  applyFilters();
})();
