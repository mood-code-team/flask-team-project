/** Mood Code 공통 JS */
/** 검색 패널 열기/닫기, 사이드 메뉴, 뉴스레터, 1:1 상담 버튼 */

function bootMain() {
  document.querySelectorAll(".flash").forEach((el) => {
    setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateX(100%)";
      setTimeout(() => el.remove(), 300);
    }, 4000);
  });

  initSearchPanel();
  initSideMenu();
  initFooterNewsletter();
  initFloatingActions();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bootMain);
} else {
  bootMain();
}

/** 푸터 뉴스레터 — UI만 (백엔드 연동 전) */
function initFooterNewsletter() {
  const form = document.getElementById("footer-newsletter-form");
  if (!form) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const email = form.querySelector('input[type="email"]');
    if (!email?.value.trim()) {
      email?.focus();
      return;
    }
    alert("구독 신청이 접수되었습니다. (데모)");
    form.reset();
  });
}

/** 검색 패널 */
function initSearchPanel() {
  const toggle = document.getElementById("search-toggle");
  const panel = document.getElementById("search-panel");
  const overlay = document.getElementById("search-panel-overlay");
  const closeBtn = document.getElementById("search-panel-close");
  const input = document.getElementById("search-input");
  const chips = document.querySelectorAll(".search-chip");

  if (!toggle || !panel || !overlay || !input) return;

  function openSearch() {
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    toggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("search-panel-open");
    setTimeout(() => input.focus(), 350);
  }

  function closeSearch() {
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    overlay.classList.remove("is-visible");
    toggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("search-panel-open");
    setTimeout(() => { overlay.hidden = true; }, 300);
  }

  toggle.addEventListener("click", () => {
    if (panel.classList.contains("is-open")) {
      closeSearch();
    } else {
      openSearch();
    }
  });

  closeBtn?.addEventListener("click", closeSearch);
  overlay.addEventListener("click", closeSearch);

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const keyword = chip.dataset.keyword || "";
      input.value = keyword;
      if (keyword && input.form) {
        input.form.submit();
      } else {
        input.focus();
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && panel.classList.contains("is-open")) {
      closeSearch();
    }
  });
}

/** 사이드 메뉴 (햄버거) */
function initSideMenu() {
  const menuToggle = document.querySelector(".menu-toggle");
  const menuClose = document.getElementById("side-menu-close");
  const sideMenu = document.getElementById("side-menu");
  const overlay = document.getElementById("side-menu-overlay");

  if (!menuToggle || !sideMenu || !overlay) return;

  function openMenu() {
    sideMenu.classList.add("is-open");
    sideMenu.setAttribute("aria-hidden", "false");
    overlay.hidden = false;
    requestAnimationFrame(() => overlay.classList.add("is-visible"));
    menuToggle.setAttribute("aria-expanded", "true");
    document.body.classList.add("side-menu-open");
  }

  function closeMenu() {
    sideMenu.classList.remove("is-open");
    sideMenu.setAttribute("aria-hidden", "true");
    overlay.classList.remove("is-visible");
    menuToggle.setAttribute("aria-expanded", "false");
    document.body.classList.remove("side-menu-open");
    resetSideMenuProductList(sideMenu);
    setTimeout(() => { overlay.hidden = true; }, 300);
  }

  menuToggle.addEventListener("click", openMenu);
  menuClose?.addEventListener("click", closeMenu);
  overlay.addEventListener("click", closeMenu);

  initSideMenuAccordion(sideMenu);
  initSideMenuProductList(sideMenu);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && sideMenu.classList.contains("is-open")) {
      closeMenu();
    }
  });
}

/** 상품목록 클릭 시 Lighting·Sofa 등 카테고리 버튼 펼침 */
function resetSideMenuProductList(sideMenu) {
  const toggle = sideMenu?.querySelector("#side-menu-products-toggle");
  const panel = sideMenu?.querySelector("#side-menu-products");
  const group = sideMenu?.querySelector(".side-menu__group--products");
  if (!toggle || !panel) return;

  panel.setAttribute("hidden", "");
  toggle.setAttribute("aria-expanded", "false");
  group?.classList.remove("is-open");

  sideMenu.querySelectorAll(".side-menu__category").forEach((category) => {
    category.classList.remove("is-open");
    category.querySelector(".side-menu__category-btn")?.setAttribute("aria-expanded", "false");
    category.querySelector(".side-menu__sublist")?.setAttribute("hidden", "");
  });
}

function initSideMenuProductList(sideMenu) {
  const toggle = sideMenu?.querySelector("#side-menu-products-toggle");
  const panel = sideMenu?.querySelector("#side-menu-products");
  const group = sideMenu?.querySelector(".side-menu__group--products");
  if (!toggle || !panel) return;

  toggle.addEventListener("click", () => {
    const willOpen = panel.hasAttribute("hidden");

    if (willOpen) {
      panel.removeAttribute("hidden");
      toggle.setAttribute("aria-expanded", "true");
      group?.classList.add("is-open");
    } else {
      resetSideMenuProductList(sideMenu);
    }
  });
}

/** 사이드 메뉴 카테고리 아코디언 */
function initSideMenuAccordion(sideMenu) {
  const categories = sideMenu?.querySelectorAll(".side-menu__category");
  if (!categories?.length) return;

  categories.forEach((category) => {
    const btn = category.querySelector(".side-menu__category-btn");
    const sublist = category.querySelector(".side-menu__sublist");
    if (!btn || !sublist) return;

    btn.addEventListener("click", () => {
      const willOpen = !category.classList.contains("is-open");

      categories.forEach((other) => {
        other.classList.remove("is-open");
        const otherBtn = other.querySelector(".side-menu__category-btn");
        const otherList = other.querySelector(".side-menu__sublist");
        otherBtn?.setAttribute("aria-expanded", "false");
        otherList?.setAttribute("hidden", "");
      });

      if (willOpen) {
        category.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
        sublist.removeAttribute("hidden");
      }
    });
  });
}

/** 플로팅 버튼 — 고객센터 (TOP 스크롤은 scroll-top.js) */
function initFloatingActions() {
  const chatBtn = document.getElementById("chat-launcher-btn");

  chatBtn?.addEventListener("click", () => {
    const centerUrl = chatBtn.dataset.chatUrl;
    if (centerUrl) {
      window.location.href = centerUrl;
    }
  });
}
